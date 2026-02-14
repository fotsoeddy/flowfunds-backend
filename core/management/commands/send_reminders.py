from django.core.management.base import BaseCommand
from core.services.notification_service import NotificationService

class Command(BaseCommand):
    help = 'Sends push notification reminders to users'

    def add_arguments(self, parser):
        parser.add_argument('--type', type=str, help='Type of reminder: morning or evening')

    def handle(self, *args, **options):
        reminder_type = options.get('type')
        
        if reminder_type == 'morning':
            count = NotificationService.send_morning_reminders()
            self.stdout.write(self.style.SUCCESS(f'Successfully sent {count} morning reminders'))
        elif reminder_type == 'evening':
            count = NotificationService.send_evening_summary()
            self.stdout.write(self.style.SUCCESS(f'Successfully sent {count} evening summaries'))
        elif reminder_type == 'test':
            count = NotificationService.send_evening_summary() # Use evening summary for test
            self.stdout.write(self.style.SUCCESS(f'Successfully sent {count} test notifications'))
        else:
            self.stdout.write(self.style.ERROR('Please specify --type morning or --type evening'))
