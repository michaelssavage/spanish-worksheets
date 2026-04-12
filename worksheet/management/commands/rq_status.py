"""Inspect RQ default queue (depth, started, failed) for production debugging."""

from django.core.management.base import BaseCommand
from django_rq import get_queue


class Command(BaseCommand):
    help = "Print RQ queue depth and registry counts for the default queue."

    def handle(self, *args, **options):
        q = get_queue("default")
        self.stdout.write(f"default queue length (waiting): {len(q)}")

        for name in (
            "started_job_registry",
            "deferred_job_registry",
            "scheduled_job_registry",
        ):
            reg = getattr(q, name, None)
            if reg is not None:
                self.stdout.write(f"{name}: {reg.count}")

        failed = getattr(q, "failed_job_registry", None)
        if failed is not None:
            self.stdout.write(f"failed_job_registry: {failed.count}")
            try:
                ids = failed.get_job_ids()
            except AttributeError:
                ids = []
            if ids:
                self.stdout.write("recent failed job ids (up to 10):")
                for jid in ids[:10]:
                    self.stdout.write(f"  {jid}")
