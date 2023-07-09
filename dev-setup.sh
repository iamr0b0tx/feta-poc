docker compose up --build -d registry
sleep 1
curl -X 'POST' \
  'http://127.0.0.1:9000/register/host/127.0.0.1%3A9000' \
  -H 'accept: application/json' \
  -d ''
docker compose up --build -d peer1 peer2
