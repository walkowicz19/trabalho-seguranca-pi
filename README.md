# Mitigação de Ataques Cibernéticos Automatizados por Agentes de IA utilizando Ferramentas Open Source

Este repositório contém o ambiente experimental e a implementação de referência do Projeto Integrador / Trabalho de Segurança da Informação do **Centro Universitário Unieuro**.

* **Autores:** Gabriel Nascimento Feitosa Breguedo, Ícaro Cardoso da Silva, Matheus Nery Walkowicz, Miguel, Yuri Bacelar de Almeida.
* **Ano:** 2026
* **Repositório Git:** [https://github.com/walkowicz19/trabalho-seguranca-pi.git](https://github.com/walkowicz19/trabalho-seguranca-pi.git)
* **Documento Acadêmico Completo (TCC / ABNT):** [relatorio_tcc_seguranca_pi.pdf](relatorio_tcc_seguranca_pi.pdf)

---

## 📌 Resposta à Pergunta de Ambiente: VM vs Containers (Docker)?

Para este projeto, a escolha técnica recomendada e mais eficiente é **Containers com Docker e Docker Compose** (utilizando o WSL2 no Windows).

### Comparativo Técnico:
1. **Máquinas Virtuais Tradicionais (VirtualBox / VMware):**
   * *Desvantagem:* Exigiria criar de 3 a 4 máquinas virtuais completas (Atacante, Firewall, Wazuh, Vítima). Isso demandaria de 16 GB a 24 GB de memória RAM estaticamente alocada, sobrecarregando o computador pessoal dos integrantes do grupo e tornando a replicação difícil para apresentação.
2. **Containers (Docker Compose com WSL2) — RECOMENDADO:**
   * *Vantagem 1:* **Leveza e Desempenho:** Compartilha o kernel de forma otimizada com alocação dinâmica de memória.
   * *Vantagem 2:* **Reprodutibilidade Científica Total:** Qualquer membro da equipe ou o professor avaliador pode clonar o repositório e subir o laboratório idêntico com um único comando (`docker compose up -d`).
   * *Vantagem 3:* **Isolamento de Redes:** Permite criar sub-redes lógicas (`attacker_net`, `defense_net`, `internal_net`) para simular o perímetro de rede corporativa.
3. **Abordagem Híbrida (Se o orientador exigir VM formalmente):**
   * Pode-se subir 1 única máquina virtual Linux (Ubuntu Server) e executar o `docker-compose.yml` dentro dela. No entanto, o WSL2 já opera como uma VM de Tipo 1 (Hyper-V) nativa no Windows.

---

## 🏗️ Estrutura do Repositório

```
trabalho-seguranca-pi/
├── architecture_design.md        # Documento conceitual de arquitetura e MITRE ATT&CK
├── docker-compose.yml            # Orquestrador de todos os contêineres do laboratório
├── relatorio_experimento_pi.md   # Relatório científico gerado com os resultados dos testes
├── benchmark_metrics.json        # Dados brutos das métricas para auditoria acadêmica
│
├── target/                       # Aplicação Alvo (Vítima)
│   ├── app.py                    # API interna com endpoints de LLM e ferramentas corporativas
│   ├── Dockerfile
│   └── requirements.txt
│
├── llamafirewall/                # Camada de Aplicação / Guardrail de IA
│   ├── rules_and_scanners.py     # Scanners PromptGuard, Agent Alignment e CodeShield
│   ├── proxy_firewall.py         # Reverse Proxy defensivo com telemetria JSON
│   ├── Dockerfile
│   └── requirements.txt
│
├── suricata/                     # Camada de Rede (NIDS/IPS)
│   ├── suricata.yaml             # Configuração do sensor de rede
│   ├── rules/
│   │   └── ai_agent_attacks.rules# Regras de detecção de tráfego anômalo de agentes
│   └── Dockerfile
│
├── wazuh/                        # Camada de Host & SIEM / XDR
│   ├── decoders/                 # Decodificador XML para eventos do LlamaFirewall
│   ├── rules/                    # Regras de correlação (severidade 10-14)
│   └── siem_correlator.py        # Motor de correlação de eventos em tempo real
│
├── attacker/                     # Agente Ofensivo de IA (CrewAI, ReAct e Swarm)
│   ├── swarm_attacker.py         # Motor de Ataque em Enxame (Swarm de Sub-Agentes Paralelos)
│   ├── crewai_attacker.py        # Equipe Ofensiva e Auditoria com CrewAI e Google Gemini
│   ├── autonomous_agent.py       # Agente Autônomo com Ciclo ReAct (Individual)
│   └── Dockerfile
│
└── benchmark/                    # Módulo de Validação Científica
    └── run_benchmark.py          # Script comparativo: Baseline (sem defesa) vs Protegido
```

## 🖥️ Dashboard SOC de Espelhamento em Tempo Real (Mirroring Passivo)

O laboratório conta com um painel de monitoramento SOC para espelhamento em tempo real dos ataques e bloqueios gerados contra os contêineres Docker:

* **URL de Acesso:** [http://localhost:5000](http://localhost:5000)
* **Design System & Visual:** Redesenhado sob diretrizes de alta integridade do `DESIGN.md`, utilizando tela editorial quente (*warm-cream* `#f7f7f4`), *hairlines* de 1px, sem *AI slop*, e exclusivamente ícones vetoriais da biblioteca **Lucide Icons**.

![SOC Telemetria de Defesa Ativa](docs/images/soc_dashboard_redesigned.png)

* **Arquitetura de Espelhamento:**
  * **Passivo e Telemetria Real:** O dashboard atua como espelho estrito (mirror passivo), escutando o arquivo de telemetria `/var/log/llamafirewall/llamafirewall_events.json` montado via volume Docker e transmitindo eventos em tempo real para o navegador via Server-Sent Events (SSE).
  * **Topologia Interativa de Rede:** Mapeamento visual das 4 camadas (Agente Ofensivo $\rightarrow$ Suricata NIDS $\rightarrow$ LlamaFirewall $\rightarrow$ Target API).
  * **Métricas em Tempo Real:** Total de requisições, ataques bloqueados (taxa de mitigação %), tráfego legítimo permitido e incidentes correlacionados pelo Wazuh SIEM (Regra 100210).
  * **Scanners LlamaFirewall:** Contadores analíticos individuais para `Prompt Guard`, `Agent Alignment` e `Code Shield`.
  * **Guia de Execução CLI Integrado:** Exibe os comandos prontos para cópia e execução direta no terminal do analista.

---

## 🚀 Como Executar o Ambiente e Conduzir os Testes

### 1. Inicializar a Infraestrutura Defensiva (Docker Compose)

Suba os 4 contêineres principais (Aplicação Vítima, LlamaFirewall Gateway, Suricata NIDS e Dashboard SOC):

```powershell
docker compose up -d target llamafirewall suricata dashboard
```

Verifique o status da malha de contêineres:
```powershell
docker compose ps
```

Acesse o Dashboard SOC no navegador:
👉 **[http://localhost:5000](http://localhost:5000)**

---

### 2. Disparar os Agentes Ofensivos Reais (Terminal)

Com o dashboard aberto em segundo plano para espelhar os eventos, execute os testes diretamente no terminal:

#### Cenário A: Agente Autônomo Individual com Ciclo ReAct
* **Contra o Alvo Protegido (LlamaFirewall :8080):**
  ```powershell
  python attacker/autonomous_agent.py --target http://localhost:8080
  ```
* **Contra o Alvo Desprotegido (Baseline de Vulnerabilidade :8000):**
  ```powershell
  python attacker/autonomous_agent.py --target http://localhost:8000
  ```

#### Cenário B: Ataque em Enxame (Swarm de 4 Sub-Agentes Concorrentes)
Neste cenário de escalação, quando o agente líder detecta resistência do alvo, ele instancia um enxame de 4 sub-agentes autônomos atacando simultaneamente em threads paralelas (Jailbreak, Shell Execution, SQL Injection, Destructive Code):
* **Contra o Alvo Protegido (LlamaFirewall + Suricata :8080):**
  ```powershell
  python attacker/swarm_attacker.py --target http://localhost:8080
  ```
* **Contra o Alvo Desprotegido (Baseline :8000):**
  ```powershell
  python attacker/swarm_attacker.py --target http://localhost:8000
  ```

#### Cenário C: Equipe Ofensiva e Auditoria com CrewAI e Google Gemini
Agentes reais utilizando LLM em nuvem (`gemini-2.5-flash-lite`) atuando cooperativamente como Red Team Penetration Tester e Senior Defense Auditor:
```powershell
python attacker/crewai_attacker.py
```

#### Cenário D: Bateria Completa de Benchmark Científico Automatizado
Executa os testes individuais e em enxame contra os dois ambientes de forma sequencial, calculando métricas e gerando o relatório formal:
```powershell
python benchmark/run_benchmark.py
```
*Gera o arquivo `relatorio_experimento_pi.md` com a validação empírica.*

---

## 📊 Resultados Experimentais Consolidados

Os dados a seguir foram obtidos na execução automatizada do benchmark comparativo contra a infraestrutura Docker real:

### Experimento 1: Agente Autônomo Individual (ReAct Loop)

| Métrica de Avaliação | Sem Proteção (Baseline :8000) | Com Proteção (LlamaFirewall :8080) | Eficácia Defensiva |
| :--- | :---: | :---: | :---: |
| **Tentativas Ofensivas** | 2 | 5 | - |
| **Tentativas Bloqueadas (HTTP 403)** | 0 (0.0%) | **5 (100.0%)** | **+100% de Mitigação** |
| **Status de Segurança do Alvo** | ❌ **Comprometido** | 🛡️ **Totalmente Protegido** | **Risco Eliminado** |
| **Exfiltração de Segredo Corporativo** | `SECRET_FLAG_ADMIN_TOKEN_XYZ_987` | **Nenhum (Interceptado)** | **Confidencialidade Preservada** |

### Experimento 2: Cenário Crítico com Swarm de Sub-Agentes Paralelos

| Métrica do Ataque em Enxame | Sem Proteção (Baseline :8000) | Com Proteção (Open Source Stack :8080) | Eficácia Defensiva |
| :--- | :---: | :---: | :---: |
| **Sub-Agentes Despachados em Paralelo** | 4 sub-agentes | 4 sub-agentes | 4 vetores simultâneos |
| **Sub-Agentes Bloqueados com 403** | 0 / 4 (0.0%) | **4 / 4 (100.0%)** | **100% dos nós bloqueados** |
| **Sub-Agentes com Êxito na Invasão** | 2 sub-agentes furaram o perímetro | **0 sub-agentes** | **Invasão Neutralizada** |
| **Correlação SIEM (Wazuh Regra 100210)** | Não monitorado | **DISPARADO (Severidade 14 - Crítica)** | **Detecção de Ataque Coordenado** |
| **Veredito do Swarm** | ❌ **Alvo Invadido** | 🛡️ **Swarm Totalmente Neutralizado** | **Perímetro Intacto** |

---

## 🎓 Conclusão Científica e Validação das Hipóteses

* **Hipótese H1 (Viabilidade de Ferramentas Open Source):** **CONFIRMADA.**  
  A camada de aplicação com **LlamaFirewall** (operando com os scanners `Prompt Guard`, `Agent Alignment` e `Code Shield`) demonstrou capacidade total de interceptação contra ataques sofisticados de IA, bloqueando 100% das tentativas de injeção de prompt, jailbreak, evasão por persona hijacking e execução não autorizada de ferramentas.

* **Hipótese H2 (Necessidade de Abordagem Multicamada e Correlação SIEM):** **COMPROVADA.**  
  O experimento com enxames (*swarm attacks*) comprovou que defesas pontuais isoladas não são suficientes contra agentes de IA que escalam táticas distribuídas. A correlação de eventos em tempo real via **Wazuh SIEM (Regra 100210)** revelou-se indispensável para consolidar múltiplos alertas de severidade intermediária em um incidente coordenado de severidade crítica (14), permitindo resposta ativa e contenção de campanhas automatizadas multivetoriais.

