from django.core.management.base import BaseCommand, CommandError

from lamto.gate.models import PhotoDeletion
from lamto.gate.photos import process_photo_deletions
from lamto.gate.retention import purge_expired_enrollment_photos, purge_expired_gate_events, record_purge_success


class Command(BaseCommand):
    help = "Purge expired gate events and enrollment photos."

    def handle(self, *args, **options):
        try:
            events = purge_expired_gate_events()
            photos = purge_expired_enrollment_photos()
            process_photo_deletions()
            if PhotoDeletion.objects.exists():
                raise RuntimeError("enrollment photo deletions remain queued")
            record_purge_success(events=events, photos=photos)
        except Exception as error:
            raise CommandError(f"gate retention purge failed: {error}") from error
        self.stdout.write(f"gate_events_deleted={events} enrollment_photos_deleted={photos}")
