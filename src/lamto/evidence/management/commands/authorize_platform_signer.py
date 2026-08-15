from django.core.management.base import BaseCommand

from lamto.evidence.chain import default_client
from lamto.evidence.signatures import platform_signer_address


class Command(BaseCommand):
    help = "Authorize the platform signer address on the EvidenceRegistry (owner key)."

    def handle(self, *args, **options):
        address = platform_signer_address()
        tx = default_client().set_signer(address, True)
        self.stdout.write(self.style.SUCCESS(f"Authorized {address} (tx {tx})"))
