#!make

.PHONY: clean

ifndef DOCKER_REGISTRY
$(error DOCKER_REGISTRY is not set)
endif

# VARIABLES
VERSION=1.0.0
BASE?=$(shell echo "${VERSION}" | sed "s/\([0-9]*\)\.\([0-9]*\)\.\(.*\)/\1.\2/g" )
BUILDDIR?=./~build
CONTAINER_NAME=django_temporary_permissions
DOCKER_IMAGE=kt/django_temporary_permissions
DOCKER_IMAGE_NAME=${DOCKER_IMAGE}:${VERSION}
DOCKER_IMAGE_FULLNAME=${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${VERSION}
STACK_PROTOCOL?=https
MEDIA_ROOT?=../~media
STATIC_ROOT?=../~static

LOCAL_PORT?=18000
LOCAL_HTTPS_PORT?=18443

CMD?=run
BUILD_OPTIONS?=--squash

# HELP HELPER
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

requirements:  ## Builds the /dist/image-requirements.txt
	@cd .. && uv build --sdist
	@uv export --no-dev --no-emit-project --group image --format requirements-txt > ../dist/image-requirements.txt

build-base: requirements  ## Builds the base image
	cd .. && docker build \
			${BUILD_OPTIONS} \
			--build-arg REPO_NAME="${REPO_NAME}" \
			-t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}/base:${BASE} \
			-f docker/Dockerfile.base  .
	#docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}/base:${BASE}
	docker images | grep ${DOCKER_IMAGE}/base | grep ${BASE}

build: ## Builds the image
	cd .. && docker build \
		${BUILD_OPTIONS} \
		--build-arg BASE_IMAGE="${BASE}" \
		--build-arg DOCKER_REGISTRY="${DOCKER_REGISTRY}" \
		-t ${DOCKER_IMAGE_FULLNAME} \
		-f docker/Dockerfile .
	@docker images | grep ${DOCKER_IMAGE} | grep ${VERSION}

ecrlogin:  ## Log in to docker
	@if [ "${ECR_AWS_PROFILE}" != "" ]; then \
		aws ecr get-login-password --profile ${ECR_AWS_PROFILE} --region ${ECR_AWS_REGION} | docker login --username AWS --password-stdin ${DOCKER_REGISTRY} ; \
	else \
		@echo ${DOCKER_SECRET} | echo docker login ${DOCKER_REGISTRY} -u ${DOCKER_USERNAME} --password-stdin ; \
    fi

release: ecrlogin  ## Release the image
	# docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}/base:${BASE}
	docker push ${DOCKER_IMAGE_FULLNAME}
	docker images | grep ${DOCKER_IMAGE}

nexus-release:
	docker tag ${DOCKER_IMAGE_FULLNAME} docker.singlewave.co.uk/${DOCKER_IMAGE}:${VERSION}
	docker push docker.singlewave.co.uk/${DOCKER_IMAGE}:${VERSION}

release-all: release nexus-release

full-release:  build-base build release  ## buils all and releases
	@echo "Done"

.run:
	docker run \
			--rm \
	 		--name=${CONTAINER_NAME} \
			-p "${LOCAL_PORT}:8000" \
			-p "${LOCAL_HTTPS_PORT}:443" \
			-e DJANGO_SETTINGS_MODULE="django_temporary_permissions.config.settings" \
			-e DEBUG="${DEBUG}" \
			-e DATABASE_URL="${DATABASE_URL}" \
			-e SECRET_KEY="${SECRET_KEY}" \
			-e ADMIN_EMAIL="${ADMIN_EMAIL}" \
			-e ADMIN_USERNAME="${ADMIN_USERNAME}" \
			-e ADMIN_PASSWORD="${ADMIN_PASSWORD}" \
			-e STACK_PROTOCOL=${STACK_PROTOCOL} \
			--hostname host-ktech \
			-v "`pwd`/certs:/etc/certs:ro" \
			-v "${STATIC_ROOT}:/data/static" \
			-v "${MEDIA_ROOT}:/data/media" \
			${RUN_OPTIONS} \
			${DOCKER_IMAGE_FULLNAME} \
			${CMD}

run: ## run docker container locally with http
	STACK_PROTOCOL=http $(MAKE) .run

runs: ## run docker container locally with https
	$(MAKE) .run

shell: ## run shell container
	@RUN_OPTIONS=-it CMD='/bin/bash' $(MAKE) .run

test: ## run 'django-admin check --deploy' into container
	RUN_OPTIONS=-it CMD='django-admin check --deploy' $(MAKE) .run
	RUN_OPTIONS=-it CMD='uwsgi' $(MAKE) .run

stack:  ## run containder with both web/celery services
	RUN_OPTIONS=-it CMD='stack' $(MAKE) .run
