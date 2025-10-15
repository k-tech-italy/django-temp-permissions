"""Signals for django_temporary_permissions."""

import django.dispatch

permission_overlap_detected = django.dispatch.Signal()
