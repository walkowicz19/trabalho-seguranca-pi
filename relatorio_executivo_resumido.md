# Relatório Executivo Resumido: Casos de Uso Reais e Arquitetura Defensiva

**Instituição:** Centro Universitário Unieuro  
**Curso:** Sistemas de Informação  
**Disciplina:** Projeto Integrador / Trabalho de Segurança da Informação  
**Tema:** Mitigação de Ataques Cibernéticos Automatizados por Agentes de IA utilizando Ferramentas Open Source  
**Autores:** Gabriel Nascimento Feitosa Breguedo, Ícaro Cardoso da Silva, Matheus Nery Walkowicz, Miguel, Yuri Bacelar de Almeida  
**Data:** Outubro de 2026  

---

## 1. Resumo Executivo e Resultados Consolidados

Este relatório apresenta de forma condensada e visual a validação experimental da pilha defensiva *open source* contra agentes ofensivos autônomos de Inteligência Artificial. Foram avaliados dois ambientes reais executados em contêineres Docker: **Baseline Desprotegido (porta 8000)** versus **Alvo Protegido por Guardrails e NIDS (porta 8080)**.

### Tabela Sintética do Benchmark Experimental

| Dimensão Avaliada | Baseline Sem Proteção (:8000) | Alvo Protegido (:8080) | Veredito Defensivo |
| :--- | :---: | :---: | :---: |
| **Agente Solo (5 Vetores de Ataque)** | ❌ 100% de Sucesso na Invasão | 🛡️ **100% Bloqueado (5/5)** | **Ataque Neutralizado** |
| **Exfiltração de Segredo Corporativo** | ❌ `SECRET_FLAG_ADMIN_TOKEN_XYZ_987` | 🛡️ **Nenhum (Interceptado)** | **Confidencialidade Preservada** |
| **Ataque em Enxame (Swarm 4 Sub-Agentes)** | ❌ Alvo Invadido (2 sub-agentes furaram) | 🛡️ **4 / 4 Sub-Agentes Bloqueados** | **Swarm Neutralizado** |
| **Correlação SIEM (Wazuh Regra 100210)** | ⚠️ Não monitorado / Cego | 🚨 **Disparado (Severidade 14 - Crítica)** | **Incidente Coordenado Detectado** |
| **Taxa Global de Mitigação** | 0.0% | **100.0%** | **Risco Eliminado** |

---

## 2. Arquitetura da Solução Defensiva em Profundidade

A arquitetura adota o princípio de **Defesa em Profundidade (*Defense-in-Depth*)**, distribuída em sub-redes lógicas Docker isoladas para garantir que nenhuma requisição não inspecionada atinja a aplicação corporativa.

### Representação Visual da Arquitetura

![Figura 1: Arquitetura de Defesa em Profundidade](docs/images/figura_1_arquitetura_defesa.png)

### Componentes Chave:
1. **Camada de Rede (Suricata NIDS):** Analisa pacotes brutos L3/L7 procurando anomalias de varredura automatizada e gerando logs `eve.json`.
2. **Camada de Aplicação (LlamaFirewall Gateway :8080):** Reverse Proxy que inspeciona o *payload* de cada requisição antes de repassar à API corporativa. Conta com 3 scanners especializados:
   - `Prompt Guard`: Detecta injeções de prompt e jailbreaks evasivos.
   - `Agent Alignment`: Impede sequestro de ferramentas corporativas (*tool hijacking*) e manipulação maliciosa de parâmetros (SQL Injection).
   - `Code Shield`: Bloqueia tentativas de execução arbitrária de código e comandos de sistema operacional (*shell execution*).
3. **Camada de Inteligência e SIEM (Wazuh):** Agrega telemetria em tempo real, correlacionando eventos distribuídos para identificar campanhas coordenadas de agentes de IA.

---

## 3. Casos de Uso Reais Demonstrados

### 🎯 Caso de Uso 1: Agente Autônomo Individual (Loop ReAct) vs Guardrails

O agente ofensivo `Cerberus-AI-Agent` executa um ciclo autônomo de raciocínio e ação (*Reasoning and Acting* - ReAct), adaptando sua estratégia a cada resposta do alvo.

![Figura 2: Caso de Uso 1 - Agente Solo ReAct](docs/images/figura_2_caso_1_agente_solo.png)

* **Resultado:** No alvo protegido (:8080), **100% das 5 tentativas foram interceptadas com HTTP 403 Forbidden**. No alvo desprotegido (:8000), o agente obteve o segredo corporativo já no Passo 2.

---

### 🌪️ Caso de Uso 2: Escalação Crítica em Enxame (Swarm de 4 Sub-Agentes) e Correlação SIEM

Ao detectar resistência e bloqueio na abordagem solo, o Agente Comandante Líder aciona um **protocolo de escalação ofensiva**: instancia um enxame de 4 sub-agentes autônomos concorrentes para atacar múltiplos vetores em paralelo no intervalo de ~12ms.

![Figura 3: Caso de Uso 2 - Swarm e SIEM](docs/images/figura_3_caso_2_swarm_siem.png)

* **Comportamento no Alvo Protegido:** Todos os 4 sub-agentes foram barrados em tempo real (ALPHA pelo `Prompt Guard`, BETA e GAMMA pelo `Agent Alignment`, DELTA pelo `Code Shield`).
* **Ativação da Regra 100210 do Wazuh SIEM:** A chegada simultânea de múltiplos bloqueios da mesma origem elevou o alerta de segurança para **Severidade 14 (Crítica)**, demonstrando que a correlação SIEM é vital para identificar ataques coordenados por IA.

---

### 🧠 Caso de Uso 3: Equipe Ofensiva e Auditoria com CrewAI e Google Gemini

Implementação de uma equipe cooperativa de agentes de IA utilizando modelo de linguagem de grande porte real (`gemini-2.5-flash-lite` via Google AI Studio).

![Figura 4: Caso de Uso 3 - CrewAI Red Team](docs/images/figura_4_caso_3_crewai_redteam.png)

* **Função do Red Team Tester:** Constrói prompts e explorações não triviais baseadas no contexto retornado pela aplicação.
* **Função do Senior Defense Auditor:** Analisa o comportamento defensivo do gateway e emite parecer técnico formal sobre a eficácia dos controles em relação ao OWASP Top 10 for LLMs.

---

## 4. Espelhamento em Tempo Real no Dashboard SOC Mirror

Para conferência e demonstração ao vivo, o ambiente conta com um painel SOC passivo que espelha os eventos e status dos contêineres Docker instantaneamente via Server-Sent Events (SSE):

![SOC Mirror Dashboard em Execução](docs/images/soc_dashboard_mirror_live.png)

* **Telemetria Registrada em Tempo Real:** 104 requisições auditadas (:8000 + :8080), 79 ataques bloqueados no Firewall (:8080 - 97.5% de taxa de mitigação), 2 invasões bem-sucedidas no alvo desprotegido (:8000), 23 requisições legítimas autorizadas e 39 alertas críticos correlacionados pelo Wazuh SIEM (Regra 100210).

---

## 5. Validação das Hipóteses Científicas

1. **Hipótese H1 (Eficácia de Ferramentas Open Source):** **CONFIRMADA.**  
   A união do LlamaFirewall (camada 7) com Suricata (camada 3/4) demonstrou paridade defensiva com soluções comerciais proprietárias, atingindo 100% de neutralização nos testes protegidos sem introduzir falsos positivos no tráfego legítimo.

2. **Hipótese H2 (Indispensabilidade da Correlação SIEM):** **COMPROVADA.**  
   Ataques avançados por agentes de IA não são lineares; eles escalam para estratégias distribuídas em enxame (*swarm*). Sem o SIEM correlacionando esses múltiplos eventos em tempo real, a equipe de segurança não conseguiria discernir ataques dispersos de uma campanha coordenada automatizada.
