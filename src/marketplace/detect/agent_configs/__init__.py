from marketplace.detect.agent_configs.claude import CLAUDE_CONFIG
from marketplace.detect.agent_configs.codex import CODEX_CONFIG
from marketplace.detect.agent_configs.copilot import COPILOT_CONFIG
from marketplace.detect.agent_configs.cursor import CURSOR_CONFIG
from marketplace.detect.agent_configs.gemini import GEMINI_CONFIG
from marketplace.detect.base import AgentConfig

ALL_CONFIGS: tuple[AgentConfig, ...] = (
    CLAUDE_CONFIG,
    CURSOR_CONFIG,
    COPILOT_CONFIG,
    CODEX_CONFIG,
    GEMINI_CONFIG,
)

__all__ = [
    "ALL_CONFIGS",
    "CLAUDE_CONFIG",
    "CODEX_CONFIG",
    "COPILOT_CONFIG",
    "CURSOR_CONFIG",
    "GEMINI_CONFIG",
]
