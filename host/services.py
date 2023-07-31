import time

from schemas import WebSocketRequest
from utils import make_request_id

DEFAULT_LATENCY_IN_SECS = 60


def make_request(req_id, req, request_queue, response_queue, latency_in_secs=DEFAULT_LATENCY_IN_SECS):
    request_queue[req_id] = req
    start_time = time.time()

    while time.time() - start_time < latency_in_secs and req_id not in response_queue:
        pass

    return response_queue.get(req_id)


def get_principal_metadata(request_queue, response_queue, latency_in_secs=DEFAULT_LATENCY_IN_SECS):
    req_id = make_request_id()
    req = WebSocketRequest(request_id=req_id, sender="", receiver="", endpoint="get_principal_metadata", body={"principal": "principal"})
    return make_request(req_id, req, request_queue, response_queue, latency_in_secs)
