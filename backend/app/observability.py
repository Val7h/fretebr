"""
Observabilidade leve:
- Structured logging (JSON) com request_id
- Middleware que adiciona X-Request-ID em todas as respostas
- Endpoint /metrics com contadores in-process (Prometheus-ready)
- Hooks de Sentry quando SENTRY_DSN definido
"""
import logging
import time
import uuid
import os
from collections import defaultdict
from contextvars import ContextVar
from fastapi import Request

# Request context
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = _request_id_ctx.get()
        return True


class JsonFormatter(logging.Formatter):
    """Formatter JSON real (para Loki/Datadog/CloudWatch)."""
    def format(self, record):
        import json as _json
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return _json.dumps(payload, ensure_ascii=False)


def setup_logging():
    """Configura logging estruturado com request_id. JSON em prod/staging, texto em dev."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    handler = logging.StreamHandler()
    if env in ("production", "staging") or os.getenv("LOG_JSON", "").lower() == "true":
        handler.setFormatter(JsonFormatter())
    else:
        fmt = "%(asctime)s | %(levelname)s | rid=%(request_id)s | %(name)s | %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(RequestIdFilter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def setup_sentry():
    """Inicializa Sentry se SENTRY_DSN definido."""
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            environment=os.getenv("ENVIRONMENT", "staging"),
        )
        logging.getLogger(__name__).info("[OBS] Sentry inicializado")
        return True
    except ImportError:
        logging.getLogger(__name__).warning(
            "[OBS] SENTRY_DSN definido mas sentry-sdk nao instalado"
        )
        return False


# Metricas in-process (Prometheus-style counters)
class Metrics:
    def __init__(self):
        self.request_count = defaultdict(int)        # (method, path, status) -> count
        self.request_duration_ms = defaultdict(list) # path -> [duration_ms]
        self.errors_total = 0
        self.started_at = time.time()

    def record_request(self, method: str, path: str, status: int, duration_ms: float):
        # Sanitiza path - agrupa IDs numericos
        norm_path = self._normalize_path(path)
        self.request_count[(method, norm_path, status)] += 1
        self.request_duration_ms[norm_path].append(duration_ms)
        # Keep last 1000 per path
        if len(self.request_duration_ms[norm_path]) > 1000:
            self.request_duration_ms[norm_path] = self.request_duration_ms[norm_path][-1000:]
        if status >= 500:
            self.errors_total += 1

    @staticmethod
    def _normalize_path(path: str) -> str:
        # /api/matches/123 -> /api/matches/:id
        import re
        return re.sub(r"/\d+", "/:id", path)

    def render_prometheus(self) -> str:
        lines = []
        lines.append("# HELP fretebr_uptime_seconds Seconds since startup")
        lines.append("# TYPE fretebr_uptime_seconds gauge")
        lines.append(f"fretebr_uptime_seconds {time.time() - self.started_at:.1f}")
        lines.append("")
        lines.append("# HELP fretebr_errors_total Total 5xx responses")
        lines.append("# TYPE fretebr_errors_total counter")
        lines.append(f"fretebr_errors_total {self.errors_total}")
        lines.append("")
        lines.append("# HELP fretebr_requests_total Total HTTP requests")
        lines.append("# TYPE fretebr_requests_total counter")
        for (method, path, status), count in sorted(self.request_count.items()):
            lines.append(
                f'fretebr_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
            )
        lines.append("")
        lines.append("# HELP fretebr_request_duration_ms_avg Mean duration per path")
        lines.append("# TYPE fretebr_request_duration_ms_avg gauge")
        for path, durations in sorted(self.request_duration_ms.items()):
            if durations:
                avg = sum(durations) / len(durations)
                lines.append(f'fretebr_request_duration_ms_avg{{path="{path}"}} {avg:.2f}')
        return "\n".join(lines) + "\n"

    def summary_json(self) -> dict:
        per_path = {}
        for path, durations in self.request_duration_ms.items():
            if durations:
                per_path[path] = {
                    "count": len(durations),
                    "avg_ms": round(sum(durations) / len(durations), 2),
                    "p95_ms": round(sorted(durations)[int(len(durations) * 0.95)], 2)
                                if len(durations) >= 20 else None,
                }
        return {
            "uptime_seconds": round(time.time() - self.started_at, 1),
            "errors_total": self.errors_total,
            "total_requests": sum(self.request_count.values()),
            "per_path": per_path,
        }


metrics = Metrics()


async def request_id_middleware(request: Request, call_next):
    """Adiciona X-Request-ID + metricas em cada request."""
    rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    token = _request_id_ctx.set(rid)
    start = time.time()
    response = None
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        metrics.record_request(
            request.method, request.url.path, status_code, duration_ms
        )
        if response is not None:
            response.headers["X-Request-ID"] = rid
        _request_id_ctx.reset(token)
