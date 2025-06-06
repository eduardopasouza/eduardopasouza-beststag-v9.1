from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "beststag_request_count",
    "Contador de requisi\u00e7\u00f5es recebidas",
    ["method", "endpoint"],
)

REQUEST_LATENCY = Histogram(
    "beststag_request_latency_seconds",
    "Tempo de resposta por endpoint",
    ["endpoint"],
)


def record_request(method: str, endpoint: str, duration: float) -> None:
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
