from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from lamto.accounts.models import Building, ManagementMembership, User
from lamto.audit.models import AuditEvent
from lamto.audit.services import record_audit

CLEANUP_MIGRATION = ("accounts", "0019_purge_totp_secrets")

TOTP_SECRET = "a4227a03748ce7b4486b56f1fdce131c3981e3ff"

TOTP_DEVICE_TABLE_SQL = """
CREATE TABLE otp_totp_totpdevice (
    id serial NOT NULL PRIMARY KEY,
    name varchar(64) NOT NULL,
    confirmed boolean NOT NULL,
    key varchar(80) NOT NULL,
    step smallint NOT NULL,
    t0 bigint NOT NULL,
    digits smallint NOT NULL,
    tolerance smallint NOT NULL,
    drift smallint NOT NULL,
    last_t bigint NOT NULL,
    user_id integer NOT NULL,
    throttling_failure_count integer NOT NULL,
    throttling_failure_timestamp timestamptz NULL,
    created_at timestamptz NULL,
    last_used_at timestamptz NULL
)
"""


def _remove_cleanup_migration_record():
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM django_migrations WHERE app = %s AND name = %s",
            [CLEANUP_MIGRATION[0], CLEANUP_MIGRATION[1]],
        )


def _apply_cleanup_migration():
    executor = MigrationExecutor(connection)
    executor.migrate([CLEANUP_MIGRATION])


def _install_totp_schema(user_id):
    with connection.cursor() as cursor:
        cursor.execute(TOTP_DEVICE_TABLE_SQL)
        cursor.execute(
            "INSERT INTO django_content_type (app_label, model)"
            " VALUES ('otp_totp', 'totpdevice') RETURNING id"
        )
        content_type_id = cursor.fetchone()[0]
        for codename in (
            "add_totpdevice",
            "change_totpdevice",
            "delete_totpdevice",
            "view_totpdevice",
        ):
            cursor.execute(
                "INSERT INTO auth_permission (name, content_type_id, codename)"
                " VALUES (%s, %s, %s)",
                [f"Can {codename}", content_type_id, codename],
            )
        cursor.execute(
            "INSERT INTO otp_totp_totpdevice ("
            " name, confirmed, key, step, t0, digits, tolerance, drift, last_t,"
            " user_id, throttling_failure_count"
            ") VALUES ('default', TRUE, %s, 30, 0, 6, 1, 0, -1, %s, 0)",
            [TOTP_SECRET, user_id],
        )
        cursor.execute(
            "INSERT INTO otp_totp_totpdevice ("
            " name, confirmed, key, step, t0, digits, tolerance, drift, last_t,"
            " user_id, throttling_failure_count"
            ") VALUES ('pending', FALSE, %s, 30, 0, 6, 1, 0, -1, %s, 0)",
            [TOTP_SECRET, user_id],
        )


def _totp_table_exists():
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('otp_totp_totpdevice')")
        return cursor.fetchone()[0] is not None


def _assert_totp_schema_absent():
    assert not _totp_table_exists()
    assert not ContentType.objects.filter(
        app_label__in=["otp_totp", "django_otp"]
    ).exists()
    assert not Permission.objects.filter(
        content_type__app_label__in=["otp_totp", "django_otp"]
    ).exists()


def _make_management_actor():
    user = User.objects.create_user(
        email="board@example.test", password="secret", display_name="Board Member"
    )
    building = Building.objects.create(name="Minh An Residence")
    membership = ManagementMembership.objects.create(user=user, building=building)
    return user, membership


def test_cleanup_migration_purges_totp_schema_and_keeps_audit_evidence(db):
    user, membership = _make_management_actor()
    enroll_begin = record_audit(
        actor=user,
        membership=membership,
        action="security.mfa.enroll_begin",
        target_type="TOTPDevice",
        target_id="1",
        result="accepted",
    )
    enroll_confirm = record_audit(
        actor=user,
        membership=membership,
        action="security.mfa.enroll_confirm",
        target_type="TOTPDevice",
        target_id="1",
        result="accepted",
        metadata={"confirmed": True},
    )

    _install_totp_schema(user.pk)
    _remove_cleanup_migration_record()
    assert _totp_table_exists()

    _apply_cleanup_migration()

    _assert_totp_schema_absent()

    enroll_begin.refresh_from_db()
    enroll_confirm.refresh_from_db()
    assert AuditEvent.objects.count() == 2
    assert enroll_begin.action == "security.mfa.enroll_begin"
    assert enroll_begin.result == "accepted"
    assert enroll_confirm.action == "security.mfa.enroll_confirm"
    assert enroll_confirm.result == "accepted"
    assert enroll_confirm.metadata == {"confirmed": True}
    assert enroll_confirm.target_id == "1"


def test_cleanup_migration_is_safe_when_totp_schema_is_absent(db):
    _assert_totp_schema_absent()

    _remove_cleanup_migration_record()
    _apply_cleanup_migration()

    _assert_totp_schema_absent()
    assert AuditEvent.objects.count() == 0
