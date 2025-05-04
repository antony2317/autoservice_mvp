#!/bin/sh

echo "Запуск Celery..."
celery -A autoservice_mvp worker --loglevel=info --pool=solo -E
