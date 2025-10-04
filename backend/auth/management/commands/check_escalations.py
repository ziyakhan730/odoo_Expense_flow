"""
Django management command to check for expense escalations
Run this command via cron job every hour
"""
from django.core.management.base import BaseCommand
from auth.workflow import check_escalations


class Command(BaseCommand):
    help = 'Check for expenses that need escalation'

    def handle(self, *args, **options):
        escalated_count = check_escalations()
        
        if escalated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully escalated {escalated_count} expenses')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No expenses needed escalation')
            )
