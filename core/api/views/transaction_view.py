from rest_framework import generics, permissions
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.models import Transaction, Account
from core.api.serializers.transaction_serializer import TransactionSerializer
from core.api.serializers.dashboard_serializer import DashboardSummarySerializer

@extend_schema(
    summary="List or Create Transactions",
    description="Create a new transaction (updates account balance) or list history.",
    examples=[
        OpenApiExample(
            'Create Expense Example',
            value={
                'type': 'expense',
                'amount': 2500,
                'category': 'Food',
                'reason': 'Lunch',
                'date': '2026-01-14T12:00:00Z',
                'account_id': '3fa85f64-5717-4562-b3fc-2c963f66afa6'
            },
            request_only=True
        )
    ]
)
class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

@extend_schema(
    summary="Dashboard Summary",
    description="Get aggregated stats including total balance and recent activity.",
    responses={200: DashboardSummarySerializer}
)
class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        accounts = Account.objects.filter(user=user, status=1)
        total_balance = sum(acc.balance for acc in accounts)
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]
        recent_serializer = TransactionSerializer(recent_transactions, many=True)
        
        return Response({
            "total_balance": total_balance,
            "account_count": accounts.count(),
            "recent_transactions": recent_serializer.data
        })
