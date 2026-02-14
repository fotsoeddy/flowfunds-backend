from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import BudgetLimit, PushSubscription
from core.api.serializers.extras_serializer import BudgetLimitSerializer, PushSubscriptionSerializer

class BudgetLimitViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetLimitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BudgetLimit.objects.filter(user=self.request.user)

class PushSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PushSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PushSubscription.objects.filter(user=self.request.user)
