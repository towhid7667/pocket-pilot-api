.PHONY: build run test clean flower

build:
    docker-compose -f docker-compose.yml build

run:
    docker-compose -f docker-compose.yml up -d

test:
    docker-compose -f docker-compose.test.yml up --abort-on-container-exit

clean:
    docker-compose -f docker-compose.yml down --volumes
    docker-compose -f docker-compose.test.yml down --volumes

flower:
    celery -A app.celery_worker.celery_app flower --port=5555