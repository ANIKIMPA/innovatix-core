import csv
import json

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = "Convert a CSV file to a Django JSON data fixture"

    def add_arguments(self, parser):
        parser.add_argument("csv_file_path", type=str, help="The path to the CSV file")
        parser.add_argument(
            "json_file_path", type=str, help="The path to the JSON file"
        )
        parser.add_argument(
            "model", type=str, help="The Django model in the form app.model"
        )

    def handle(self, *args, **options):
        csv_file_path = options["csv_file_path"]
        json_file_path = options["json_file_path"]
        model = options["model"]

        # Start conversion process
        self.stdout.write(f"Starting conversion of {csv_file_path} to {json_file_path}")

        data = []
        try:
            with open(csv_file_path) as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for pk, row in enumerate(csv_reader, start=1):
                    fields = {key.lower(): value for key, value in row.items()}
                    now = timezone.now()
                    fields["created_at"] = now.isoformat()
                    data.append(
                        {
                            "pk": pk,
                            "model": model,
                            "fields": fields,
                        }
                    )
        except FileNotFoundError:
            raise CommandError(f"Could not open file at {csv_file_path}")

        try:
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
        except Exception as e:
            raise CommandError(f"Could not write to file at {json_file_path}: {e}")

        # Conversion process completed successfully
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully converted {csv_file_path} to {json_file_path}"
            )
        )
