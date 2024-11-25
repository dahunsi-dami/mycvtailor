#!/bin/bash
# scripts/start_server.sh

# Clear Redis cache
redis-cli FLUSHALL

# Preload templates
python manage.py preload_templates

# Start the server
python manage.py runserver
