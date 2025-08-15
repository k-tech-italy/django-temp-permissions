from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from factory import SubFactory, Faker, Sequence, LazyFunction
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import timedelta

from django_temporary_permissions.models import UserTemporaryPermission

class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: f"test_user_{n}")

    class Meta:
        model = get_user_model()


class PermissionFactory(DjangoModelFactory):
    name = Faker("sentence", nb_words=3)

    codename = Sequence(lambda n: f"test_perm_{n}")
    content_type = LazyFunction(lambda: ContentType.objects.get(app_label="auth", model="user"))

    class Meta:
        model = Permission


class UserTemporaryPermissionFactory(DjangoModelFactory):

    user = SubFactory(UserFactory)
    permission = SubFactory(PermissionFactory)

    start_datetime = LazyFunction(timezone.now)
    end_datetime = LazyFunction(lambda: timezone.now() + timedelta(days=5))

    class Meta:
        model = UserTemporaryPermission
