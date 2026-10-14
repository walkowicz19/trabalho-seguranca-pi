#!/usr/bin/env python3
"""
Gerador de Relatório Acadêmico / TCC em formato ABNT (PDF)
Tema: Arquitetura de Defesa Ativa e Mitigação de Ataques de IA com Ferramentas Open Source
Centro Universitário Unieuro - Curso de Sistemas de Informação
Normas: NBR 14724 (Estrutura e Formatação), NBR 6028 (Resumo), NBR 6027 (Sumário),
        NBR 10520 (Citações Diretas e Indiretas), NBR 6023 (Referências Bibliográficas).
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
import pypdf

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Registro oficial de fontes TrueType True ABNT (Arial)
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic', 'C:/Windows/Fonts/arialbi.ttf'))
registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-BoldItalic')

class ABNTCanvas(canvas.Canvas):
    """
    Canvas ABNT NBR 14724:
    - Pré-textuais contadas, mas sem numeração impressa.
    - Numeração inicia em algarismos arábicos a partir do primeiro capítulo textual (1 INTRODUÇÃO).
    - Canto superior direito: 20mm da borda direita e 20mm da borda superior.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []
        self.first_textual_page = 6

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if self._pageNumber >= self.first_textual_page:
                self.setFont("Arial", 10)
                # 20mm da borda direita, 20mm da borda superior
                page_str = str(self._pageNumber)
                self.drawRightString(210 * mm - 20 * mm, 297 * mm - 20 * mm, page_str)
            super().showPage()
        super().save()


def build_story(page_map=None):
    if page_map is None:
        page_map = {
            "intro": 6,
            "hipot": 7,
            "teoria": 8,
            "metod": 9,
            "result": 11,
            "resumo_exec": 16,
            "codigo": 16,
            "concl": 17,
            "refs": 18
        }

    styles = getSampleStyleSheet()

    # Estilos ABNT
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

    quote_long_style = ParagraphStyle(
        'ABNTQuoteLong',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        leftIndent=4.0 * cm,
        spaceBefore=8,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'ABNTH1',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'ABNTH2',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    cover_inst_style = ParagraphStyle(
        'CoverInst',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER
    )

    cover_author_style = ParagraphStyle(
        'CoverAuthor',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER
    )

    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=13,
        leading=17,
        alignment=TA_CENTER
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER
    )

    cover_local_style = ParagraphStyle(
        'CoverLocal',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER
    )

    rosto_natureza_style = ParagraphStyle(
        'RostoNatureza',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        leftIndent=7.0 * cm,
        spaceBefore=8,
        spaceAfter=8
    )

    caption_top_style = ParagraphStyle(
        'ABNTCaptionTop',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    caption_bottom_style = ParagraphStyle(
        'ABNTCaptionBottom',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=10
    )

    ref_style = ParagraphStyle(
        'ABNTRef',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=8
    )

    story = []

    # =========================================================================
    # 1. CAPA (NBR 14724)
    # =========================================================================
    story.append(Paragraph("CENTRO UNIVERSITÁRIO UNIEURO", cover_inst_style))
    story.append(Paragraph("CURSO DE BACHARELADO EM SISTEMAS DE INFORMAÇÃO", cover_inst_style))
    story.append(Paragraph("DISCIPLINA DE SEGURANÇA DA INFORMAÇÃO / PROJETO INTEGRADOR", cover_inst_style))
    story.append(Spacer(1, 2.8 * cm))

    autores = (
        "GABRIEL NASCIMENTO FEITOSA BREGUEDO<br/>"
        "ÍCARO CARDOSO DA SILVA<br/>"
        "MATHEUS NERY WALKOWICZ<br/>"
        "MIGUEL<br/>"
        "YURI BACELAR DE ALMEIDA"
    )
    story.append(Paragraph(autores, cover_author_style))
    story.append(Spacer(1, 3.2 * cm))

    story.append(Paragraph("ARQUITETURA DE DEFESA ATIVA E MITIGAÇÃO DE ATAQUES CIBERNÉTICOS AUTÔNOMOS CONDUZIDOS POR AGENTES DE IA COM FERRAMENTAS OPEN SOURCE", cover_title_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Avaliação Experimental em Ambiente Conteinerizado com LlamaFirewall, Suricata NIDS e SIEM Wazuh", cover_subtitle_style))

    story.append(Spacer(1, 4.0 * cm))
    story.append(Paragraph("BRASÍLIA - DF<br/>2026", cover_local_style))
    story.append(PageBreak())

    # =========================================================================
    # 2. FOLHA DE ROSTO (NBR 14724)
    # =========================================================================
    story.append(Paragraph(autores, cover_author_style))
    story.append(Spacer(1, 2.5 * cm))

    story.append(Paragraph("ARQUITETURA DE DEFESA ATIVA E MITIGAÇÃO DE ATAQUES CIBERNÉTICOS AUTÔNOMOS CONDUZIDOS POR AGENTES DE IA COM FERRAMENTAS OPEN SOURCE", cover_title_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Avaliação Experimental em Ambiente Conteinerizado com LlamaFirewall, Suricata NIDS e SIEM Wazuh", cover_subtitle_style))
    story.append(Spacer(1, 1.8 * cm))

    nota_rosto = (
        "Trabalho de Conclusão / Relatório Técnico-Científico apresentado "
        "ao Curso de Sistemas de Informação do Centro Universitário Unieuro "
        "como requisito de avaliação parcial na área de Segurança da Informação "
        "e Inteligência Artificial Aplicada."
    )
    story.append(Paragraph(nota_rosto, rosto_natureza_style))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("<b>Repositório Oficial no GitHub:</b><br/><font color='#f54e00'><u>https://github.com/walkowicz19/trabalho-seguranca-pi.git</u></font>", rosto_natureza_style))

    story.append(Spacer(1, 3.0 * cm))
    story.append(Paragraph("BRASÍLIA - DF<br/>2026", cover_local_style))
    story.append(PageBreak())

    # =========================================================================
    # 3. RESUMO (NBR 6028)
    # =========================================================================
    story.append(Paragraph("<b>RESUMO</b>", h1_style))
    resumo_text = (
        "A crescente proliferação de modelos de linguagem de grande escala (LLMs) operando como agentes autônomos dotados "
        "de raciocínio iterativo e capacidade de execução de ferramentas corporativas (paradigmas ReAct e Swarm) transformou "
        "o cenário contemporâneo de ameaças cibernéticas. Defesas tradicionais de rede baseadas em assinaturas de pacotes "
        "(L3/L4) mostram-se cegas à semântica maliciosa transportada em cargas úteis de texto estruturado. Este trabalho projeta, "
        "implementa e avalia empiricamente uma arquitetura de defesa ativa em profundidade fundamentada estritamente em soluções de "
        "código aberto: o gateway de aplicação LlamaFirewall (camada 7 provido de scanners de Prompt Guard, Agent Alignment e "
        "Code Shield), o sistema de detecção de intrusão de rede Suricata NIDS (L3/L7) e a plataforma SIEM Wazuh para "
        "correlação analítica em tempo real. A validação experimental foi conduzida em uma bancada conteinerizada em Docker, "
        "confrontando um baseline desprotegido (porta 8000) com o alvo mitigado por guardrails (porta 8080) sob três classes "
        "de ofensivas reais: agente solo autônomo, enxame coordenado com quatro sub-agentes simultâneos e equipe ofensiva Red "
        "Team CrewAI orquestrada com o modelo Google Gemini. Os resultados demonstraram que o alvo desprotegido foi integralmente "
        "comprometido em 100% dos vetores avaliados, com exfiltração imediata de tokens corporativos e execução remota de código. "
        "Em contrapartida, o alvo protegido alcançou taxa de neutralização de 100% em injeções diretas e jailbreaks, sem registrar "
        "falsos positivos no tráfego corporativo legítimo homologado. Ademais, a correlação SIEM demonstrou ser estritamente "
        "indispensável para identificar campanhas distribuídas de agentes em enxame (disparando alertas correlacionados de severidade "
        "crítica 14). Conclui-se que a composição de guardrails semânticos e sensores de correlação open source atinge paridade "
        "operacional com soluções comerciais proprietárias de alto custo, assegurando resiliência cibernética contra agentes adversariais de IA."
    )
    story.append(Paragraph(resumo_text, body_style))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("<b>Palavras-chave:</b> Segurança em Inteligência Artificial. Defesa em Profundidade. Agentes Autônomos. LlamaFirewall. Suricata NIDS. SIEM Wazuh. ABNT.", body_no_indent))
    story.append(PageBreak())

    # =========================================================================
    # 4. ABSTRACT
    # =========================================================================
    story.append(Paragraph("<b>ABSTRACT</b>", h1_style))
    abstract_text = (
        "The increasing adoption of Large Language Models (LLMs) operating as autonomous agents capable of iterative "
        "reasoning and corporate tool execution (ReAct and Swarm paradigms) has fundamentally reshaped the cyber threat "
        "landscape. Conventional signature-based network intrusion detection systems (L3/L4) remain blind to semantic payloads "
        "embedded within legitimate application traffic. This work designs, deploys, and experimentally validates a defense-in-depth "
        "active architecture built strictly on open-source technologies: the LlamaFirewall application gateway (Layer 7 guardrail "
        "comprising Prompt Guard, Agent Alignment, and Code Shield scanners), Suricata NIDS (L3/L7), and the Wazuh SIEM platform "
        "for real-time event correlation. The experimental testbed was containerized using Docker, comparing an unprotected baseline "
        "endpoint (port 8000) against a protected gateway (port 8080) under three real attack scenarios: an autonomous solo ReAct "
        "agent, a coordinated swarm consisting of four concurrent sub-agents, and a collaborative CrewAI Red Team powered by Google "
        "Gemini. Experimental findings revealed that the unprotected target suffered a 100% compromise rate across all attack vectors, "
        "resulting in immediate token exfiltration and remote code execution. Conversely, the protected architecture achieved a 100% "
        "mitigation rate against direct prompt injections and evasive jailbreaks, with zero false positives on legitimate corporate traffic. "
        "Furthermore, SIEM event correlation proved essential in detecting distributed swarm campaigns (triggering Critical Severity 14 "
        "alerts). It is concluded that combining semantic guardrails with open-source multi-layer sensors achieves defensive parity with "
        "commercial high-cost solutions, providing robust cyber resilience against adversarial AI agents."
    )
    story.append(Paragraph(abstract_text, body_style))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("<b>Keywords:</b> Artificial Intelligence Security. Defense-in-Depth. Autonomous Agents. LlamaFirewall. Suricata NIDS. Wazuh SIEM. ABNT Standard.", body_no_indent))
    story.append(PageBreak())

    # =========================================================================
    # 5. SUMÁRIO (NBR 6027)
    # =========================================================================
    story.append(Paragraph("<b>SUMÁRIO</b>", h1_style))
    sumario_data = [
        [Paragraph("<b>1 INTRODUÇÃO</b>", body_no_indent), Paragraph(f"<b>{page_map['intro']}</b>", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.1 Contextualização e Problema de Pesquisa", body_no_indent), Paragraph(f"{page_map['intro']}", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.2 Objetivos Gerais e Específicos", body_no_indent), Paragraph(f"{page_map['intro']}", body_no_indent)],
        [Paragraph("<b>2 HIPÓTESES DE PESQUISA</b>", body_no_indent), Paragraph(f"<b>{page_map['hipot']}</b>", body_no_indent)],
        [Paragraph("<b>3 FUNDAMENTAÇÃO TEÓRICA E CITAÇÕES FORMAIS</b>", body_no_indent), Paragraph(f"<b>{page_map['teoria']}</b>", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.1 Vulnerabilidades em LLMs (OWASP Top 10 for LLMs 2025)", body_no_indent), Paragraph(f"{page_map['teoria']}", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.2 Governança e Risco de IA (NIST AI RMF e SP 800-53)", body_no_indent), Paragraph(f"{page_map['teoria']}", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.3 O Paradigma Ofensivo dos Agentes Autônomos (ReAct e Swarms)", body_no_indent), Paragraph(f"{page_map['teoria']}", body_no_indent)],
        [Paragraph("<b>4 METODOLOGIA E ARQUITETURA EXPERIMENTAL DOCKER</b>", body_no_indent), Paragraph(f"<b>{page_map['metod']}</b>", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.1 Topologia de Redes e Isolamento de Perímetro", body_no_indent), Paragraph(f"{page_map['metod']}", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Scanners Especializados do Guardrail LlamaFirewall", body_no_indent), Paragraph(f"{page_map['metod']}", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.3 Painel de Telemetria SOC em Tempo Real (Interface Redesenhada)", body_no_indent), Paragraph(f"{page_map['metod']}", body_no_indent)],
        [Paragraph("<b>5 RESULTADOS EMPÍRICOS E ANÁLISE COMPARATIVA</b>", body_no_indent), Paragraph(f"<b>{page_map['result']}</b>", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.1 Tabela Consolidada de Benchmark Experimental", body_no_indent), Paragraph(f"{page_map['result']}", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Análise dos Três Casos de Uso Reais", body_no_indent), Paragraph(f"{page_map['result']}", body_no_indent)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.3 Avaliação e Validação das Hipóteses", body_no_indent), Paragraph(f"{page_map['result']}", body_no_indent)],
        [Paragraph("<b>6 RESUMO EXECUTIVO E RECOMENDAÇÕES OPERACIONAIS</b>", body_no_indent), Paragraph(f"<b>{page_map['resumo_exec']}</b>", body_no_indent)],
        [Paragraph("<b>7 DISPONIBILIDADE DO CÓDIGO FONTE E REPRODUTIBILIDADE</b>", body_no_indent), Paragraph(f"<b>{page_map['codigo']}</b>", body_no_indent)],
        [Paragraph("<b>8 CONSIDERAÇÕES FINAIS</b>", body_no_indent), Paragraph(f"<b>{page_map['concl']}</b>", body_no_indent)],
        [Paragraph("<b>REFERÊNCIAS</b>", body_no_indent), Paragraph(f"<b>{page_map['refs']}</b>", body_no_indent)],
    ]
    t_sumario = Table(sumario_data, colWidths=[14.5 * cm, 1.5 * cm])
    t_sumario.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t_sumario)
    story.append(PageBreak())

    # =========================================================================
    # CAPÍTULO 1 - INTRODUÇÃO (Página 6)
    # =========================================================================
    story.append(Paragraph("<b>1 INTRODUÇÃO</b>", h1_style))
    story.append(Paragraph(
        "A evolução recente dos Modelos de Linguagem de Grande Escala (<i>Large Language Models</i> - LLMs) viabilizou a transição "
        "de sistemas passivos de geração de texto para arquiteturas operacionais de agentes autônomos. Tais entidades computacionais "
        "não apenas processam solicitações em linguagem natural, mas executam ciclos contínuos de raciocínio, planejamento e invocação "
        "de ferramentas externas (<i>tool use</i>), interagindo diretamente com interfaces de programação de aplicações (APIs), bancos "
        "de dados corporativos e subsistemas de execução de código.",
        body_style
    ))
    story.append(Paragraph(
        "Essa autonomia operacional, embora revolucionária para a produtividade corporativa, expande exponencialmente a superfície "
        "de ataque. As arquiteturas convencionais de segurança da informação — consolidadas sob inspeções de rede em Camadas 3 e 4 "
        "(como <i>firewalls</i> de pacotes e sensores NIDS tradicionais) — fundamentam-se na detecção de anomalias volumétricas ou "
        "assinaturas de <i>exploits</i> binários pré-catalogados. Diante de requisições que trafegam em HTTP(S) encapsulando comandos "
        "semânticos persuasivos (<i>jailbreaks</i>, injeções de prompt e manipulação contextual de ferramentas), os controles "
        "periféricos mostram-se integralmente cegos, incapazes de discernir comandos corporativos legítimos de manipulações adversariais.",
        body_style
    ))

    story.append(Paragraph("<b>1.1 Contextualização e Problema de Pesquisa</b>", h2_style))
    story.append(Paragraph(
        "A ausência de mecanismos de inspeção semântica em Camada 7 posicionados como barreira intermediária entre a rede e as "
        "APIs corporativas de LLM viabiliza o comprometimento integral de ativos organizacionais por agentes autônomos ofensivos. "
        "Quando um agente explora com êxito vulnerabilidades semânticas, ele pode forçar o modelo de linguagem corporativo a evocar "
        "ferramentas privilegiadas, consultar tabelas sigilosas via injeção de comandos SQL, executar instruções no sistema "
        "operacional hospedeiro e exfiltrar dados sensíveis de credenciamento. Surge, portanto, a questão central deste trabalho: "
        "<i>Em que medida uma arquitetura de defesa ativa em profundidade, composta exclusivamente por soluções abertas "
        "(LlamaFirewall, Suricata NIDS e Wazuh SIEM), é capaz de identificar e neutralizar ataques automatizados de agentes "
        "autônomos individuais e em enxame sem degradar a operação legítima corporativa?</i>",
        body_style
    ))

    story.append(Paragraph("<b>1.2 Objetivos Gerais e Específicos</b>", h2_style))
    story.append(Paragraph(
        "O <b>objetivo geral</b> deste trabalho consiste em projetar, homologar e avaliar experimentalmente uma arquitetura de "
        "defesa cibernética multicamada de código aberto voltada à mitigação de ameaças perpetradas por agentes de IA autônomos.",
        body_style
    ))
    story.append(Paragraph("Constituem <b>objetivos específicos</b> desta investigação acadêmica:", body_style))
    obj_items = [
        "a) Estruturar uma bancada de testes conteinerizada e reprodutível em Docker com isolamento estrito de sub-redes;",
        "b) Desenvolver agentes ofensivos autônomos reais operando sob o paradigma ReAct (Reasoning and Acting) e orquestrações avançadas em enxame (Swarm e CrewAI);",
        "c) Implementar um gateway de aplicação reversa (LlamaFirewall) provido de múltiplos scanners semânticos em tempo de execução;",
        "d) Avaliar a suficiência do Suricata NIDS e a indispensabilidade das regras de correlação SIEM no Wazuh;",
        "e) Desenvolver um painel passivo de telemetria SOC em tempo real aderente a princípios profissionais de usabilidade e visualização analítica."
    ]
    for it in obj_items:
        story.append(Paragraph(f"• {it}", ParagraphStyle('ObjItem', parent=body_style, leftIndent=1.0*cm, firstLineIndent=0, spaceAfter=2)))

    # =========================================================================
    # CAPÍTULO 2 - HIPÓTESES DE PESQUISA
    # =========================================================================
    story.append(Paragraph("<b>2 HIPÓTESES DE PESQUISA</b>", h1_style))
    story.append(Paragraph(
        "Com base na literatura contemporânea de segurança ofensiva e defensiva para inteligência artificial, formulam-se "
        "duas hipóteses centrais submetidas ao crivo experimental deste estudo:",
        body_style
    ))
    story.append(Paragraph(
        "<b>Hipótese 1 (H1) – Eficácia e Resiliência do Guardrail Semântico de Camada 7:</b> "
        "<i>A introdução de um proxy reverso guardrail de Camada 7 (LlamaFirewall), provido de analisadores semânticos "
        "especializados (Prompt Guard, Agent Alignment e Code Shield), provê uma taxa de mitigação igual ou superior a 95% "
        "contra ataques de injeção de prompt direta, desvios éticos (jailbreaks) e sequestro de ferramentas corporativas "
        "conduzidos por agentes autônomos, mantendo taxa nula de falsos positivos sobre requisições empresariais homologadas.</i>",
        body_style
    ))
    story.append(Paragraph(
        "<b>Hipótese 2 (H2) – Insuficiência da Inspeção L3/L4 Isolada e Indispensabilidade da Correlação SIEM:</b> "
        "<i>A inspeção tradicional de tráfego de rede via NIDS (Suricata) em Camadas 3 e 4 é fundamentalmente incapaz "
        "de barrar manipulações semânticas de LLMs operando sobre payloads de texto legítimo; contudo, quando integrada a "
        "um sistema de gerenciamento e correlação de eventos de segurança (SIEM Wazuh), a telemetria multi-camada torna-se "
        "indispensável para detectar, agregar temporalmente e classificar ofensivas coordenadas distribuídas em enxame (swarms).</i>",
        body_style
    ))

    # =========================================================================
    # CAPÍTULO 3 - FUNDAMENTAÇÃO TEÓRICA E CITAÇÕES FORMAIS
    # =========================================================================
    story.append(Paragraph("<b>3 FUNDAMENTAÇÃO TEÓRICA E CITAÇÕES FORMAIS</b>", h1_style))
    story.append(Paragraph(
        "A fundamentação deste trabalho ancora-se nas taxonomias de segurança estabelecidas por órgãos normativos internacionais, "
        "destacando-se o <i>Open Worldwide Application Security Project</i> (OWASP), o <i>National Institute of Standards and "
        "Technology</i> (NIST) e a matriz de ameaças <i>MITRE ATLAS</i>.",
        body_style
    ))

    story.append(Paragraph("<b>3.1 Taxonomia de Vulnerabilidades em LLMs (OWASP Top 10 for LLMs 2025)</b>", h2_style))
    story.append(Paragraph(
        "A fundação OWASP (2025) cataloga as principais vulnerabilidades que emergem da integração corporativa de modelos de "
        "linguagem. Entre os riscos mais críticos sobressaem-se a Injeção de Prompt (LLM01), a Divulgação de Informações Sensíveis "
        "(LLM02) e o Sequestro de Ferramentas / Invocação Insegura de Plugins (LLM07). Conforme estabelece a OWASP:",
        body_style
    ))

    citacao_owasp = (
        "“A injeção de prompt ocorre quando a entrada de um usuário malicioso manipula a operação pretendida do modelo de linguagem. "
        "Isso permite que invasores ignorem restrições de segurança do sistema, executem chamadas a ferramentas com privilégios não "
        "autorizados e acessem dados sensíveis mantidos no contexto do aplicativo. As injeções podem ser diretas (quando o atacante "
        "interage diretamente com o endpoint) ou indiretas (quando o modelo consome dados externos comprometidos).” (OWASP, 2025, p. 4)."
    )
    story.append(Paragraph(citacao_owasp, quote_long_style))

    story.append(Paragraph(
        "A mitigação de tais vetores exige mecanismos de filtragem semântica operando em linha (*in-line*), capazes de inspecionar "
        "as entradas antes de seu repasse à inferência generativa, bem como auditar os comandos gerados antes de sua execução real.",
        body_style
    ))

    story.append(Paragraph("<b>3.2 Governança e Risco de IA (NIST AI RMF e SP 800-53)</b>", h2_style))
    story.append(Paragraph(
        "O NIST (2023), por meio do <i>Artificial Intelligence Risk Management Framework</i> (AI RMF 1.0), preconiza que a segurança "
        "em sistemas de aprendizado de máquina demanda uma abordagem multidisciplinar dividida em quatro funções essenciais: "
        "<i>Govern</i> (Governar), <i>Map</i> (Mapear), <i>Measure</i> (Medir) e <i>Manage</i> (Gerenciar). Complementarmente, a "
        "publicação especial NIST SP 800-53 Rev. 5 reitera a necessidade do princípio da Defesa em Profundidade "
        "(<i>Defense-in-Depth</i>), originado na obra seminal de Saltzer e Schroeder (1975), no qual múltiplos controles sobrepostos "
        "devem garantir que a falha de um perímetro isolado não resulte no colapso sistêmico do ativo protegido.",
        body_style
    ))

    story.append(Paragraph("<b>3.3 O Paradigma Ofensivo dos Agentes Autônomos (ReAct e Swarms)</b>", h2_style))
    story.append(Paragraph(
        "A capacidade adaptativa de ataques cibernéticos modernos foi substancialmente ampliada pela formalização do paradigma "
        "ReAct por Yao et al. (2023). Nessa abordagem, o agente de IA intercala passos de reflexão deliberada (*Thoughts*) com "
        "ações concretas (*Actions*), inspecionando as respostas do ambiente (*Observations*) para reorientar sua estratégia em "
        "caso de falha. De forma análoga, arquiteturas em enxame (*swarms*) introduzem paralelismo ofensivo, permitindo que sub-agentes "
        "especializados executem simultaneamente sondagens sobre vetores distintos (ex.: injeções de SQL, leitura de arquivos e bypass "
        "de autenticação), sobrecarregando a capacidade de resposta defensiva não automatizada.",
        body_style
    ))

    # =========================================================================
    # CAPÍTULO 4 - METODOLOGIA E ARQUITETURA EXPERIMENTAL DOCKER
    # =========================================================================
    story.append(Paragraph("<b>4 METODOLOGIA E ARQUITETURA EXPERIMENTAL DOCKER</b>", h1_style))
    story.append(Paragraph(
        "Para garantir o rigor científico, a reprodutibilidade integral dos ensaios e a observabilidade forense, concebeu-se uma bancada "
        "experimental conteinerizada por meio da orquestração Docker Compose. A infraestrutura física hospedeira opera com arquitetura "
        "isolada, impedindo vazamento de tráfego para redes públicas e segmentando a comunicação em sub-redes virtuais dedicadas.",
        body_style
    ))

    story.append(Paragraph("<b>4.1 Topologia de Redes e Isolamento de Perímetro</b>", h2_style))
    story.append(Paragraph(
        "A bancada de testes foi particionada em três redes lógicas independentes (<i>bridge networks</i>):",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>attacker_net:</b> Sub-rede onde residem os agentes ofensivos e o ponto de entrada externo do gateway LlamaFirewall;<br/>"
        "2. <b>defense_net:</b> Sub-rede de monitoramento onde atuam o sensor de pacotes Suricata NIDS e os agentes de auditoria;<br/>"
        "3. <b>internal_net:</b> Sub-rede privada interna onde reside o ativo corporativo protegido (Target API). O tráfego direto "
        "entre atacantes externos e a Target API é estritamente proibido no cenário protegido, impondo o fluxo compulsório através "
        "do proxy reverso LlamaFirewall.",
        ParagraphStyle('RedeList', parent=body_style, leftIndent=0.8*cm, firstLineIndent=0)
    ))
    story.append(Spacer(1, 0.3 * cm))

    fig1_path = os.path.join(PROJECT_ROOT, "docs", "images", "figura_1_arquitetura_defesa.png")
    if os.path.exists(fig1_path):
        story.append(KeepTogether([
            Paragraph("<b>Figura 1 – Arquitetura de Defesa em Profundidade com Isolamento de Redes Docker</b>", caption_top_style),
            Image(fig1_path, width=15.5 * cm, height=9.0 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bottom_style)
        ]))

    story.append(Paragraph("<b>4.2 Scanners Especializados do Guardrail LlamaFirewall</b>", h2_style))
    story.append(Paragraph(
        "O proxy LlamaFirewall (executando na porta :8080) intercepta cada payload HTTP antes de transmiti-lo à API corporativa, "
        "submetendo os parâmetros a três scanners de análise estática e comportamental:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Prompt Guard:</b> Analisa a semântica de entrada em busca de padrões de evasão, comandos imperativos de anulação "
        "de diretrizes prévias (<i>ignore all previous instructions</i>), técnicas de <i>roleplaying</i> e extração de prompt do sistema;<br/>"
        "• <b>Agent Alignment:</b> Verifica o alinhamento das chamadas a ferramentas corporativas, bloqueando tentativas de "
        "sequestro de funções internas e injeção de parâmetros maliciosos em chamadas estruturadas de banco de dados (SQL Injection);<br/>"
        "• <b>Code Shield:</b> Detecta e impede a transmissão de instruções executáveis destinadas à interpretação em nível de "
        "sistema operacional (<i>shell commands</i>, injeção de pipes, manipulação de processos e execução arbitrária de scripts).",
        ParagraphStyle('ScannerList', parent=body_style, leftIndent=0.8*cm, firstLineIndent=0)
    ))

    story.append(Paragraph("<b>4.3 Painel de Telemetria SOC em Tempo Real (Interface Redesenhada)</b>", h2_style))
    story.append(Paragraph(
        "Para conferência analítica, auditoria forense e validação das hipóteses operacionais, concebeu-se um painel de operações "
        "de segurança passivo (SOC Mirroring). A interface foi inteiramente redesenhada com base nas diretrizes de alta integridade do "
        "arquivo <code>DESIGN.md</code>, adotando a paleta sóbria de tela editorial quente (<i>warm-cream</i> #f7f7f4 e tinta escura "
        "#26251e), profundidade baseada em fios de precisão milimétrica (<i>hairlines</i> de 1px), tipografia Inter com espaçamento "
        "negativo, métricas em JetBrains Mono e <b>exclusivamente ícones vetoriais da biblioteca Lucide Icons</b>, eliminando qualquer "
        "artefato de linguagem visual automatizada (<i>anti-ai-slop</i>).",
        body_style
    ))

    fig5_path = os.path.join(PROJECT_ROOT, "docs", "images", "soc_dashboard_redesigned.png")
    if os.path.exists(fig5_path):
        story.append(KeepTogether([
            Paragraph("<b>Figura 2 – Interface Redesenhada do SOC Dashboard de Telemetria e Defesa Ativa</b>", caption_top_style),
            Image(fig5_path, width=15.5 * cm, height=9.3 * cm),
            Paragraph("Fonte: Autores (2026). Interface implementada sob as diretrizes do DESIGN.md e Lucide Icons.", caption_bottom_style)
        ]))

    # =========================================================================
    # CAPÍTULO 5 - RESULTADOS EMPÍRICOS E ANÁLISE COMPARATIVA
    # =========================================================================
    story.append(Paragraph("<b>5 RESULTADOS EMPÍRICOS E ANÁLISE COMPARATIVA</b>", h1_style))
    story.append(Paragraph(
        "Os testes controlados foram realizados submetendo a infraestrutura a campanhas ofensivas reais contra dois cenários "
        "rigorosamente idênticos em lógica de negócio, mas distintos em controles de segurança: o <b>Baseline Desprotegido</b> "
        "(alvo corporativo exposto diretamente na porta 8000) e o <b>Alvo Protegido</b> (guarnecido pelo proxy LlamaFirewall na porta 8080).",
        body_style
    ))

    story.append(Paragraph("<b>5.1 Tabela Consolidada de Benchmark Experimental</b>", h2_style))
    story.append(Paragraph(
        "A Tabela 1 apresenta a síntese quantitativa dos testes executados por meio dos scripts automatizados de benchmark e "
        "auditoria de eventos.",
        body_style
    ))

    table_data = [
        [
            Paragraph("<b>Dimensão Avaliada</b>", caption_top_style),
            Paragraph("<b>Baseline Desprotegido (:8000)</b>", caption_top_style),
            Paragraph("<b>Alvo Protegido Guardrail (:8080)</b>", caption_top_style),
            Paragraph("<b>Veredito Defensivo</b>", caption_top_style)
        ],
        [
            Paragraph("Agente Solo ReAct (5 Vetores)", body_no_indent),
            Paragraph("100% de Sucesso na Invasão", body_no_indent),
            Paragraph("100% Bloqueado (5/5 Interceptados)", body_no_indent),
            Paragraph("Ataque Neutralizado", body_no_indent)
        ],
        [
            Paragraph("Exfiltração de Segredo Corporativo", body_no_indent),
            Paragraph("Vazamento Imediato no Passo 2", body_no_indent),
            Paragraph("Nenhum Dado Vazado (Zero Leak)", body_no_indent),
            Paragraph("Confidencialidade Preservada", body_no_indent)
        ],
        [
            Paragraph("Ataque em Enxame (Swarm 4 Agentes)", body_no_indent),
            Paragraph("Comprometimento em Paralelo", body_no_indent),
            Paragraph("4 / 4 Sub-Agentes Bloqueados", body_no_indent),
            Paragraph("Swarm Contido", body_no_indent)
        ],
        [
            Paragraph("Correlação SIEM (Regra 100210)", body_no_indent),
            Paragraph("Não Detectado / Cego", body_no_indent),
            Paragraph("Disparado (Severidade 14 - Crítica)", body_no_indent),
            Paragraph("Incidente Classificado", body_no_indent)
        ],
        [
            Paragraph("Impacto no Tráfego Legítimo (200 OK)", body_no_indent),
            Paragraph("100% Permitido (23/23)", body_no_indent),
            Paragraph("100% Homologado (Zero Falso Positivo)", body_no_indent),
            Paragraph("Operação Preservada", body_no_indent)
        ],
        [
            Paragraph("<b>Taxa Global de Mitigação</b>", body_no_indent),
            Paragraph("<b>0.0%</b>", body_no_indent),
            Paragraph("<b>100.0%</b>", body_no_indent),
            Paragraph("<b>Risco Mitigado</b>", body_no_indent)
        ],
    ]

    t_bench = Table(table_data, colWidths=[4.2 * cm, 3.8 * cm, 4.5 * cm, 3.5 * cm])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0eee6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#26251e')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfcdc4')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fafaf7')),
    ]))

    story.append(KeepTogether([
        Paragraph("<b>Tabela 1 – Benchmark Comparativo Quantitativo entre Baseline Desprotegido e Alvo Protegido</b>", caption_top_style),
        t_bench,
        Paragraph("Fonte: Autores (2026). Dados auditados a partir dos logs de telemetria dos contêineres Docker.", caption_bottom_style)
    ]))

    story.append(Paragraph("<b>5.2 Análise dos Três Casos de Uso Reais</b>", h2_style))
    story.append(Paragraph(
        "<b>Caso de Uso 1: Agente Autônomo Solo (Loop ReAct) vs Guardrail LlamaFirewall</b><br/>"
        "O agente ofensivo solo executou cinco tentativas consecutivas de exploração, articulando raciocínio contextual e adaptando "
        "seus comandos ao feedback da API. No alvo desprotegido (:8000), a flag sigilosa de administração corporativa foi obtida no "
        "Passo 2 via injeção direta de prompt. Por outro lado, no alvo protegido (:8080), todas as cinco requisições foram rejeitadas "
        "com código de status HTTP 403 Forbidden pelo LlamaFirewall.",
        body_style
    ))

    fig2_path = os.path.join(PROJECT_ROOT, "docs", "images", "figura_2_caso_1_agente_solo.png")
    if os.path.exists(fig2_path):
        story.append(KeepTogether([
            Paragraph("<b>Figura 3 – Fluxo de Execução do Caso de Uso 1: Agente Solo ReAct</b>", caption_top_style),
            Image(fig2_path, width=13.0 * cm, height=12.6 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bottom_style)
        ]))

    story.append(Paragraph(
        "<b>Caso de Uso 2: Escalação Ofensiva em Enxame (Swarm) e Correlação Crítica no Wazuh SIEM</b><br/>"
        "Diante do bloqueio individual, o agente comandante instanciou quatro sub-agentes autônomos simultâneos (ALPHA, BETA, GAMMA "
        "e DELTA), disparando rajadas de injeção paralelizadas em um intervalo de ~12ms. No ambiente protegido, cada sub-agente foi "
        "barrado pelo scanner respectivo (ALPHA pelo Prompt Guard, BETA e GAMMA pelo Agent Alignment e DELTA pelo Code Shield). "
        "A chegada dos múltiplos eventos correlacionados da mesma origem ativou a Regra 100210 do SIEM Wazuh, elevando o status do "
        "incidente para <b>Severidade 14 (Crítica)</b>.",
        body_style
    ))

    fig3_path = os.path.join(PROJECT_ROOT, "docs", "images", "figura_3_caso_2_swarm_siem.png")
    if os.path.exists(fig3_path):
        story.append(KeepTogether([
            Paragraph("<b>Figura 4 – Escalação em Enxame (Swarm) e Correlação Temporal no SIEM Wazuh</b>", caption_top_style),
            Image(fig3_path, width=15.5 * cm, height=3.4 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bottom_style)
        ]))

    story.append(Paragraph(
        "<b>Caso de Uso 3: Equipe Red Team e Auditoria Defensiva com CrewAI e Google Gemini</b><br/>"
        "Com o intuito de eliminar qualquer viés de simulação sintética, implementou-se uma equipe cooperativa com o framework "
        "CrewAI integrado diretamente ao modelo real <code>gemini-1.5-flash</code> via API Key do Google AI Studio. O agente "
        "<i>Red Team Tester</i> confeccionou payloads dinâmicos baseados no comportamento do alvo, enquanto o agente "
        "<i>Senior Defense Auditor</i> emitiu parecer formal comprovando a efetividade das barreiras de contenção.",
        body_style
    ))

    fig4_path = os.path.join(PROJECT_ROOT, "docs", "images", "figura_4_caso_3_crewai_redteam.png")
    if os.path.exists(fig4_path):
        story.append(KeepTogether([
            Paragraph("<b>Figura 5 – Estrutura Operacional da Equipe Red Team CrewAI com Google Gemini</b>", caption_top_style),
            Image(fig4_path, width=12.5 * cm, height=13.7 * cm),
            Paragraph("Fonte: Autores (2026).", caption_bottom_style)
        ]))

    story.append(Paragraph("<b>5.3 Avaliação e Validação das Hipóteses</b>", h2_style))
    story.append(Paragraph(
        "<b>Validação da Hipótese 1 (H1): CONFIRMADA INTEGRALMENTE.</b> "
        "O gateway LlamaFirewall atingiu 100% de neutralização nos ataques adversariais dirigidos ao endpoint :8080 (superando "
        "a meta estipulada de 95%), com preservação irrestrita de todas as 23 requisições corporativas legítimas submetidas "
        "(zero falso positivo).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Validação da Hipótese 2 (H2): COMPROVADA EXPERIMENTALMENTE.</b> "
        "O Suricata NIDS registrou a volumetria de pacotes TCP e HTTP, mas não impediu a exploração de vulnerabilidades no alvo "
        "desprotegido. A correlação multi-camada no SIEM Wazuh demonstrou ser estritamente indispensável para consolidar eventos "
        "dispersos e identificar a campanha coordenada do enxame de sub-agentes.",
        body_style
    ))

    # =========================================================================
    # CAPÍTULO 6 - RESUMO EXECUTIVO E RECOMENDAÇÕES OPERACIONAIS
    # =========================================================================
    story.append(Paragraph("<b>6 RESUMO EXECUTIVO E RECOMENDAÇÕES OPERACIONAIS</b>", h1_style))
    story.append(Paragraph(
        "Os resultados deste estudo fornecem subsídios técnicos e estratégicos indispensáveis para gestores de tecnologia (CISOs, "
        "arquitetos de soluções e engenheiros de segurança) na implantação de agentes de inteligência artificial em ambientes "
        "corporativos de produção:",
        body_style
    ))

    recs = [
        "<b>1. Vetar a Exposição Direta de LLMs Corporativos:</b> Nenhuma aplicação ou agente de IA que possua privilégios de execução de ferramentas deve ser exposto à rede sem um gateway de inspeção semântica em Camada 7;",
        "<b>2. Princípio do Menor Privilégio na Invocação de Ferramentas (Tool Sandboxing):</b> Ferramentas que executam comandos em sistema operacional ou consultas a bancos de dados devem operar em ambientes isolados (containers sem privilégios de root) e validar parâmetros sintáticos e semânticos;",
        "<b>3. Correlação SIEM Obrigatória para Ameaças de IA:</b> Os logs emitidos pelos guardrails de IA devem ser compulsoriamente ingeridos por um SIEM corporativo com regras analíticas capazes de agrupar múltiplos bloqueios em janelas de tempo curtas (inferiores a 1 segundo) para identificação de swarms;",
        "<b>4. Monitoramento Passivo de Rede (NIDS) como Suporte Forense:</b> A captura contínua de metadados em L3/L7 pelo Suricata provê trilha de auditoria incontestável em investigações pós-incidente."
    ]
    for r in recs:
        story.append(Paragraph(f"• {r}", ParagraphStyle('RecItem', parent=body_style, leftIndent=1.0*cm, firstLineIndent=0, spaceAfter=4)))

    # =========================================================================
    # CAPÍTULO 7 - DISPONIBILIDADE DO CÓDIGO FONTE E REPRODUTIBILIDADE
    # =========================================================================
    story.append(Paragraph("<b>7 DISPONIBILIDADE DO CÓDIGO FONTE E REPRODUTIBILIDADE</b>", h1_style))
    story.append(Paragraph(
        "Em observância às boas práticas científicas e aos preceitos da pesquisa aberta, todo o código-fonte desenvolvido — englobando "
        "os manifestos de conteinerização Docker Compose, o código dos contêineres Target API e LlamaFirewall, as regras do Suricata NIDS, "
        "as regras de correlação SIEM do Wazuh, os agentes autônomos ofensivos e o dashboard SOC de telemetria — encontra-se "
        "disponível publicamente no seguinte repositório Git:",
        body_style
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "<b>Repositório Oficial no GitHub:</b><br/>"
        "<font color='#f54e00'><b><u>https://github.com/walkowicz19/trabalho-seguranca-pi.git</u></b></font>",
        ParagraphStyle('GitBox', parent=body_style, alignment=TA_CENTER, firstLineIndent=0, spaceBefore=4, spaceAfter=8)
    ))
    story.append(Paragraph(
        "Para reproduzir integralmente o ambiente experimental e os benchmarks descritos neste relatório, basta clonar o repositório "
        "e executar as instruções catalogadas no arquivo <code>README.md</code>:",
        body_style
    ))
    story.append(Paragraph(
        "<code>git clone https://github.com/walkowicz19/trabalho-seguranca-pi.git<br/>"
        "cd trabalho-seguranca-pi<br/>"
        "docker compose up -d --build<br/>"
        "python benchmark/run_benchmark.py</code>",
        ParagraphStyle('CodeBlock', parent=styles['Normal'], fontName='Courier', fontSize=9.5, leading=13, leftIndent=1.0*cm, spaceBefore=4, spaceAfter=8)
    ))

    # =========================================================================
    # CAPÍTULO 8 - CONSIDERAÇÕES FINAIS
    # =========================================================================
    story.append(Paragraph("<b>8 CONSIDERAÇÕES FINAIS</b>", h1_style))
    story.append(Paragraph(
        "Este trabalho demonstrou que a defesa cibernética contra agentes autônomos de Inteligência Artificial demanda uma "
        "mudança paradigmática: a transição de perímetros puramente baseados em rede para ecossistemas de defesa ativa e "
        "inspeção semântica em profundidade. A bancada experimental comprovou que ferramentas de código aberto (LlamaFirewall, "
        "Suricata NIDS e SIEM Wazuh), quando adequadamente articuladas e isoladas em rede, são plenamente capazes de neutralizar "
        "ataques autônomos complexos em tempo real, preservando a integridade e a confidencialidade dos ativos corporativos.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # REFERÊNCIAS (NBR 6023)
    # =========================================================================
    story.append(Paragraph("<b>REFERÊNCIAS</b>", h1_style))
    
    refs = [
        "CREWAI. <b>CrewAI Multi-Agent Orchestration Framework</b>: Production-ready agentic workflows. 2024. Disponível em: &lt;https://github.com/crewAIInc/crewAI&gt;. Acesso em: 10 out. 2026.",
        "META AI. <b>Llama Guard & LlamaFirewall</b>: Open-source safeguards for generative AI models and applications. Meta Platforms, 2024. Disponível em: &lt;https://ai.meta.com/research/&gt;. Acesso em: 10 out. 2026.",
        "MITRE. <b>MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)</b>. McLean: The MITRE Corporation, 2024. Disponível em: &lt;https://atlas.mitre.org/&gt;. Acesso em: 11 out. 2026.",
        "NIST. <b>Artificial Intelligence Risk Management Framework (AI RMF 1.0)</b>. Gaithersburg: National Institute of Standards and Technology, 2023. DOI: 10.6028/NIST.CSWP.25.",
        "NIST. <b>Security and Privacy Controls for Information Systems and Organizations</b>. NIST Special Publication 800-53, Revision 5. Gaithersburg: National Institute of Standards and Technology, 2020.",
        "OWASP. <b>OWASP Top 10 for Large Language Model Applications and Generative AI</b>. Versão 2025. Open Worldwide Application Security Project, 2025. Disponível em: &lt;https://owasp.org/www-project-top-10-for-large-language-model-applications/&gt;. Acesso em: 08 out. 2026.",
        "SALTZER, J. H.; SCHROEDER, M. D. The protection of information in computer systems. <b>Proceedings of the IEEE</b>, v. 63, n. 9, p. 1278-1308, 1975.",
        "SURICATA. <b>Suricata User Guide Release 7.0</b>: Open Source Next Generation Intrusion Detection and Prevention Engine. Open Information Security Foundation (OISF), 2024. Disponível em: &lt;https://suricata.io/&gt;. Acesso em: 09 out. 2026.",
        "WAZUH. <b>Wazuh Documentation</b>: Open Source Security Platform for Threat Detection, Integrity Monitoring, and Incident Response. Wazuh Inc., 2024. Disponível em: &lt;https://documentation.wazuh.com/&gt;. Acesso em: 10 out. 2026.",
        "YAO, S. et al. ReAct: Synergizing Reasoning and Acting in Language Models. In: <b>International Conference on Learning Representations (ICLR)</b>, 2023. arXiv:2210.03629."
    ]

    for r in refs:
        story.append(Paragraph(r, ref_style))

    return story


def generate_accurate_pdf():
    pdf_filename = os.path.join(PROJECT_ROOT, "relatorio_tcc_seguranca_pi.pdf")
    
    # Pass 1: Build initial draft to extract exact heading page numbers
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=3.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=3.0 * cm,
        bottomMargin=2.0 * cm
    )
    story1 = build_story()
    doc.build(story1, canvasmaker=ABNTCanvas)

    # Inspect page locations
    reader = pypdf.PdfReader(pdf_filename)
    page_map = {
        "intro": 6,
        "hipot": 7,
        "teoria": 7,
        "metod": 8,
        "result": 11,
        "resumo_exec": 14,
        "codigo": 15,
        "concl": 15,
        "refs": 16
    }

    heading_keywords = {
        "intro": "1 INTRODUÇÃO",
        "hipot": "2 HIPÓTESES DE PESQUISA",
        "teoria": "3 FUNDAMENTAÇÃO TEÓRICA",
        "metod": "4 METODOLOGIA",
        "result": "5 RESULTADOS EMPÍRICOS",
        "resumo_exec": "6 RESUMO EXECUTIVO",
        "codigo": "7 DISPONIBILIDADE DO CÓDIGO",
        "concl": "8 CONSIDERAÇÕES FINAIS",
        "refs": "REFERÊNCIAS"
    }

    for p_idx, page in enumerate(reader.pages):
        txt = page.extract_text() or ''
        for key, kw in heading_keywords.items():
            if kw in txt:
                page_map[key] = p_idx + 1

    print("Mapa de páginas extraído da Passada 1:", page_map)

    # Pass 2: Rebuild with accurate page mapping in the Sumário
    doc2 = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=3.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=3.0 * cm,
        bottomMargin=2.0 * cm
    )
    story2 = build_story(page_map=page_map)
    doc2.build(story2, canvasmaker=ABNTCanvas)

    print(f"[OK] Documento PDF final gerado com precisão ABNT: {pdf_filename}")
    return pdf_filename


if __name__ == "__main__":
    generate_accurate_pdf()
