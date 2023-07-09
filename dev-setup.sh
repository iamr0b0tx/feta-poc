docker compose build
docker compose up -d registry
sleep 1
curl -X 'POST' \
  'http://127.0.0.1:9000/host/register/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "host.docker.internal:9501/ws"
}'
curl -X 'POST' \
  'http://127.0.0.1:9000/host/register/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "host.docker.internal:9502/ws"
}'
docker compose up -d
