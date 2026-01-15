import logging
from rest_framework import generics, permissions
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.models import Transaction, Account
from core.api.serializers.transaction_serializer import TransactionSerializer
from core.api.serializers.dashboard_serializer import DashboardSummarySerializer

logger = logging.getLogger(__name__)

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
        logger.debug(f"[TRANSACTION_LIST] Fetching transactions for user: {self.request.user}")
        try:
            queryset = Transaction.objects.filter(user=self.request.user).order_by('-date')
            logger.info(f"[TRANSACTION_LIST] Found {queryset.count()} transactions for user: {self.request.user}")
            return queryset
        except Exception as e:
            logger.error(f"[TRANSACTION_LIST] Error fetching transactions: {str(e)}", exc_info=True)
            logger.error(f"[TRANSACTION_LIST] User: {self.request.user}")
            raise
    
    def list(self, request, *args, **kwargs):
        logger.info(f"[TRANSACTION_LIST] Transaction list request from user: {request.user}")
        
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.debug(f"[TRANSACTION_LIST] Returning {len(serializer.data)} transactions")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"[TRANSACTION_LIST] Failed to list transactions: {str(e)}", exc_info=True)
            logger.error(f"[TRANSACTION_LIST] User: {request.user}")
            raise
    
    def create(self, request, *args, **kwargs):
        logger.info(f"[TRANSACTION_CREATE] Transaction creation attempt by user: {request.user}")
        logger.debug(f"[TRANSACTION_CREATE] Request data: {request.data}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"[TRANSACTION_CREATE] Validation failed: {serializer.errors}")
                logger.debug(f"[TRANSACTION_CREATE] Invalid data: {request.data}")
                return Response(serializer.errors, status=400)
            
            logger.info(f"[TRANSACTION_CREATE] Validation successful, creating transaction")
            logger.debug(f"[TRANSACTION_CREATE] Transaction type: {request.data.get('type')}, Amount: {request.data.get('amount')}")
            
            # Log account balance before transaction
            account_id = request.data.get('account_id')
            if account_id:
                try:
                    account = Account.objects.get(id=account_id, user=request.user)
                    logger.debug(f"[TRANSACTION_CREATE] Account balance before: {account.balance}")
                except Account.DoesNotExist:
                    logger.error(f"[TRANSACTION_CREATE] Account not found: {account_id}")
            
            self.perform_create(serializer)
            
            # Log account balance after transaction
            if account_id:
                try:
                    account.refresh_from_db()
                    logger.debug(f"[TRANSACTION_CREATE] Account balance after: {account.balance}")
                except Exception as e:
                    logger.warning(f"[TRANSACTION_CREATE] Could not refresh account balance: {str(e)}")
            
            headers = self.get_success_headers(serializer.data)
            logger.info(f"[TRANSACTION_CREATE] Transaction created successfully: {serializer.data.get('type')} - {serializer.data.get('amount')}")
            logger.debug(f"[TRANSACTION_CREATE] Created transaction data: {serializer.data}")
            
            return Response(serializer.data, status=201, headers=headers)
            
        except Exception as e:
            logger.error(f"[TRANSACTION_CREATE] Transaction creation failed: {str(e)}", exc_info=True)
            logger.error(f"[TRANSACTION_CREATE] User: {request.user}, Data: {request.data}")
            return Response(
                {"error": "Transaction creation failed", "detail": str(e)},
                status=500
            )

@extend_schema(
    summary="Dashboard Summary",
    description="Get aggregated stats including total balance and recent activity.",
    responses={200: DashboardSummarySerializer}
)
class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logger.info(f"[DASHBOARD] Dashboard summary request from user: {request.user}")
        
        try:
            user = request.user
            logger.debug(f"[DASHBOARD] Fetching accounts for user: {user}")
            
            accounts = Account.objects.filter(user=user, status=1)
            account_count = accounts.count()
            logger.info(f"[DASHBOARD] Found {account_count} active accounts")
            
            logger.debug(f"[DASHBOARD] Calculating total balance")
            total_balance = sum(acc.balance for acc in accounts)
            logger.info(f"[DASHBOARD] Total balance calculated: {total_balance}")
            
            # Recent transactions
            logger.debug(f"[DASHBOARD] Fetching recent transactions")
            recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]
            logger.info(f"[DASHBOARD] Found {recent_transactions.count()} recent transactions")
            
            recent_serializer = TransactionSerializer(recent_transactions, many=True)
            
            response_data = {
                "total_balance": total_balance,
                "account_count": account_count,
                "recent_transactions": recent_serializer.data
            }
            
            logger.debug(f"[DASHBOARD] Response data prepared: {response_data}")
            logger.info(f"[DASHBOARD] Dashboard summary completed successfully for user: {user}")
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"[DASHBOARD] Dashboard summary failed: {str(e)}", exc_info=True)
            logger.error(f"[DASHBOARD] User: {request.user}")
            return Response(
                {"error": "Failed to fetch dashboard summary", "detail": str(e)},
                status=500
            )
