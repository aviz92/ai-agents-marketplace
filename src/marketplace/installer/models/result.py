from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InstallResult:
    target: str
    installed: int
    files_written: list[str] = field(default_factory=list)
    output_dir: str = ""
    covers: list[str] = field(default_factory=list)
