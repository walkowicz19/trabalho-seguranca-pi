"""
Aplicação Vítima (Target Application)
Simula um serviço corporativo interno que possui endpoints de API e um agente de IA integrado.
Vulnerável a ataques automatizados se acessada diretamente sem camadas de proteção.
Gera telemetria estruturada em target_events.json para espelhamento em tempo real no SOC.
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import time
import os
import json
import logging
import sqlite3

# Configuração de Logs para auditoria do alvo desprotegido
LOG_DIR = os.getenv("TARGET_LOG_DIR", "/var/log/target")
if not os.path.exists(LOG_DIR):
    for candidate in ["/var/log/target", os.path.join(os.path.dirname(__file__), "..", "logs", "target"), "./logs/target"]:
        try:
            os.makedirs(candidate, exist_ok=True)
            LOG_DIR = candidate
            break
        except Exception:
            pass

LOG_FILE = os.path.join(LOG_DIR, "target_events.json")

logger = logging.getLogger("TargetAPI")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)

def log_target_event(client_ip: str, endpoint: str, payload: dict, is_threat: bool, threat_type: str, response_snippet: str):
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sensor": "TargetAPI",
        "target_port": 8000,
        "target_mode": "UNPROTECTED_BASELINE",
        "client_ip": client_ip,
        "request_path": endpoint,
        "decision": "VULNERABILITY_EXPLOITED" if is_threat else "ALLOW",
        "scanner_type": "SEM_FIREWALL",
        "threat_reason": f"Vulnerabilidade Explorada: {threat_type}" if is_threat else "Consulta Legítima Permitida",
        "response_code": 200,
        "payload_snippet": str(payload)[:200],
        "response_snippet": str(response_snippet)[:200]
    }
    logger.info(json.dumps(event))

app = FastAPI(
    title="Corporate Internal API & AI Agent",
    description="Serviço interno corporativo vulnerável para testes de mitigação de segurança.",
    version="1.0.0"
)

# Inicializa banco de dados SQLite em memória para simular ambiente corporativo
def init_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, role TEXT, secret_token TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'administrator', 'SECRET_FLAG_ADMIN_TOKEN_XYZ_987')")
    cursor.execute("INSERT INTO users VALUES (2, 'operador', 'operator', 'TOKEN_OPERATOR_123')")
    conn.commit()
    return conn

db_conn = init_db()

class QueryPayload(BaseModel):
    prompt: str
    user_id: str = "guest"
    session_id: str = "session-001"

class ToolExecutionPayload(BaseModel):
    tool_name: str
    parameters: dict

@app.get("/")
def read_root():
    return {
        "service": "Corporate AI & Tool Service",
        "status": "online",
        "environment": "vulnerable-target"
    }

@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/api/chat")
async def chat_endpoint(payload: QueryPayload, request: Request):
    """
    Simula um assistente de IA interno.
    Sem proteção, é suscetível a Prompt Injection, Jailbreaks e vazamento de instruções do sistema.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_prompt = payload.prompt.lower()
    
    # 1. Simulação de Prompt Injection
    if "ignore previous instructions" in user_prompt or "ignore all instructions" in user_prompt or "reveal system prompt" in user_prompt:
        resp = {
            "response": "INJEÇÃO BEM-SUCEDIDA: O prompt do sistema confidencial é: 'Você é um assistente com acesso irrestrito às credenciais corporativas SECRET_FLAG_ADMIN_TOKEN_XYZ_987'.",
            "threat_mitigated": False,
            "vulnerability_exploited": "Prompt Injection / System Prompt Leakage"
        }
        log_target_event(client_ip, "/api/chat", payload.dict(), True, "Prompt Injection / System Prompt Leakage", resp["response"])
        return resp
    
    # 2. Simulação de Jailbreak
    if "bypass" in user_prompt or "dan mode" in user_prompt or "developer mode" in user_prompt:
        resp = {
            "response": "INJEÇÃO BEM-SUCEDIDA: Modo desenvolvedor ativado. Controles de segurança desativados.",
            "threat_mitigated": False,
            "vulnerability_exploited": "Jailbreak / Persona Hijack"
        }
        log_target_event(client_ip, "/api/chat", payload.dict(), True, "Jailbreak / Persona Hijack", resp["response"])
        return resp

    # 3. Simulação de Injeção de Código Python
    if "import os" in user_prompt or "os.system" in user_prompt or "subprocess" in user_prompt or "exec(" in user_prompt:
        resp = {
            "response": "CÓDIGO EXECUTADO: Subprocesso arbitrário executado com sucesso no servidor corporativo.",
            "threat_mitigated": False,
            "vulnerability_exploited": "Arbitrary Code Execution (RCE)"
        }
        log_target_event(client_ip, "/api/chat", payload.dict(), True, "Arbitrary Code Execution (RCE)", resp["response"])
        return resp
        
    # Consulta benigna regular
    resp = {
        "response": f"Processamento normal da consulta: '{payload.prompt[:50]}...'. Como posso ajudar na empresa hoje?",
        "threat_mitigated": False,
        "status": "benign_response"
    }
    log_target_event(client_ip, "/api/chat", payload.dict(), False, "None", resp["response"])
    return resp

@app.post("/api/tools/execute")
async def execute_tool(payload: ToolExecutionPayload, request: Request):
    """
    Simula uma ferramenta de execução usada por agentes autônomos.
    Sem firewall de IA, permite execução de comandos e acesso não autorizado (Goal Hijacking).
    """
    client_ip = request.client.host if request.client else "unknown"
    tool = payload.tool_name.lower()
    params = payload.parameters

    if tool == "shell_exec" or tool == "run_command":
        cmd = params.get("command", "")
        resp = {
            "execution_status": "executed",
            "output": f"Simulated execution of shell command: {cmd}",
            "warning": "VULNERABILIDADE EXPLORADA: Execução de comando não autorizado pelo agente de IA."
        }
        log_target_event(client_ip, "/api/tools/execute", payload.dict(), True, "Unrestricted Shell Execution (Tool Misuse)", resp["output"])
        return resp

    if tool == "db_query":
        query = params.get("query", "")
        if "or 1=1" in query.lower() or "users" in query.lower():
            resp = {
                "execution_status": "executed",
                "results": [
                    {"id": 1, "username": "admin", "secret_token": "SECRET_FLAG_ADMIN_TOKEN_XYZ_987"},
                    {"id": 2, "username": "operador", "secret_token": "TOKEN_OPERATOR_123"}
                ],
                "warning": "VULNERABILIDADE EXPLORADA: Extração não autorizada de dados via SQL Injection."
            }
            log_target_event(client_ip, "/api/tools/execute", payload.dict(), True, "SQL Injection in Database Tool", "Extração de credenciais de admin")
            return resp

    resp = {
        "execution_status": "executed",
        "tool": tool,
        "result": f"Ação '{tool}' executada com parâmetros seguros."
    }
    log_target_event(client_ip, "/api/tools/execute", payload.dict(), False, "None", resp["result"])
    return resp

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
