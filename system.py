from functools import partial

from django.utils.functional import SimpleLazyObject, cached_property

from django_temporary_permissions.config import env
from django_temporary_permissions.state import State
from django_temporary_permissions.utils.locking.backends.redis import RedisLockBackend
from django_temporary_permissions.utils.locking.manager import LockManager
from django_temporary_permissions.utils.redis import SmartRedis


class Logger:
    def __init__(self, system):
        from django_temporary_permissions.models import SysLogEntry
        self.info = partial(SysLogEntry.info, system.organization)


class System:
    def __init__(self):
        pass

    @cached_property
    def logger(self):
        return Logger(self)


core = SimpleLazyObject(System)
locks = LockManager(RedisLockBackend(SmartRedis.from_url(env('REDIS_LOCK_URL'))))
# stop = sys.stop
# stopped = sys.stopped
# running = sys.running
# restart = sys.restart
state = State()
