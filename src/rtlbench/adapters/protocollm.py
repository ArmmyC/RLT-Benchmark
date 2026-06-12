from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

import yaml

from rtlbench.adapters.base import BenchmarkAdapter
from rtlbench.types import BenchmarkTask


class ProtocolLLMAdapter(BenchmarkAdapter):
    name = "protocollm"
    extract_all_modules = True
    evaluator_name = "verilator_lint"

    def load_tasks(self) -> Iterator[BenchmarkTask]:
        config_path = self._find_config()
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        for protocol, prompts in config.items():
            if self.split and protocol.lower() != self.split.lower():
                continue
            if not isinstance(prompts, dict):
                continue
            for prompt_name, prompt in prompts.items():
                if not isinstance(prompt, str) or not prompt.strip():
                    continue
                yield BenchmarkTask(
                    task_id=f"{protocol}__{prompt_name}",
                    prompt=prompt,
                    testbench="",
                    module_name=_module_name(prompt),
                    metadata={
                        "source_format": "protocollm_public",
                        "protocol": protocol,
                        "prompt_name": prompt_name,
                        "config_path": str(config_path),
                        "evaluation_note": "Public repo includes prompts and lint/synthesis scripts, but no functional waveform testbenches.",
                    },
                )

    def build_prompt(self, task: BenchmarkTask) -> str:
        module_note = (
            f"The required top module is `{task.module_name}`. "
            if task.module_name
            else ""
        )
        return (
            f"{task.prompt.rstrip()}\n\n"
            f"{module_note}Do not change the module name or interface. "
            "Do not include a testbench. Output only the complete synthesizable SystemVerilog RTL module."
        )

    def _find_config(self) -> Path:
        candidates = [
            self.root / "src" / "configs" / "base.yaml",
            self.root / "configs" / "base.yaml",
            self.root,
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise FileNotFoundError(
            f"No ProtocolLLM base.yaml found under {self.root}. Expected src/configs/base.yaml."
        )


def _module_name(prompt: str) -> str | None:
    match = re.search(r"\bmodule\s+([A-Za-z_$][\w$]*)\s*\(", prompt)
    return match.group(1) if match else None
