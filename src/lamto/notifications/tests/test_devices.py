import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase

from lamto.notifications.devices import (
    deactivate_device,
    deactivate_stale_devices,
    register_device,
)
from lamto.notifications.models import Device


class DeviceRegistryTests(TestCase):
    def setUp(self):
        self.user_a = get_user_model().objects.create_user(
            email="a@example.test", password="x", display_name="A"
        )
        self.user_b = get_user_model().objects.create_user(
            email="b@example.test", password="x", display_name="B"
        )

    def test_upsert_by_user_install(self):
        install = str(uuid.uuid4())
        d1 = register_device(self.user_a, install, "tok-1", Device.Platform.ANDROID)
        d2 = register_device(
            self.user_a, install, "tok-2", Device.Platform.ANDROID, app_version="1.1"
        )
        assert d1.pk == d2.pk  # same (user, install) row
        d2.refresh_from_db()
        assert d2.fcm_token == "tok-2" and d2.active is True and d2.app_version == "1.1"
        assert Device.objects.filter(user=self.user_a).count() == 1

    def test_token_reassignment_deactivates_old_binding(self):
        install_a = str(uuid.uuid4())
        install_b = str(uuid.uuid4())
        register_device(self.user_a, install_a, "shared-tok", Device.Platform.IOS)
        # Possession of the token proves control: it reattaches to user_b's install.
        register_device(self.user_b, install_b, "shared-tok", Device.Platform.IOS)
        old = Device.objects.get(user=self.user_a, install_id=install_a)
        new = Device.objects.get(user=self.user_b, install_id=install_b)
        assert old.active is False
        assert new.active is True and new.fcm_token == "shared-tok"
        assert Device.objects.filter(fcm_token="shared-tok", active=True).count() == 1

    def test_deactivate_device_and_stale_cleanup(self):
        from datetime import timedelta

        from django.utils import timezone

        install = str(uuid.uuid4())
        register_device(self.user_a, install, "tok-x", Device.Platform.ANDROID)
        assert deactivate_device(self.user_a, install) == 1
        assert Device.objects.get(user=self.user_a, install_id=install).active is False

        install2 = str(uuid.uuid4())
        d = register_device(self.user_a, install2, "tok-y", Device.Platform.ANDROID)
        Device.objects.filter(pk=d.pk).update(
            last_seen_at=timezone.now() - timedelta(days=200)
        )
        assert deactivate_stale_devices(days=180) == 1
        assert Device.objects.get(pk=d.pk).active is False


class DeviceRegistryRaceTests(TransactionTestCase):
    """Concurrent registration needs committed rows visible across threads.

    Django TestCase wraps each test in a transaction that worker threads cannot
    see, so this race is exercised under TransactionTestCase.
    """

    def _fixture_teardown(self):
        # Append-only document/audit triggers reject Django's TRUNCATE flush.
        # Match evidence ConcurrentOutboxTests: skip flush; test DB is dropped
        # by the runner.
        pass

    def setUp(self):
        self.user_a = get_user_model().objects.create_user(
            email="race-a@example.test", password="x", display_name="A"
        )
        self.user_b = get_user_model().objects.create_user(
            email="race-b@example.test", password="x", display_name="B"
        )

    def test_concurrent_token_reassignment_leaves_one_active(self):
        """Race around active-token partial unique: only one active holder remains."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        from django.db import connection

        install_a = str(uuid.uuid4())
        install_b = str(uuid.uuid4())
        token = f"race-tok-{uuid.uuid4()}"

        def _register(user, install):
            # Fresh connection per thread (Django TestCase).
            connection.close()
            try:
                return register_device(user, install, token, Device.Platform.ANDROID)
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(_register, self.user_a, install_a),
                pool.submit(_register, self.user_b, install_b),
            ]
            for f in as_completed(futures):
                f.result()  # must not raise IntegrityError to the caller

        active = list(Device.objects.filter(fcm_token=token, active=True))
        assert len(active) == 1
