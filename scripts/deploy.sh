#!/bin/sh
set -eu

cd /opt/inter

git fetch origin main
git checkout main
git pull --ff-only origin main

docker compose up -d --build --remove-orphans
docker compose ps

attempt=0
until wget --quiet --spider http://127.0.0.1:8080/; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 12 ]; then
    docker compose logs --tail=100 web
    exit 1
  fi
  sleep 5
done

attempt=0
until wget --quiet --spider http://127.0.0.1:8080/api/v1/health/ready; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 12 ]; then
    docker compose logs --tail=100 api migrate db
    exit 1
  fi
  sleep 5
done

echo "Inter deployment is healthy."
