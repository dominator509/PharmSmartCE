#!/usr/bin/env sh
set -eu
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PATH="$PWD/scripts/bin:$PATH"

docker compose -f infra/docker-compose.yml up -d db >/dev/null

db_container="$(docker compose -f infra/docker-compose.yml ps -q db)"
if [ -z "$db_container" ]; then
  echo "ERROR: db container not available" >&2
  exit 1
fi

for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
  if docker exec "$db_container" pg_isready -U app -d pharm >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! docker exec "$db_container" pg_isready -U app -d pharm >/dev/null 2>&1; then
  echo "ERROR: db container is not ready" >&2
  exit 1
fi

restore_db="pharm_restore_$$"
dump_file="/tmp/${restore_db}.dump"
cleanup() {
  docker exec "$db_container" rm -f "$dump_file" >/dev/null 2>&1 || true
  docker exec "$db_container" dropdb --if-exists --username=app "$restore_db" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker exec "$db_container" pg_dump --format=custom --username=app --dbname=pharm --file="$dump_file"
docker exec "$db_container" createdb --username=app "$restore_db"
docker exec "$db_container" pg_restore --clean --if-exists --no-owner --username=app --dbname="$restore_db" "$dump_file"

table_count="$(docker exec "$db_container" psql --username=app --dbname="$restore_db" --tuples-only --no-align --command="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")"
if [ "${table_count:-0}" -le 0 ]; then
  echo "ERROR: restore validation returned no public tables" >&2
  exit 1
fi

echo "backup restore: ok ($table_count public tables restored)"
