import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from lamto.accounts.models import Building
from lamto.gate.calibration import score_pairs, sweep
from lamto.gate.embedding import get_embedder

class Command(BaseCommand):
    help = "Score labelled reader captures and print a threshold sweep."
    def add_arguments(self, parser):
        parser.add_argument("manifest", help="JSON array of {occupancy_id, path} labelled captures")
        parser.add_argument("--building", type=int, required=True)
        parser.add_argument("--model-name", required=True)
        parser.add_argument("--model-version", required=True)

    def handle(self, *args, **options):
        captures = json.loads(Path(options["manifest"]).read_text())
        if not captures:
            raise CommandError("The labelled capture manifest is empty.")
        embedder = get_embedder()
        probes = []
        for capture in captures:
            result = embedder.embed(Path(capture["path"]).read_bytes())
            if (result.model_name, result.model_version) != (options["model_name"], options["model_version"]):
                raise CommandError("Capture model name/version does not match the requested calibration scope.")
            probes.append((int(capture["occupancy_id"]), result.vector))
        try:
            scores = score_pairs(Building.objects.get(pk=options["building"]), probes, model_name=options["model_name"], model_version=options["model_version"])
        except ValueError as error:
            raise CommandError(str(error)) from error
        if not scores.genuine or not scores.impostor:
            raise CommandError("Labelled captures must produce both genuine and impostor scores.")
        for row in sweep(scores, .30, .60, .01):
            self.stdout.write(f"| {row.threshold:.2f} | {row.fmr:.4f} | {row.fnmr:.4f} |")
