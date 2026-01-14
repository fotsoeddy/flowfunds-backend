from rest_framework import serializers
from core.api.serializers.transaction_serializer import TransactionSerializer

class DashboardSummarySerializer(serializers.Serializer):
    total_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    account_count = serializers.IntegerField()
    recent_transactions = TransactionSerializer(many=True)
