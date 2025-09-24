from datetime import timedelta

import pytest
from django.utils import timezone
from test_utils.factories import TemporaryPermissionFactory


@pytest.fixture
def expired_temporary_permission():
    base_time = timezone.now()

    return TemporaryPermissionFactory(
        start_datetime=base_time - timedelta(hours=5), end_datetime=base_time - timedelta(hours=1)
    )


@pytest.fixture
def future_temporary_permission():
    base_time = timezone.now()

    return TemporaryPermissionFactory(
        start_datetime=base_time + timedelta(days=1), end_datetime=base_time + timedelta(days=2)
    )
