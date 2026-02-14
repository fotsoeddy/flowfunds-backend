from pywebpush import webpush, WebPushException
from django.conf import settings
from core.models import PushSubscription, Transaction
from core.utils.ai_helper import categorize_transaction, generate_daily_insight
from decouple import config
import json
from datetime import datetime

class NotificationService:
    @staticmethod
    def send_push_notification(subscription, message_body, title="FlowFunds"):
        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth
                    }
                },
                data=json.dumps({
                    "title": title,
                    "body": message_body,
                }),
                vapid_private_key=config('VAPID_PRIVATE_KEY'),
                vapid_claims={
                    "sub": config('VAPID_MAILTO', default='mailto:admin@example.com')
                }
            )
            return True
        except WebPushException as ex:
            print(f"Web Push Failed: {ex}")
            # If 410 Gone, remove subscription
            if ex.response and ex.response.status_code == 410:
                subscription.delete()
            return False
        except Exception as e:
            print(f"Error sending push: {e}")
            return False

    @staticmethod
    def send_morning_reminders():
        subscriptions = PushSubscription.objects.all()
        message = "Good morning! ☀️ Don't forget to track your expenses today to stay on budget."
        
        count = 0
        for sub in subscriptions:
            if NotificationService.send_push_notification(sub, message, "Daily Reminder"):
                count += 1
        return count

    @staticmethod
    def send_evening_summary():
        subscriptions = PushSubscription.objects.all()
        
        count = 0
        today = datetime.now().date()
        
        for sub in subscriptions:
            user = sub.user
            # Get today's expenses
            expenses = Transaction.objects.filter(
                user=user, 
                type='expense', 
                date__date=today
            )
            total_spent = sum(t.amount for t in expenses)
            
            # Create breakdown
            breakdown = {}
            for t in expenses:
                cat = t.category or "Uncategorized"
                breakdown[cat] = breakdown.get(cat, 0) + t.amount
            
            message = generate_daily_insight(total_spent, breakdown)
                
            if NotificationService.send_push_notification(sub, message, "Daily Summary"):
                count += 1
        return count
