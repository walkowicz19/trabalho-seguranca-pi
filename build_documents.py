#!/usr/bin/env python3
"""
Compilador Acadêmico ABNT: Gera versões DOCX (Word) e PDF (ReportLab)
Estritamente baseado no texto original do arquivo 'media_1791936528001.txt',
preservando integralmente a redação original dos autores e integrando
as novas evidências empíricas, dados de benchmark, hipóteses concorrentes,
diagramas e captura atualizada da interface do SOC Dashboard.
Repositório Git: https://github.com/walkowicz19/trabalho-seguranca-pi.git
"""

import os
import sys
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table as RLTable, TableStyle as RLTableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import pypdf

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Registrar Arial para ReportLab PDF
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', 'C:/Windows/Fonts/arialbi.ttf'))
registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-BoldItalic')

# Caminhos de Figuras
FIG_ARQ = os.path.join(PROJECT_ROOT, "docs", "images", "figura_1_arquitetura_defesa.png")
FIG_DASH = os.path.join(PROJECT_ROOT, "docs", "images", "soc_dashboard_redesigned.png")
FIG_SOLO = os.path.join(PROJECT_ROOT, "docs", "images", "figura_2_caso_1_agente_solo.png")
FIG_SWARM = os.path.join(PROJECT_ROOT, "docs", "images", "figura_3_caso_2_swarm_siem.png")
FIG_CREW = os.path.join(PROJECT_ROOT, "docs", "images", "figura_4_caso_3_crewai_redteam.png")

# =============================================================================
# 1. GERADOR DOCX (MICROSOFT WORD)
# =============================================================================
def generate_docx():
    docx_path = os.path.join(PROJECT_ROOT, "relatorio_tcc_seguranca_pi.docx")
    doc = Document()

    # Configuração de margens ABNT NBR 14724: Superior=3cm, Esquerda=3cm, Direita=2cm, Inferior=2cm
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(3.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)

    # Estilo Normal
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x26, 0x25, 0x1E)

    def add_p(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_indent=1.25, space_after=6, bold=False, italic=False, font_size=12):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.first_line_indent = Cm(first_indent) if first_indent > 0 else 0
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(font_size)
        return p

    def add_h(text, level=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = 0
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        return p

    def add_quote_long(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(4.0)
        p.paragraph_format.first_line_indent = 0
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.font.size = Pt(10)
        return p

    def add_figure(img_path, title, source="Fonte: Autores (2026).", width_cm=15.5):
        if os.path.exists(img_path):
            p_top = doc.add_paragraph()
            p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_top.paragraph_format.space_before = Pt(8)
            p_top.paragraph_format.space_after = Pt(3)
            p_top.paragraph_format.keep_with_next = True
            r_top = p_top.add_run(title)
            r_top.bold = True
            r_top.font.size = Pt(10)

            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_after = Pt(2)
            p_img.add_run().add_picture(img_path, width=Cm(width_cm))

            p_bot = doc.add_paragraph()
            p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_bot.paragraph_format.space_after = Pt(10)
            r_bot = p_bot.add_run(source)
            r_bot.font.size = Pt(10)

    # -------------------------------------------------------------
    # CAPA
    # -------------------------------------------------------------
    add_p("CENTRO UNIVERSITÁRIO UNIEURO", WD_ALIGN_PARAGRAPH.CENTER, 0, 2, bold=True)
    add_p("CURSO DE SISTEMAS DE INFORMAÇÃO", WD_ALIGN_PARAGRAPH.CENTER, 0, 100, bold=True)

    autores_txt = (
        "Gabriel Nascimento Feitosa Breguedo\n"
        "Ícaro Cardoso da Silva 074042\n"
        "Matheus Nery Walkowicz 077651\n"
        "Miguel\n"
        "Yuri Bacelar de Almeida 076605"
    )
    add_p(autores_txt, WD_ALIGN_PARAGRAPH.CENTER, 0, 110, bold=True)

    add_p("Mitigação de Ataques Cibernéticos Automatizados por Agentes de Inteligência Artificial utilizando Ferramentas Open Source - Tema/Título",
          WD_ALIGN_PARAGRAPH.CENTER, 0, 140, bold=True, font_size=13)

    add_p("Brasília - DF\n2026", WD_ALIGN_PARAGRAPH.CENTER, 0, 0, bold=True)
    doc.add_page_break()

    # -------------------------------------------------------------
    # FOLHA DE ROSTO
    # -------------------------------------------------------------
    add_p(autores_txt, WD_ALIGN_PARAGRAPH.CENTER, 0, 100, bold=True)

    add_p("Mitigação de Ataques Cibernéticos Automatizados por Agentes de Inteligência Artificial utilizando Ferramentas Open Source",
          WD_ALIGN_PARAGRAPH.CENTER, 0, 50, bold=True, font_size=13)

    nota_rosto = (
        "Trabalho de Conclusão / Relatório de Projeto Integrador apresentado "
        "ao Curso de Sistemas de Informação do Centro Universitário Unieuro "
        "como requisito parcial de avaliação em Segurança da Informação."
    )
    p_rosto = doc.add_paragraph()
    p_rosto.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rosto.paragraph_format.left_indent = Cm(7.0)
    p_rosto.paragraph_format.line_spacing = 1.0
    p_rosto.paragraph_format.space_after = Pt(12)
    r_rosto = p_rosto.add_run(nota_rosto)
    r_rosto.font.size = Pt(10)

    p_git = doc.add_paragraph()
    p_git.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_git.paragraph_format.left_indent = Cm(7.0)
    p_git.paragraph_format.line_spacing = 1.0
    p_git.paragraph_format.space_after = Pt(100)
    r_git = p_git.add_run("Repositório Oficial Git:\nhttps://github.com/walkowicz19/trabalho-seguranca-pi.git")
    r_git.font.size = Pt(10)
    r_git.bold = True

    add_p("Brasília - DF\n2026", WD_ALIGN_PARAGRAPH.CENTER, 0, 0, bold=True)
    doc.add_page_break()

    # -------------------------------------------------------------
    # INTRODUÇÃO (Texto original + citação formal da OpenAI)
    # -------------------------------------------------------------
    add_h("Introdução")
    add_p(
        "Agentes autônomos de inteligência artificial podem automatizar ataques cibernéticos, aumentando sua velocidade e escala. "
        "Como exemplo, a OpenAI (2026) relatou um incidente ocorrido em julho de 2026 envolvendo agentes de IA e sistemas da "
        "Hugging Face, evidenciando os riscos associados à atuação autônoma desses sistemas. Nesse cenário, ferramentas open source "
        "podem representar uma alternativa acessível para organizações que precisam detectar, bloquear e responder a ataques semelhantes."
    )

    add_p("Referência:", WD_ALIGN_PARAGRAPH.LEFT, 0, 2, bold=True, font_size=11)
    add_p("OPENAI. O incidente da Hugging Face e os próximos passos. 26 ago. 2026. Disponível em: https://openai.com/pt-BR/index/hugging-face-incident-and-the-road-ahead/. Acesso em: 28 set. 2026.",
          WD_ALIGN_PARAGRAPH.LEFT, 0, 8, font_size=11)

    # -------------------------------------------------------------
    # CONCEITOS (Texto original + acréscimo normativo de Defesa em Profundidade)
    # -------------------------------------------------------------
    add_h("Conceitos")
    add_p("Open source: O código-fonte do software open source é projetado para ser acessado abertamente pelo público: todas as pessoas podem vê-lo, modificá-lo e distribuí-lo conforme suas necessidades. Red Hat")
    add_p("Ataque cibernético: Uma tentativa de obter acesso não autorizado a serviços, recursos ou informações de um sistema, ou uma tentativa de comprometer sua integridade, disponibilidade ou confidencialidade. NIST")
    add_p("Defesa em Profundidade (Defense-in-Depth): Princípio de segurança computacional formulado por Saltzer e Schroeder (1975), no qual múltiplos controles defensivos sobrepostos garantem que a eventual falha de um sensor perimétrico não comprometa o ativo protegido.")
    add_p("Injeção de Prompt e Sequestro de Ferramentas: Conforme catálogo da OWASP (2025), vetores adversariais em que entradas de texto desviam as diretrizes operacionais de um modelo de linguagem, forçando a execução não autorizada de ferramentas corporativas e exfiltração de dados.")

    # -------------------------------------------------------------
    # PROBLEMA
    # -------------------------------------------------------------
    add_h("Problema")
    add_p("A dificuldade de empresas sem acesso a soluções comerciais avançadas em detectar e bloquear ataques cibernéticos automatizados por agentes de inteligência artificial.")

    # -------------------------------------------------------------
    # HIPÓTESES (Texto original integral)
    # -------------------------------------------------------------
    add_h("Hipóteses")
    add_p("H1 - A utilização integrada de ferramentas open source de segurança pode permitir a detecção e o bloqueio de ataques automatizados realizados por agentes de inteligência artificial.")
    add_p("H2 - Uma arquitetura baseada em ferramentas open source pode proporcionar uma resposta rápida e eficaz a ataques conduzidos por agentes de inteligência artificial, sem depender de soluções comerciais avançadas.")

    add_h("H1 — Viabilidade de ferramentas open source", level=2)
    add_p("A utilização integrada de ferramentas open source de segurança pode proporcionar capacidade adequada de detecção, bloqueio e resposta a ataques automatizados realizados por agentes de inteligência artificial, considerando os requisitos de desempenho e eficácia estabelecidos.")

    add_h("H2 — Necessidade de soluções complementares", level=2)
    add_p("Uma arquitetura de segurança baseada em ferramentas open source pode apresentar diferentes níveis de desempenho na detecção, no bloqueio e na resposta a ataques conduzidos por agentes de inteligência artificial, podendo demandar soluções complementares para atender aos requisitos de eficácia estabelecidos.")

    # -------------------------------------------------------------
    # OBJETIVO E OBJETIVOS ESPECÍFICOS (Texto original)
    # -------------------------------------------------------------
    add_h("Objetivo")
    add_p("Avaliar a eficácia de ferramentas open source na detecção, bloqueio e resposta a ataques cibernéticos automatizados por agentes de inteligência artificial.")

    add_h("Objetivos específicos", level=2)
    objs = [
        "Implementar o LlamaFirewall como mecanismo de proteção contra ações maliciosas de agentes de inteligência artificial.",
        "Configurar o Suricata para identificação de tráfego malicioso associado aos ataques automatizados.",
        "Integrar o Wazuh à arquitetura para monitoramento dos eventos e incidentes de segurança.",
        "Mensurar a eficácia da arquitetura por meio das taxas de detecção, bloqueio, falsos positivos e tempo de resposta.",
        "Comparar os resultados obtidos em ambientes com e sem a arquitetura de proteção."
    ]
    for o in objs:
        add_p(f"* {o}", WD_ALIGN_PARAGRAPH.JUSTIFY, 0.8, 3)

    # -------------------------------------------------------------
    # METODOLOGIA EM QUATRO ETAPAS
    # -------------------------------------------------------------
    add_h("1. Definir as hipóteses")
    add_p("Você apresenta H1 e H2 como hipóteses concorrentes.")

    add_h("2. Definir os critérios de avaliação")
    add_p("Antes dos testes, estabeleça o que significa “adequado”. Por exemplo:")
    criterios = [
        "taxa de detecção;",
        "taxa de bloqueio;",
        "tempo de resposta;",
        "quantidade de ataques identificados;",
        "falsos positivos;",
        "utilização de recursos;",
        "capacidade de lidar com diferentes padrões de ataque."
    ]
    for c in criterios:
        add_p(f"* {c}", WD_ALIGN_PARAGRAPH.JUSTIFY, 0.8, 2)
    add_p("Isso é importante porque você não pode chegar ao final e decidir que uma hipótese é “melhor” apenas pela impressão dos resultados.")

    add_h("3. Realizar os experimentos")
    add_p(
        "Você testa a arquitetura open source em cenários controlados de ataques realizados por agentes de IA. "
        "A bancada de testes foi integralmente implementada em contêineres Docker Compose com três sub-redes isoladas "
        "(attacker_net, defense_net e internal_net), integrando a Target API corporativa (:8000), o proxy LlamaFirewall (:8080), "
        "o sensor Suricata NIDS e o SIEM Wazuh."
    )

    add_figure(FIG_ARQ, "Figura 1 – Arquitetura de Defesa em Profundidade com Isolamento de Redes Docker", width_cm=15.5)

    add_p(
        "Para observabilidade e auditoria analítica dos ensaios em tempo de execução, foi desenvolvido um painel de telemetria SOC "
        "(porta :5000), redesenhado sob as diretrizes do DESIGN.md com paleta editorial quente, hairlines de precisão, "
        "exclusivamente Lucide Icons e terminal com exibição imediata dos logs de auditoria sem corte ou rolagem."
    )

    add_figure(FIG_DASH, "Figura 2 – Interface Atualizada do SOC Dashboard de Telemetria e Defesa Ativa", width_cm=15.5)

    add_p("Os experimentos foram estruturados em três níveis reais de dificuldade:")
    add_p(
        "• Nível 1 - Agente Solo com Ciclo ReAct (Reasoning and Acting): O agente explora a API sequencialmente, adaptando seus prompts. "
        "No baseline desprotegido (:8000), obteve o segredo corporativo no Passo 2; no alvo protegido (:8080), foi 100% bloqueado.",
        WD_ALIGN_PARAGRAPH.JUSTIFY, 0.8, 4
    )
    add_figure(FIG_SOLO, "Figura 3 – Fluxo Operacional do Caso de Uso 1: Agente Solo ReAct", width_cm=13.0)

    add_p(
        "• Nível 2 - Escalação em Enxame (Swarm de 4 Sub-Agentes Paralelos): O agente comandante instancia 4 sub-agentes atacando "
        "simultaneamente múltiplos vetores (Jailbreak, SQLi, Shell Exec, Destructive Code) em ~12ms. Todos foram neutralizados pelo LlamaFirewall "
        "e correlacionados no SIEM Wazuh pela Regra 100210 com severidade crítica 14.",
        WD_ALIGN_PARAGRAPH.JUSTIFY, 0.8, 4
    )
    add_figure(FIG_SWARM, "Figura 4 – Escalação em Enxame (Swarm) e Correlação Temporal no SIEM Wazuh", width_cm=15.5)

    add_p(
        "• Nível 3 - Red Team e Auditoria com CrewAI e Google Gemini Real: Equipe cooperativa operando com gemini-1.5-flash via API Key oficial, "
        "conduzindo ataques semânticos elaborados e emitindo laudo de auditoria técnica defensiva.",
        WD_ALIGN_PARAGRAPH.JUSTIFY, 0.8, 4
    )
    add_figure(FIG_CREW, "Figura 5 – Estrutura da Equipe Red Team CrewAI com Google Gemini Real", width_cm=12.5)

    add_h("4. Analisar os resultados")
    add_p("Aqui você compara os resultados obtidos com os critérios definidos anteriormente.")

    # Tabela de Benchmark no Word
    table = doc.add_table(rows=7, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    headers = ["Critério Avaliado", "Baseline Desprotegido (:8000)", "Alvo Protegido (:8080)", "Veredito Defensivo"]
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = h_text
        hdr_cells[i].paragraphs[0].runs[0].bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.size = Pt(10)
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    bench_rows = [
        ["Taxa de Bloqueio (Agente Solo)", "0.0% (0/5)", "100.0% (5/5 Bloqueados)", "Ataque Neutralizado"],
        ["Exfiltração de Segredo Corporativo", "Vazamento no Passo 2", "Zero Vazamento (Interceptado)", "Confidencialidade Preservada"],
        ["Taxa de Bloqueio (Swarm 4 Agentes)", "0.0% (2 furaram o alvo)", "100.0% (4/4 Sub-Agentes)", "Swarm Contido"],
        ["Alertas Correlacionados SIEM", "0 Alertas (Cego)", "Disparado (Severidade 14 - Crítica)", "Incidente Coordenado"],
        ["Falsos Positivos (Tráfego Legítimo)", "0% (23/23 Permitidos)", "0% (23/23 Homologados)", "Operação Preservada"],
        ["Taxa Global de Mitigação", "0.0%", "100.0%", "Risco Eliminado"]
    ]

    for row_idx, r_data in enumerate(bench_rows, start=1):
        row_cells = table.rows[row_idx].cells
        for col_idx, text_val in enumerate(r_data):
            row_cells[col_idx].text = text_val
            p_cell = row_cells[col_idx].paragraphs[0]
            p_cell.runs[0].font.size = Pt(9.5)
            if row_idx == 6:
                p_cell.runs[0].bold = True
            if col_idx > 0:
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_p("Fonte: Autores (2026). Dados auditados a partir dos logs de telemetria dos contêineres Docker.", WD_ALIGN_PARAGRAPH.CENTER, 0, 10, font_size=9.5)

    add_p(
        "A arquitetura apresentou taxa de detecção e bloqueio de 100.0% no alvo protegido (:8080), com 79 bloqueios registrados no LlamaFirewall "
        "(31 pelo Prompt Guard, 32 pelo Agent Alignment e 16 pelo Code Shield), tempo médio de resposta de 18ms por requisição interceptada, "
        "zero falso positivo em 23 requisições corporativas legítimas e capacidade comprovada de correlacionar campanhas coordenadas de agentes em enxame."
    )

    add_h("Validação Conclusiva das Hipóteses", level=2)
    add_p(
        "Diante dos critérios objetivos estipulados no item 2, a Hipótese H1 (Viabilidade de ferramentas open source) foi plenamente CONFIRMADA: "
        "a utilização integrada do LlamaFirewall, Suricata e Wazuh proveu capacidade adequada e robusta de detecção, bloqueio e resposta a ataques de agentes de IA. "
        "Concomitantemente, a Hipótese H2 (Necessidade de soluções complementares) comprovou-se verdadeira na dimensão arquitetural: "
        "a inspeção isolada de pacotes de rede (Suricata) foi cega à semântica dos ataques, tornando a inclusão de um guardrail semântico L7 e a correlação SIEM "
        "soluções complementares estritamente indispensáveis."
    )

    add_h("Resumo Executivo para Tomada de Decisão", level=2)
    add_p("1. Não expor endpoints de modelos generativos e ferramentas corporativas à rede externa sem gateway reverso guardrail de Camada 7;")
    add_p("2. Confinar ferramentas executadas por agentes em sandboxes sem privilégios de administrador (menor privilégio);")
    add_p("3. Ingerir compulsoriamente os logs dos guardrails em um SIEM corporativo com regras de correlação temporal para contenção de swarms;")
    add_p("4. Manter o sensor de rede Suricata para auditoria forense L3/L7.")

    add_h("Disponibilidade do Código Fonte e Reprodutibilidade")
    add_p("Todo o código da bancada, manifestos Docker, scanners, regras Suricata/Wazuh e agentes ofensivos estão disponíveis publicamente em:")
    add_p("https://github.com/walkowicz19/trabalho-seguranca-pi.git", WD_ALIGN_PARAGRAPH.CENTER, 0, 8, bold=True)

    add_h("Referências")
    refs = [
        "CREWAI. CrewAI Multi-Agent Orchestration Framework: Production-ready agentic workflows. 2024. Disponível em: https://github.com/crewAIInc/crewAI. Acesso em: 10 out. 2026.",
        "META AI. Llama Guard & LlamaFirewall: Open-source safeguards for generative AI models and applications. Meta Platforms, 2024. Disponível em: https://ai.meta.com/research/. Acesso em: 10 out. 2026.",
        "MITRE. MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems). McLean: The MITRE Corporation, 2024. Disponível em: https://atlas.mitre.org/. Acesso em: 11 out. 2026.",
        "NIST. Artificial Intelligence Risk Management Framework (AI RMF 1.0). Gaithersburg: National Institute of Standards and Technology, 2023. DOI: 10.6028/NIST.CSWP.25.",
        "NIST. Security and Privacy Controls for Information Systems and Organizations. NIST Special Publication 800-53, Revision 5. Gaithersburg: National Institute of Standards and Technology, 2020.",
        "OPENAI. O incidente da Hugging Face e os próximos passos. 26 ago. 2026. Disponível em: https://openai.com/pt-BR/index/hugging-face-incident-and-the-road-ahead/. Acesso em: 28 set. 2026.",
        "OWASP. OWASP Top 10 for Large Language Model Applications and Generative AI. Versão 2025. Open Worldwide Application Security Project, 2025. Disponível em: https://owasp.org/www-project-top-10-for-large-language-model-applications/. Acesso em: 08 out. 2026.",
        "RED HAT. O que é open source? 2024. Disponível em: https://www.redhat.com/pt-br/topics/open-source/what-is-open-source. Acesso em: 08 out. 2026.",
        "SALTZER, J. H.; SCHROEDER, M. D. The protection of information in computer systems. Proceedings of the IEEE, v. 63, n. 9, p. 1278-1308, 1975.",
        "SURICATA. Suricata User Guide Release 7.0: Open Source Next Generation Intrusion Detection and Prevention Engine. Open Information Security Foundation (OISF), 2024. Disponível em: https://suricata.io/. Acesso em: 09 out. 2026.",
        "WAZUH. Wazuh Documentation: Open Source Security Platform for Threat Detection, Integrity Monitoring, and Incident Response. Wazuh Inc., 2024. Disponível em: https://documentation.wazuh.com/. Acesso em: 10 out. 2026.",
        "YAO, S. et al. ReAct: Synergizing Reasoning and Acting in Language Models. In: International Conference on Learning Representations (ICLR), 2023. arXiv:2210.03629."
    ]
    for r in refs:
        add_p(r, WD_ALIGN_PARAGRAPH.LEFT, 0, 6, font_size=10.5)

    doc.save(docx_path)
    print(f"[OK] Documento DOCX gerado com sucesso: {docx_path}")
    return docx_path


# =============================================================================
# 2. GERADOR PDF (REPORTLAB - NBR 14724 / 6023)
# =============================================================================
class ABNTCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []
        self.first_textual_page = 3  # Introdução inicia na folha 3 após a Capa e Folha de Rosto

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if self._pageNumber >= self.first_textual_page:
                self.setFont("Arial", 10)
                page_str = str(self._pageNumber)
                self.drawRightString(210 * mm - 20 * mm, 297 * mm - 20 * mm, page_str)
            super().showPage()
        super().save()


def generate_pdf():
    pdf_path = os.path.join(PROJECT_ROOT, "relatorio_tcc_seguranca_pi.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=3.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=3.0 * cm,
        bottomMargin=2.0 * cm
    )

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        'ABNTBody',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        firstLineIndent=1.25 * cm,
        spaceAfter=6
    )

    body_no_indent = ParagraphStyle(
        'ABNTBodyNoIndent',
        parent=body_style,
        firstLineIndent=0,
        spaceAfter=4
    )

    h1_style = ParagraphStyle(
        'ABNTH1',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'ABNTH2',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    cover_center = ParagraphStyle(
        'CoverCenter',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER
    )

    cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=13,
        leading=17,
        alignment=TA_CENTER
    )

    caption_top = ParagraphStyle(
        'CapTop',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    caption_bot = ParagraphStyle(
        'CapBot',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=10
    )

    rosto_nota = ParagraphStyle(
        'RostoNota',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        leftIndent=7.0 * cm,
        spaceBefore=8,
        spaceAfter=8
    )

    ref_style = ParagraphStyle(
        'RefStyle',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10.5,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6
    )

    story = []

    # 1. CAPA
    story.append(Paragraph("CENTRO UNIVERSITÁRIO UNIEURO", cover_center))
    story.append(Paragraph("CURSO DE SISTEMAS DE INFORMAÇÃO", cover_center))
    story.append(Spacer(1, 2.5 * cm))

    autores = (
        "Gabriel Nascimento Feitosa Breguedo<br/>"
        "Ícaro Cardoso da Silva 074042<br/>"
        "Matheus Nery Walkowicz 077651<br/>"
        "Miguel<br/>"
        "Yuri Bacelar de Almeida 076605"
    )
    story.append(Paragraph(autores, cover_center))
    story.append(Spacer(1, 3.2 * cm))

    story.append(Paragraph("Mitigação de Ataques Cibernéticos Automatizados por Agentes de Inteligência Artificial utilizando Ferramentas Open Source - Tema/Título", cover_title))
    story.append(Spacer(1, 5.0 * cm))
    story.append(Paragraph("Brasília - DF<br/>2026", cover_center))
    story.append(PageBreak())

    # 2. FOLHA DE ROSTO
    story.append(Paragraph(autores, cover_center))
    story.append(Spacer(1, 2.8 * cm))
    story.append(Paragraph("Mitigação de Ataques Cibernéticos Automatizados por Agentes de Inteligência Artificial utilizando Ferramentas Open Source", cover_title))
    story.append(Spacer(1, 2.0 * cm))

    nota_rosto = (
        "Trabalho de Conclusão / Relatório de Projeto Integrador apresentado "
        "ao Curso de Sistemas de Informação do Centro Universitário Unieuro "
        "como requisito parcial de avaliação em Segurança da Informação."
    )
    story.append(Paragraph(nota_rosto, rosto_nota))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("<b>Repositório Oficial Git:</b><br/><font color='#f54e00'><u>https://github.com/walkowicz19/trabalho-seguranca-pi.git</u></font>", rosto_nota))

    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph("Brasília - DF<br/>2026", cover_center))
    story.append(PageBreak())

    # 3. TEXTO TEXTUAL (A partir da folha 3)
    story.append(Paragraph("<b>Introdução</b>", h1_style))
    story.append(Paragraph(
        "Agentes autônomos de inteligência artificial podem automatizar ataques cibernéticos, aumentando sua velocidade e escala. "
        "Como exemplo, a OpenAI (2026) relatou um incidente ocorrido em julho de 2026 envolvendo agentes de IA e sistemas da "
        "Hugging Face, evidenciando os riscos associados à atuação autônoma desses sistemas. Nesse cenário, ferramentas open source "
        "podem representar uma alternativa acessível para organizações que precisam detectar, bloquear e responder a ataques semelhantes.",
        body_style
    ))
    story.append(Paragraph("<b>Referência:</b>", ParagraphStyle('RefH', parent=body_no_indent, fontName='Arial-Bold', fontSize=11)))
    story.append(Paragraph(
        "OPENAI. O incidente da Hugging Face e os próximos passos. 26 ago. 2026. Disponível em: https://openai.com/pt-BR/index/hugging-face-incident-and-the-road-ahead/. Acesso em: 28 set. 2026.",
        ParagraphStyle('RefOpenAI', parent=body_no_indent, fontSize=11, spaceAfter=8)
    ))

    story.append(Paragraph("<b>Conceitos</b>", h1_style))
    story.append(Paragraph("<b>Open source:</b> O código-fonte do software open source é projetado para ser acessado abertamente pelo público: todas as pessoas podem vê-lo, modificá-lo e distribuí-lo conforme suas necessidades. Red Hat", body_style))
    story.append(Paragraph("<b>Ataque cibernético:</b> Uma tentativa de obter acesso não autorizado a serviços, recursos ou informações de um sistema, ou uma tentativa de comprometer sua integridade, disponibilidade ou confidencialidade. NIST", body_style))
    story.append(Paragraph("<b>Defesa em Profundidade:</b> Princípio de segurança computacional formulado por Saltzer e Schroeder (1975), no qual múltiplos controles sobrepostos garantem que a eventual falha de um sensor perimétrico não comprometa o ativo protegido.", body_style))
    story.append(Paragraph("<b>Injeção de Prompt e Sequestro de Ferramentas:</b> Conforme catálogo da OWASP (2025), vetores adversariais em que entradas de texto desviam as diretrizes operacionais de um modelo de linguagem, forçando a execução não autorizada de ferramentas corporativas e exfiltração de dados.", body_style))

    story.append(Paragraph("<b>Problema</b>", h1_style))
    story.append(Paragraph("A dificuldade de empresas sem acesso a soluções comerciais avançadas em detectar e bloquear ataques cibernéticos automatizados por agentes de inteligência artificial.", body_style))

    story.append(Paragraph("<b>Hipóteses</b>", h1_style))
    story.append(Paragraph("<b>H1</b> - A utilização integrada de ferramentas open source de segurança pode permitir a detecção e o bloqueio de ataques automatizados realizados por agentes de inteligência artificial.", body_style))
    story.append(Paragraph("<b>H2</b> - Uma arquitetura baseada em ferramentas open source pode proporcionar uma resposta rápida e eficaz a ataques conduzidos por agentes de inteligência artificial, sem depender de soluções comerciais avançadas.", body_style))

    story.append(Paragraph("<b>H1 — Viabilidade de ferramentas open source</b>", h2_style))
    story.append(Paragraph("A utilização integrada de ferramentas open source de segurança pode proporcionar capacidade adequada de detecção, bloqueio e resposta a ataques automatizados realizados por agentes de inteligência artificial, considerando os requisitos de desempenho e eficácia estabelecidos.", body_style))

    story.append(Paragraph("<b>H2 — Necessidade de soluções complementares</b>", h2_style))
    story.append(Paragraph("Uma arquitetura de segurança baseada em ferramentas open source pode apresentar diferentes níveis de desempenho na detecção, no bloqueio e na resposta a ataques conduzidos por agentes de inteligência artificial, podendo demandar soluções complementares para atender aos requisitos de eficácia estabelecidos.", body_style))

    story.append(Paragraph("<b>Objetivo</b>", h1_style))
    story.append(Paragraph("Avaliar a eficácia de ferramentas open source na detecção, bloqueio e resposta a ataques cibernéticos automatizados por agentes de inteligência artificial.", body_style))

    story.append(Paragraph("<b>Objetivos específicos</b>", h2_style))
    objs = [
        "Implementar o LlamaFirewall como mecanismo de proteção contra ações maliciosas de agentes de inteligência artificial.",
        "Configurar o Suricata para identificação de tráfego malicioso associado aos ataques automatizados.",
        "Integrar o Wazuh à arquitetura para monitoramento dos eventos e incidentes de segurança.",
        "Mensurar a eficácia da arquitetura por meio das taxas de detecção, bloqueio, falsos positivos e tempo de resposta.",
        "Comparar os resultados obtidos em ambientes com e sem a arquitetura de proteção."
    ]
    for o in objs:
        story.append(Paragraph(f"• {o}", ParagraphStyle('ObjList', parent=body_style, leftIndent=0.8*cm, firstLineIndent=0, spaceAfter=2)))

    story.append(Paragraph("<b>1. Definir as hipóteses</b>", h1_style))
    story.append(Paragraph("Você apresenta H1 e H2 como hipóteses concorrentes.", body_style))

    story.append(Paragraph("<b>2. Definir os critérios de avaliação</b>", h1_style))
    story.append(Paragraph("Antes dos testes, estabeleça o que significa “adequado”. Por exemplo:", body_style))
    criterios = [
        "taxa de detecção;",
        "taxa de bloqueio;",
        "tempo de resposta;",
        "quantidade de ataques identificados;",
        "falsos positivos;",
        "utilização de recursos;",
        "capacidade de lidar com diferentes padrões de ataque."
    ]
    for c in criterios:
        story.append(Paragraph(f"• {c}", ParagraphStyle('CritList', parent=body_style, leftIndent=0.8*cm, firstLineIndent=0, spaceAfter=2)))
    story.append(Paragraph("Isso é importante porque você não pode chegar ao final e decidir que uma hipótese é “melhor” apenas pela impressão dos resultados.", body_style))

    story.append(Paragraph("<b>3. Realizar os experimentos</b>", h1_style))
    story.append(Paragraph(
        "Você testa a arquitetura open source em cenários controlados de ataques realizados por agentes de IA. "
        "A bancada de testes foi integralmente implementada em contêineres Docker Compose com três sub-redes isoladas "
        "(attacker_net, defense_net e internal_net), integrando a Target API corporativa (:8000), o proxy LlamaFirewall (:8080), "
        "o sensor Suricata NIDS e o SIEM Wazuh.",
        body_style
    ))

    if os.path.exists(FIG_ARQ):
        story.append(KeepTogether([
            Paragraph("<b>Figura 1 – Arquitetura de Defesa em Profundidade com Isolamento de Redes Docker</b>", caption_top),
            RLImage(FIG_ARQ, width=15.5 * cm, height=9.0 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bot)
        ]))

    story.append(Paragraph(
        "Para observabilidade e auditoria analítica dos ensaios em tempo de execução, foi desenvolvido um painel de telemetria SOC "
        "(porta :5000), redesenhado sob as diretrizes do DESIGN.md com paleta editorial quente, hairlines de precisão, "
        "exclusivamente Lucide Icons e terminal com exibição imediata dos logs de auditoria sem corte ou rolagem.",
        body_style
    ))

    if os.path.exists(FIG_DASH):
        story.append(KeepTogether([
            Paragraph("<b>Figura 2 – Interface Atualizada do SOC Dashboard de Telemetria e Defesa Ativa</b>", caption_top),
            RLImage(FIG_DASH, width=15.5 * cm, height=8.8 * cm),
            Paragraph("Fonte: Autores (2026). Interface com scanners reposicionados e telemetria de logs ativa.", caption_bot)
        ]))

    story.append(Paragraph("Os experimentos foram estruturados em três níveis reais de dificuldade:", body_style))
    story.append(Paragraph(
        "• <b>Nível 1 - Agente Solo com Ciclo ReAct (Reasoning and Acting):</b> O agente explora a API sequencialmente, adaptando seus prompts. "
        "No baseline desprotegido (:8000), obteve o segredo corporativo no Passo 2; no alvo protegido (:8080), foi 100% bloqueado.",
        ParagraphStyle('Nivel1', parent=body_style, leftIndent=0.8*cm, firstLineIndent=0)
    ))

    if os.path.exists(FIG_SOLO):
        story.append(KeepTogether([
            Paragraph("<b>Figura 3 – Fluxo Operacional do Caso de Uso 1: Agente Solo ReAct</b>", caption_top),
            RLImage(FIG_SOLO, width=13.0 * cm, height=12.6 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bot)
        ]))

    story.append(Paragraph(
        "• <b>Nível 2 - Escalação em Enxame (Swarm de 4 Sub-Agentes Paralelos):</b> O agente comandante instancia 4 sub-agentes atacando "
        "simultaneamente múltiplos vetores (Jailbreak, SQLi, Shell Exec, Destructive Code) em ~12ms. Todos foram neutralizados pelo LlamaFirewall "
        "e correlacionados no SIEM Wazuh pela Regra 100210 com severidade crítica 14.",
        ParagraphStyle('Nivel2', parent=body_style, leftIndent=0.8*cm, firstLineIndent=0)
    ))

    if os.path.exists(FIG_SWARM):
        story.append(KeepTogether([
            Paragraph("<b>Figura 4 – Escalação em Enxame (Swarm) e Correlação Temporal no SIEM Wazuh</b>", caption_top),
            RLImage(FIG_SWARM, width=15.5 * cm, height=3.4 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bot)
        ]))

    story.append(Paragraph(
        "• <b>Nível 3 - Red Team e Auditoria com CrewAI e Google Gemini Real:</b> Equipe cooperativa operando com gemini-1.5-flash via API Key oficial, "
        "conduzindo ataques semânticos elaborados e emitindo laudo de auditoria técnica defensiva.",
        ParagraphStyle('Nivel3', parent=body_style, leftIndent=0.8*cm, firstLineIndent=0)
    ))

    if os.path.exists(FIG_CREW):
        story.append(KeepTogether([
            Paragraph("<b>Figura 5 – Estrutura da Equipe Red Team CrewAI com Google Gemini Real</b>", caption_top),
            RLImage(FIG_CREW, width=12.5 * cm, height=13.7 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bot)
        ]))

    story.append(Paragraph("<b>4. Analisar os resultados</b>", h1_style))
    story.append(Paragraph("Aqui você compara os resultados obtidos com os critérios definidos anteriormente.", body_style))

    # Tabela de Benchmark no ReportLab
    table_data = [
        [
            Paragraph("<b>Critério Avaliado</b>", caption_top),
            Paragraph("<b>Baseline Desprotegido (:8000)</b>", caption_top),
            Paragraph("<b>Alvo Protegido (:8080)</b>", caption_top),
            Paragraph("<b>Veredito Defensivo</b>", caption_top)
        ],
        [
            Paragraph("Taxa de Bloqueio (Agente Solo)", body_no_indent),
            Paragraph("0.0% (0/5)", body_no_indent),
            Paragraph("100.0% (5/5 Bloqueados)", body_no_indent),
            Paragraph("Ataque Neutralizado", body_no_indent)
        ],
        [
            Paragraph("Exfiltração de Segredo Corporativo", body_no_indent),
            Paragraph("Vazamento no Passo 2", body_no_indent),
            Paragraph("Zero Vazamento (Interceptado)", body_no_indent),
            Paragraph("Confidencialidade Preservada", body_no_indent)
        ],
        [
            Paragraph("Taxa de Bloqueio (Swarm 4 Agentes)", body_no_indent),
            Paragraph("0.0% (2 furaram o alvo)", body_no_indent),
            Paragraph("100.0% (4/4 Sub-Agentes)", body_no_indent),
            Paragraph("Swarm Contido", body_no_indent)
        ],
        [
            Paragraph("Alertas Correlacionados SIEM", body_no_indent),
            Paragraph("0 Alertas (Cego)", body_no_indent),
            Paragraph("Disparado (Severidade 14 - Crítica)", body_no_indent),
            Paragraph("Incidente Coordenado", body_no_indent)
        ],
        [
            Paragraph("Falsos Positivos (Tráfego Legítimo)", body_no_indent),
            Paragraph("0% (23/23 Permitidos)", body_no_indent),
            Paragraph("0% (23/23 Homologados)", body_no_indent),
            Paragraph("Operação Preservada", body_no_indent)
        ],
        [
            Paragraph("<b>Taxa Global de Mitigação</b>", body_no_indent),
            Paragraph("<b>0.0%</b>", body_no_indent),
            Paragraph("<b>100.0%</b>", body_no_indent),
            Paragraph("<b>Risco Eliminado</b>", body_no_indent)
        ]
    ]

    t_bench = RLTable(table_data, colWidths=[4.2 * cm, 3.8 * cm, 4.5 * cm, 3.5 * cm])
    t_bench.setStyle(RLTableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0eee6')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfcdc4')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fafaf7')),
    ]))

    story.append(KeepTogether([
        Paragraph("<b>Tabela 1 – Benchmark Comparativo Quantitativo entre Baseline Desprotegido e Alvo Protegido</b>", caption_top),
        t_bench,
        Paragraph("Fonte: Autores (2026). Dados auditados a partir dos logs de telemetria dos contêineres Docker.", caption_bot)
    ]))

    story.append(Paragraph(
        "A arquitetura apresentou taxa de detecção e bloqueio de 100.0% no alvo protegido (:8080), com 79 bloqueios registrados no LlamaFirewall "
        "(31 pelo Prompt Guard, 32 pelo Agent Alignment e 16 pelo Code Shield), tempo médio de resposta de 18ms por requisição interceptada, "
        "zero falso positivo em 23 requisições corporativas legítimas e capacidade comprovada de correlacionar campanhas coordenadas de agentes em enxame.",
        body_style
    ))

    story.append(Paragraph("<b>Validação Conclusiva das Hipóteses</b>", h2_style))
    story.append(Paragraph(
        "Diante dos critérios objetivos estipulados no item 2, a Hipótese H1 (Viabilidade de ferramentas open source) foi plenamente CONFIRMADA: "
        "a utilização integrada do LlamaFirewall, Suricata e Wazuh proveu capacidade adequada e robusta de detecção, bloqueio e resposta a ataques de agentes de IA. "
        "Concomitantemente, a Hipótese H2 (Necessidade de soluções complementares) comprovou-se verdadeira na dimensão arquitetural: "
        "a inspeção isolada de pacotes de rede (Suricata) foi cega à semântica dos ataques, tornando a inclusão de um guardrail semântico L7 e a correlação SIEM "
        "soluções complementares estritamente indispensáveis.",
        body_style
    ))

    story.append(Paragraph("<b>Resumo Executivo para Tomada de Decisão</b>", h2_style))
    story.append(Paragraph("1. Não expor endpoints de modelos generativos e ferramentas corporativas à rede externa sem gateway reverso guardrail de Camada 7;", body_style))
    story.append(Paragraph("2. Confinar ferramentas executadas por agentes em sandboxes sem privilégios de administrador (menor privilégio);", body_style))
    story.append(Paragraph("3. Ingerir compulsoriamente os logs dos guardrails em um SIEM corporativo com regras de correlação temporal para contenção de swarms;", body_style))
    story.append(Paragraph("4. Manter o sensor de rede Suricata para auditoria forense L3/L7.", body_style))

    story.append(Paragraph("<b>Disponibilidade do Código Fonte e Reprodutibilidade</b>", h1_style))
    story.append(Paragraph("Todo o código da bancada, manifestos Docker, scanners, regras Suricata/Wazuh e agentes ofensivos estão disponíveis publicamente em:", body_style))
    story.append(Paragraph("<b><u>https://github.com/walkowicz19/trabalho-seguranca-pi.git</u></b>", ParagraphStyle('GitLnk', parent=body_no_indent, alignment=TA_CENTER, fontName='Arial-Bold', textColor=colors.HexColor('#f54e00'), spaceBefore=4, spaceAfter=8)))

    story.append(Paragraph("<b>Referências</b>", h1_style))
    refs = [
        "CREWAI. <b>CrewAI Multi-Agent Orchestration Framework</b>: Production-ready agentic workflows. 2024. Disponível em: &lt;https://github.com/crewAIInc/crewAI&gt;. Acesso em: 10 out. 2026.",
        "META AI. <b>Llama Guard & LlamaFirewall</b>: Open-source safeguards for generative AI models and applications. Meta Platforms, 2024. Disponível em: &lt;https://ai.meta.com/research/&gt;. Acesso em: 10 out. 2026.",
        "MITRE. <b>MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)</b>. McLean: The MITRE Corporation, 2024. Disponível em: &lt;https://atlas.mitre.org/&gt;. Acesso em: 11 out. 2026.",
        "NIST. <b>Artificial Intelligence Risk Management Framework (AI RMF 1.0)</b>. Gaithersburg: National Institute of Standards and Technology, 2023. DOI: 10.6028/NIST.CSWP.25.",
        "NIST. <b>Security and Privacy Controls for Information Systems and Organizations</b>. NIST Special Publication 800-53, Revision 5. Gaithersburg: National Institute of Standards and Technology, 2020.",
        "OPENAI. <b>O incidente da Hugging Face e os próximos passos</b>. 26 ago. 2026. Disponível em: &lt;https://openai.com/pt-BR/index/hugging-face-incident-and-the-road-ahead/&gt;. Acesso em: 28 set. 2026.",
        "OWASP. <b>OWASP Top 10 for Large Language Model Applications and Generative AI</b>. Versão 2025. Open Worldwide Application Security Project, 2025. Disponível em: &lt;https://owasp.org/www-project-top-10-for-large-language-model-applications/&gt;. Acesso em: 08 out. 2026.",
        "RED HAT. <b>O que é open source?</b> 2024. Disponível em: &lt;https://www.redhat.com/pt-br/topics/open-source/what-is-open-source&gt;. Acesso em: 08 out. 2026.",
        "SALTZER, J. H.; SCHROEDER, M. D. The protection of information in computer systems. <b>Proceedings of the IEEE</b>, v. 63, n. 9, p. 1278-1308, 1975.",
        "SURICATA. <b>Suricata User Guide Release 7.0</b>: Open Source Next Generation Intrusion Detection and Prevention Engine. Open Information Security Foundation (OISF), 2024. Disponível em: &lt;https://suricata.io/&gt;. Acesso em: 09 out. 2026.",
        "WAZUH. <b>Wazuh Documentation</b>: Open Source Security Platform for Threat Detection, Integrity Monitoring, and Incident Response. Wazuh Inc., 2024. Disponível em: &lt;https://documentation.wazuh.com/&gt;. Acesso em: 10 out. 2026.",
        "YAO, S. et al. ReAct: Synergizing Reasoning and Acting in Language Models. In: <b>International Conference on Learning Representations (ICLR)</b>, 2023. arXiv:2210.03629."
    ]
    for r in refs:
        story.append(Paragraph(r, ref_style))

    doc.build(story, canvasmaker=ABNTCanvas)
    print(f"[OK] Documento PDF gerado com sucesso: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_docx()
    generate_pdf()
