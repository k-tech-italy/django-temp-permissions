"""django_temporary_permissions model validators."""

from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_date_not_in_past(value: datetime) -> None:
    """Validate that a date is not in the past."""
    if value <= timezone.now():
        raise ValidationError(f"{value} date is in the past.")
