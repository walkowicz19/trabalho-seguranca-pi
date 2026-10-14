FROM jasonish/suricata:latest

COPY suricata.yaml /etc/suricata/suricata.yaml
COPY rules/ai_agent_attacks.rules /etc/suricata/rules/ai_agent_attacks.rules

RUN mkdir -p /var/log/suricata

CMD ["-i", "eth0", "-c", "/etc/suricata/suricata.yaml", "-v"]
