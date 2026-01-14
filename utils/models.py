import uuid
from django.db import models
from django_extensions.db.models import TimeStampedModel, ActivatorModel

class FlowFundsBaseModel(TimeStampedModel, ActivatorModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
