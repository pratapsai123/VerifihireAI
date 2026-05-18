"""
Reset consumed Secure Agent registrations (support / testing).

Usage:
  python manage.py reset_consumed_agents
  python manage.py reset_consumed_agents --instance-id <uuid>
"""
from django.core.management.base import BaseCommand
from api.models import SecureAgentInstance


class Command(BaseCommand):
    help = 'Clear consumed flags on Secure Agent instances so candidates can retry with a fresh download.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--instance-id',
            type=str,
            default='',
            help='Only reset a specific agent instance_id',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Reset every consumed agent (use with care)',
        )

    def handle(self, *args, **options):
        instance_id = (options.get('instance_id') or '').strip()
        reset_all = options.get('all')

        qs = SecureAgentInstance.objects.filter(consumed=True)
        if instance_id:
            qs = qs.filter(instance_id=instance_id)
        elif not reset_all:
            self.stderr.write(
                'Pass --instance-id <uuid> or --all to confirm.\n'
                'Example: python manage.py reset_consumed_agents --all'
            )
            return

        count = qs.update(consumed=False, consumed_at=None)
        self.stdout.write(self.style.SUCCESS(f'Reset {count} consumed agent instance(s).'))
