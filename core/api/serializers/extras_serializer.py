from rest_framework import serializers
from core.models import BudgetLimit, PushSubscription

class BudgetLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetLimit
        fields = ['id', 'category', 'amount', 'period']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['id', 'endpoint', 'p256dh', 'auth']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Update existing subscription if endpoint matches, or create new
        subscription, created = PushSubscription.objects.update_or_create(
            user=self.context['request'].user,
            endpoint=validated_data['endpoint'],
            defaults=validated_data
        )
        return subscription
