"""
Módulo de Scanners do LlamaFirewall
Implementa os scanners definidos pela Meta (PurpleLlama / LlamaFirewall):
1. Prompt Guard: Detecção de Prompt Injection e Jailbreak
2. Agent Alignment: Detecção de Goal Hijacking e manipulação de ferramentas
3. Code Shield: Detecção de código malicioso e injeção de comandos
"""

import re
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional

class ScannerType(str, Enum):
    PROMPT_GUARD = "PROMPT_GUARD"
    AGENT_ALIGNMENT = "AGENT_ALIGNMENT"
    CODE_SHIELD = "CODE_SHIELD"

class Decision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"

@dataclass
class ScanResult:
    decision: Decision
    scanner_type: Optional[ScannerType] = None
    reason: Optional[str] = None
    score: float = 0.0
    details: Optional[Dict[str, Any]] = None

    def to_dict(self):
        d = asdict(self)
        d['decision'] = self.decision.value
        if self.scanner_type:
            d['scanner_type'] = self.scanner_type.value
        return d

class PromptGuardScanner:
    """
    Inspeciona entradas textuais procurando injeções diretas e indiretas de prompt,
    tentativas de jailbreak, exfiltração de prompt de sistema e desvio de persona.
    """
    def __init__(self):
        self.injection_patterns = [
            (r"(?i)ignore\s+(?:all\s+|any\s+|previous\s+|prior\s+)*(?:instructions|rules|directions|prompts)", 0.95, "Prompt Injection: Ignore instructions directive"),
            (r"(?i)disregard\s+(?:all\s+|any\s+|previous\s+|prior\s+)*(?:instructions|rules|prompts)", 0.95, "Prompt Injection: Disregard instructions directive"),
            (r"(?i)(reveal|show|print|display|output|dump)\s+(the\s+)?(system\s+prompt|initial\s+prompt|secret\s+key|confidential)", 0.92, "Prompt Injection: System prompt extraction attempt"),
            (r"(?i)(you\s+are\s+now|act\s+as|pretend\s+to\s+be)\s+(dan|developer\s+mode|unfiltered|jailbroken|an\s+evil)", 0.93, "Jailbreak: Persona / Role Hijacking (DAN mode)"),
            (r"(?i)bypass\s+(all\s+)?(security|guardrails|safety\s+filters|moderation)", 0.90, "Jailbreak: Safety filter bypass attempt"),
            (r"(?i)(start\s+in\s+developer\s+mode|enable\s+sudo\s+mode)", 0.90, "Jailbreak: Privilege escalation attempt"),
            (r"(?i)base64\s+decode.*(eval|exec|import)", 0.88, "Prompt Injection: Obfuscated payload execution")
        ]

    def scan(self, text: str) -> ScanResult:
        if not text:
            return ScanResult(decision=Decision.ALLOW, score=0.0)

        for pattern, base_score, reason in self.injection_patterns:
            if re.search(pattern, text):
                return ScanResult(
                    decision=Decision.BLOCK,
                    scanner_type=ScannerType.PROMPT_GUARD,
                    reason=reason,
                    score=base_score,
                    details={"matched_pattern": pattern, "input_snippet": text[:100]}
                )

        return ScanResult(decision=Decision.ALLOW, scanner_type=ScannerType.PROMPT_GUARD, score=0.02)


class AgentAlignmentScanner:
    """
    Inspeciona ações de agentes autônomos e chamadas de ferramentas (tool calling).
    Impede Goal Hijacking e abuso de ferramentas sensíveis do sistema.
    """
    def __init__(self):
        self.forbidden_tools = {"shell_exec", "run_command", "bash", "terminal", "system_exec"}
        self.sensitive_tools = {"db_query", "file_read", "file_write"}

    def scan_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> ScanResult:
        tool_lower = tool_name.lower().strip()

        # Bloqueio imediato de execução direta de comandos não autorizados
        if tool_lower in self.forbidden_tools:
            return ScanResult(
                decision=Decision.BLOCK,
                scanner_type=ScannerType.AGENT_ALIGNMENT,
                reason=f"Goal Hijacking / Tool Misalignment: Execução não autorizada da ferramenta '{tool_name}'",
                score=0.98,
                details={"tool": tool_name, "parameters": parameters}
            )

        # Inspeciona parâmetros de consultas ou ferramentas de dados
        params_str = json.dumps(parameters).lower()
        if "drop table" in params_str or "or 1=1" in params_str or "--" in params_str:
            return ScanResult(
                decision=Decision.BLOCK,
                scanner_type=ScannerType.AGENT_ALIGNMENT,
                reason="Agent Tool Abuse: Tentativa de injeção de parâmetros maliciosos em ferramenta interna",
                score=0.96,
                details={"tool": tool_name, "parameters": parameters}
            )

        return ScanResult(decision=Decision.ALLOW, scanner_type=ScannerType.AGENT_ALIGNMENT, score=0.05)


class CodeShieldScanner:
    """
    Inspeciona códigos gerados ou transmitidos por agentes procurando scripts maliciosos,
    reverse shells e comandos de destruição.
    """
    def __init__(self):
        self.dangerous_code_patterns = [
            (r"(?i)(os\.system|subprocess\.Popen|subprocess\.run|shlex\.quote)", 0.91, "CodeShield: Unsafe subprocess execution"),
            (r"(?i)(/bin/bash\s+-i|nc\s+-e\s+/bin/sh|mkfifo\s+/tmp/f)", 0.99, "CodeShield: Reverse Shell payload detected"),
            (r"(?i)(rm\s+-rf\s+/|del\s+/f\s+/s\s+/q\s+c:\\)", 0.99, "CodeShield: Destructive filesystem command detected"),
            (r"(?i)(eval\s*\(|exec\s*\(|__import__\s*\()", 0.89, "CodeShield: Dynamic code evaluation detected")
        ]

    def scan(self, code_text: str) -> ScanResult:
        if not code_text:
            return ScanResult(decision=Decision.ALLOW, score=0.0)

        for pattern, base_score, reason in self.dangerous_code_patterns:
            if re.search(pattern, code_text):
                return ScanResult(
                    decision=Decision.BLOCK,
                    scanner_type=ScannerType.CODE_SHIELD,
                    reason=reason,
                    score=base_score,
                    details={"matched_pattern": pattern, "snippet": code_text[:100]}
                )

        return ScanResult(decision=Decision.ALLOW, scanner_type=ScannerType.CODE_SHIELD, score=0.01)


class LlamaFirewallEngine:
    """
    Motor central que orquestra todos os scanners da arquitetura LlamaFirewall.
    """
    def __init__(self):
        self.prompt_guard = PromptGuardScanner()
        self.agent_alignment = AgentAlignmentScanner()
        self.code_shield = CodeShieldScanner()

    def inspect_request(self, payload: Dict[str, Any], path: str) -> ScanResult:
        # Se for endpoint de chat ou geração de texto
        if "prompt" in payload:
            text = str(payload["prompt"])
            # 1. Verifica prompt injection
            res = self.prompt_guard.scan(text)
            if res.decision == Decision.BLOCK:
                return res
            # 2. Verifica se há código perigoso no prompt
            res_code = self.code_shield.scan(text)
            if res_code.decision == Decision.BLOCK:
                return res_code

        # Se for execução de ferramentas por agentes
        if "tool_name" in payload:
            tool_name = str(payload.get("tool_name", ""))
            params = payload.get("parameters", {})
            res_agent = self.agent_alignment.scan_tool_call(tool_name, params)
            if res_agent.decision == Decision.BLOCK:
                return res_agent

        return ScanResult(decision=Decision.ALLOW, score=0.02, reason="Passed all LlamaFirewall guardrails")
