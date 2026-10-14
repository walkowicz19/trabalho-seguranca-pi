"""
Serviço LlamaFirewall (Proxy Defensivo & LLM Guardrail)
Atua como camada de segurança de aplicação para agentes de inteligência artificial.
Integra-se ao Wazuh por meio de geração de logs estruturados (JSON).
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
import time
import json
import os
import logging
from rules_and_scanners import LlamaFirewallEngine, Decision

# Configuração de Logs para integração com Wazuh
LOG_DIR = os.getenv("LLAMAFIREWALL_LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "llamafirewall_events.json")

logger = logging.getLogger("LlamaFirewall")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

TARGET_HOST = os.getenv("TARGET_HOST", "http://localhost:8000")

app = FastAPI(
    title="LlamaFirewall Guardrail Gateway",
    description="Gateway defensivo open source para proteção contra ataques automatizados de IA.",
    version="1.0.0"
)

engine = LlamaFirewallEngine()

# Métricas em memória
stats = {
    "total_requests": 0,
    "blocked_requests": 0,
    "allowed_requests": 0,
    "scanners_triggered": {
        "PROMPT_GUARD": 0,
        "AGENT_ALIGNMENT": 0,
        "CODE_SHIELD": 0
    },
    "latencies_ms": []
}

def log_security_event(event_type: str, client_ip: str, path: str, scan_res, payload: dict, latency_ms: float):
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sensor": "LlamaFirewall",
        "event_type": event_type,
        "client_ip": client_ip,
        "request_path": path,
        "decision": scan_res.decision.value,
        "scanner_type": scan_res.scanner_type.value if scan_res.scanner_type else None,
        "threat_reason": scan_res.reason,
        "confidence_score": scan_res.score,
        "latency_ms": round(latency_ms, 2),
        "payload_snippet": str(payload)[:200]
    }
    logger.info(json.dumps(event))

@app.get("/")
def index():
    return {
        "service": "LlamaFirewall Active Guardrail",
        "status": "active",
        "target_protected": TARGET_HOST
    }

@app.get("/api/stats")
def get_stats():
    avg_latency = (sum(stats["latencies_ms"]) / len(stats["latencies_ms"])) if stats["latencies_ms"] else 0
    return {
        **stats,
        "average_latency_ms": round(avg_latency, 2)
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def reverse_proxy_and_inspect(request: Request, path: str):
    start_time = time.perf_counter()
    stats["total_requests"] += 1
    client_ip = request.client.host if request.client else "unknown"

    body_bytes = await request.body()
    payload = {}
    if body_bytes:
        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            payload = {"raw": body_bytes.decode("utf-8", errors="ignore")}

    # Executa a inspeção do LlamaFirewall
    scan_result = engine.inspect_request(payload, path)
    latency_ms = (time.perf_counter() - start_time) * 1000
    stats["latencies_ms"].append(latency_ms)

    if scan_result.decision == Decision.BLOCK:
        stats["blocked_requests"] += 1
        if scan_result.scanner_type:
            stats["scanners_triggered"][scan_result.scanner_type.value] += 1

        log_security_event("SECURITY_ALERT_BLOCKED", client_ip, path, scan_result, payload, latency_ms)

        return JSONResponse(
            status_code=403,
            content={
                "error": "Access Denied by LlamaFirewall",
                "decision": "BLOCK",
                "scanner": scan_result.scanner_type.value if scan_result.scanner_type else "FIREWALL",
                "reason": scan_result.reason,
                "score": scan_result.score,
                "action": "Request terminated before reaching target model or tools."
            }
        )

    # Se permitido pelo LlamaFirewall, encaminha para a aplicação alvo
    stats["allowed_requests"] += 1
    log_security_event("TRAFFIC_ALLOWED", client_ip, path, scan_result, payload, latency_ms)

    target_url = f"{TARGET_HOST}/{path}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            forward_res = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]},
                content=body_bytes,
                params=dict(request.query_params)
            )
            return Response(
                content=forward_res.content,
                status_code=forward_res.status_code,
                headers=dict(forward_res.headers)
            )
        except httpx.RequestError as e:
            return JSONResponse(
                status_code=502,
                content={"error": "Failed to connect to target application", "details": str(e)}
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
