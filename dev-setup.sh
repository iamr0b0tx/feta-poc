docker compose build
docker compose up -d registry
sleep 1
curl -X 'POST' \
  'http://127.0.0.1:9000/hosts/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "http://host.docker.internal:9501"
}'
#curl -X 'POST' \
#  'http://127.0.0.1:9000/hosts/' \
#  -H 'accept: application/json' \
#  -H 'Content-Type: application/json' \
#  -d '{
#  "url": "http://host.docker.internal:9502"
#}'
docker compose up -d
