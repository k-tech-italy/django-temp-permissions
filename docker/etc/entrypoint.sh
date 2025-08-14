#!/bin/bash -e

#mkdir -p "/data/django_temporary_permissions/logs" "${STATIC_ROOT}" "${MEDIA_ROOT}"
#chown ktech -R /data/django_temporary_permissions "${STATIC_ROOT}" "${MEDIA_ROOT}"

echo "$*"

setup() {
  django-admin upgrade -vv \
          --static \
          --admin-username ${ADMIN_USERNAME:-admin} \
          --admin-email ${ADMIN_EMAIL} \
          --admin-password ${ADMIN_PASSWORD}
}
if [ "${STACK_PROTOCOL}" = "https" ]; then
      echo "setting up HTTPS"
      STACK_PORT="8443,/etc/certs/cbtcsudan.crt,/etc/certs/cbtcsudan.key"
else
      echo "setting up HTTP"
      STACK_PORT=8000
fi

if [ "$*" = "run" ]; then
  setup
  exec uwsgi --${STACK_PROTOCOL} 0.0.0.0:${STACK_PORT} \
    --static-map "/static=/data/static" \
    --static-map "/media=/data/media" \
    --master \
    --module django_temporary_permissions.config.wsgi \
    --processes 4 \
    --offload-threads 8
elif [ "$*" = "worker" ]; then
  setup
  celery -A django_temporary_permissions.config.celery worker --loglevel=INFO  -n wk_%h
elif [ "$*" = "stack" ]; then
  setup
  export STACK_PROTOCOL
  export STACK_PORT
  exec circusd /etc/circus.conf
elif [ "$*" = "dev" ]; then
  setup
  exec django-admin runserver 0.0.0.0:8000
elif [ "$*" = "flower" ]; then
  exec -A django_temporary_permissions.config.celery --broker=${CELERY_BROKER_URL} flower
elif [ "$*" = "beat" ]; then
  setup
  celery -A django_temporary_permissions.config.celery beat --loglevel=INFO
else
  exec "$@"
fi
