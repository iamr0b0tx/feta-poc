docker compose build
docker compose up -d registry
sleep 1
curl -X 'POST' \
  'http://127.0.0.1:9000/hosts/register/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "127.0.0.1:9501/ws"
}'
curl -X 'POST' \
  'http://127.0.0.1:9000/hosts/register/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "127.0.0.1:9502/ws"
}'
docker compose up -d
