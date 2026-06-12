from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

from rtlbench.adapters.base import BenchmarkAdapter
from rtlbench.types import BenchmarkTask


class RTLLM2Adapter(BenchmarkAdapter):
    name = "rtllm2"
    extract_all_modules = True

    def load_tasks(self) -> Iterator[BenchmarkTask]:
        task_dirs = sorted(
            path.parent
            for path in self.root.rglob("design_description.txt")
            if not any(part.startswith("_") or part == ".git" for part in path.parts)
        )
        if self.split:
            task_dirs = [path for path in task_dirs if self.split.lower() in _task_id(self.root, path).lower()]
        if not task_dirs:
            raise FileNotFoundError(
                f"No RTLLM 2.0 design_description.txt files found under {self.root}"
            )

        for task_dir in task_dirs:
            description_path = task_dir / "design_description.txt"
            testbench_path = task_dir / "testbench.v"
            if not testbench_path.is_file():
                raise FileNotFoundError(f"Missing testbench.v for {task_dir}")
            description = description_path.read_text(encoding="utf-8", errors="replace")
            support_files = {}
            for support_path in sorted(task_dir.iterdir()):
                if support_path.name in {"design_description.txt", "testbench.v", "makefile"}:
                    continue
                if support_path.name.startswith("verified_") and support_path.suffix == ".v":
                    continue
                if support_path.is_file() and support_path.suffix.lower() in {".txt", ".dat", ".mem"}:
                    support_files[support_path.name] = support_path.read_text(
                        encoding="utf-8", errors="replace"
                    )
            yield BenchmarkTask(
                task_id=_task_id(self.root, task_dir),
                prompt=description,
                testbench=testbench_path.read_text(encoding="utf-8", errors="replace"),
                module_name=_module_name(description) or task_dir.name,
                support_files=support_files,
                compile_support_files=[],
                metadata={
                    "source_format": "rtllm2",
                    "source_dir": str(task_dir),
                    "reference_files": [path.name for path in task_dir.glob("verified_*.v")],
                },
            )

    def build_prompt(self, task: BenchmarkTask) -> str:
        return (
            f"{task.prompt.rstrip()}\n\n"
            f"The required top module is `{task.module_name}`. "
            "Do not change the module name or interface. "
            "Do not include a testbench. Output only the complete synthesizable RTL module."
        )


def _task_id(root: Path, task_dir: Path) -> str:
    return "__".join(task_dir.relative_to(root).parts)


def _module_name(description: str) -> str | None:
    match = re.search(
        r"Module\s+name\s*:\s*([A-Za-z_$][\w$]*)", description, re.IGNORECASE
    )
    return match.group(1) if match else None
