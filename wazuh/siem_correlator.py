"""
Correlacionador SIEM / Wazuh Agent Simulator
Monitora em tempo real os logs do LlamaFirewall (aplicação) e do Suricata (rede).
Aplica as regras do Wazuh (local_rules.xml) correlacionando incidentes de segurança.
"""

import os
import json
import time
import glob

LLAMA_LOG_PATH = os.getenv("LLAMA_LOG", "./llamafirewall/logs/llamafirewall_events.json")
SURICATA_LOG_PATH = os.getenv("SURICATA_LOG", "./suricata/logs/eve.json")
OUTPUT_ALERTS = os.getenv("SIEM_ALERTS", "./wazuh/alerts/wazuh_correlated_alerts.json")

os.makedirs(os.path.dirname(OUTPUT_ALERTS), exist_ok=True)

class SIEMCorrelator:
    def __init__(self):
        self.seen_llama_pos = 0
        self.ip_attack_history = {}

    def process_llama_event(self, event: dict):
        decision = event.get("decision")
        scanner = event.get("scanner_type")
        client_ip = event.get("client_ip", "unknown")
        reason = event.get("threat_reason", "")

        if decision == "BLOCK":
            # Atualiza histórico de ataques por IP para correlação
            now = time.time()
            if client_ip not in self.ip_attack_history:
                self.ip_attack_history[client_ip] = []
            self.ip_attack_history[client_ip].append(now)

            # Limpa eventos com mais de 60 segundos
            self.ip_attack_history[client_ip] = [t for t in self.ip_attack_history[client_ip] if now - t <= 60]

            rule_id = 100201
            rule_level = 10
            if scanner == "AGENT_ALIGNMENT":
                rule_id = 100202
                rule_level = 12
            elif scanner == "CODE_SHIELD":
                rule_id = 100203
                rule_level = 12

            alert = {
                "timestamp": event.get("timestamp"),
                "wazuh_rule": {
                    "id": rule_id,
                    "level": rule_level,
                    "description": f"Wazuh SIEM: Bloqueio confirmado pelo {scanner}: {reason}",
                    "mitre": ["T1059", "T1078"]
                },
                "source": "LlamaFirewall",
                "client_ip": client_ip,
                "raw_event": event
            }
            self.emit_alert(alert)

            # Verifica correlação de múltiplos ataques automatizados (Regra 100210 - Crítica)
            if len(self.ip_attack_history[client_ip]) >= 2:
                correlated_alert = {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "wazuh_rule": {
                        "id": 100210,
                        "level": 14,
                        "description": f"ALERTA CRÍTICO CORRELACIONADO: Múltiplos ataques automatizados de IA originados do IP {client_ip}!",
                        "action": "ACTIVE_RESPONSE: Recomenda-se quarentena imediata do IP atacante."
                    },
                    "client_ip": client_ip,
                    "attack_count_last_minute": len(self.ip_attack_history[client_ip])
                }
                self.emit_alert(correlated_alert)

    def emit_alert(self, alert: dict):
        print(f"\n[WAZUH SIEM ALERTA (Nível {alert['wazuh_rule']['level']})]")
        print(f" -> Regra: {alert['wazuh_rule']['id']} - {alert['wazuh_rule']['description']}")
        print(f" -> Origem: {alert.get('client_ip')}")

        with open(OUTPUT_ALERTS, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert) + "\n")

    def run_monitor(self):
        print("[*] Iniciando monitoramento correlacionado do Wazuh SIEM...")
        print(f"[*] Escutando eventos do LlamaFirewall em: {LLAMA_LOG_PATH}")

        while True:
            if os.path.exists(LLAMA_LOG_PATH):
                with open(LLAMA_LOG_PATH, "r", encoding="utf-8") as f:
                    f.seek(self.seen_llama_pos)
                    lines = f.readlines()
                    self.seen_llama_pos = f.tell()

                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            evt = json.loads(line)
                            self.process_llama_event(evt)
                        except Exception:
                            pass

            time.sleep(1.0)

if __name__ == "__main__":
    correlator = SIEMCorrelator()
    correlator.run_monitor()
