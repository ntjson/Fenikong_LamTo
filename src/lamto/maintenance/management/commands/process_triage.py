from django.core.management.base import BaseCommand

from lamto.maintenance.ai import _claim_triage_job, _process_claimed_job


class Command(BaseCommand):
    help = "Process pending AI triage jobs."

    def handle(self, *args, **options):
        while job := _claim_triage_job():
            _process_claimed_job(job)
