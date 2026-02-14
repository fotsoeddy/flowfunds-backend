from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.views.auth_view import RegisterView, CustomTokenObtainPairView, UserDetailView
from core.api.views.account_view import AccountListCreateView, AccountDetailView
from core.api.views.transaction_view import TransactionListCreateView, DashboardSummaryView
from core.api.views.extras_view import BudgetLimitViewSet, PushSubscriptionViewSet
from core.api.views.ai_view import ai_chat
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'budget-limits', BudgetLimitViewSet, basename='budget-limit')
router.register(r'push-subscriptions', PushSubscriptionViewSet, basename='push-subscription')

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', UserDetailView.as_view(), name='user_detail'),

    # Accounts
    path('accounts/', AccountListCreateView.as_view(), name='account-list-create'),
    path('accounts/<uuid:pk>/', AccountDetailView.as_view(), name='account-detail'),

    # Transactions
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),

    # Dashboard
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    
    # AI Assistant
    path('ai/chat/', ai_chat, name='ai-chat'),

    # Extras (Budget & Push)
    path('', include(router.urls)),
]
