from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

from rtlbench.adapters.base import BenchmarkAdapter
from rtlbench.types import BenchmarkTask


class RTLOPTAdapter(BenchmarkAdapter):
    name = "rtlopt"
    extract_all_modules = True
    evaluator_name = "verilator_lint"

    def load_tasks(self) -> Iterator[BenchmarkTask]:
        benchmark_root = self._find_benchmark_root()
        design_dirs = sorted(
            path
            for path in benchmark_root.iterdir()
            if path.is_dir() and not path.name.endswith("_ref")
        )
        if self.split:
            wanted = {item.strip() for item in self.split.split(",") if item.strip()}
            design_dirs = [path for path in design_dirs if path.name in wanted]
        if not design_dirs:
            raise FileNotFoundError(f"No RTL-OPT design directories found under {benchmark_root}")

        for design_dir in design_dirs:
            design = design_dir.name
            rtl_path = _find_rtl_file(design_dir, design)
            ref_dir = benchmark_root / f"{design}_ref"
            ref_path = _find_rtl_file(ref_dir, f"{design}_ref") if ref_dir.is_dir() else None
            if rtl_path is None:
                continue
            source_rtl = rtl_path.read_text(encoding="utf-8")
            yield BenchmarkTask(
                task_id=design,
                prompt=source_rtl,
                testbench="",
                module_name=_module_name(source_rtl) or design,
                metadata={
                    "source_format": "rtlopt",
                    "source_rtl": str(rtl_path),
                    "reference_rtl": str(ref_path) if ref_path else None,
                    "has_reference": ref_path is not None,
                },
            )

    def build_prompt(self, task: BenchmarkTask) -> str:
        module_note = (
            f"The required top module is `{task.module_name}`. " if task.module_name else ""
        )
        return (
            "Optimize the following RTL for better power, performance, and area while preserving "
            "cycle-level functional behavior and the same top-level interface.\n\n"
            f"{module_note}"
            "Keep the module name and ports unchanged. Return only complete synthesizable "
            "Verilog/SystemVerilog code, with no markdown fences, comments about the task, or testbench.\n\n"
            "Suboptimal RTL:\n"
            f"{task.prompt.rstrip()}"
        )

    def _find_benchmark_root(self) -> Path:
        candidates = [self.root]
        if self.root.is_dir():
            candidates.append(self.root / "benchmark")
        for candidate in candidates:
            if candidate.is_dir() and any(
                path.is_dir()
                and not path.name.endswith("_ref")
                and _find_rtl_file(path, path.name) is not None
                for path in candidate.iterdir()
            ):
                return candidate
        raise FileNotFoundError(
            f"No RTL-OPT benchmark directory found under {self.root}. "
            "Set benchmark.root to the RTL-OPT repository or its benchmark/ directory."
        )


def _find_rtl_file(directory: Path, stem: str) -> Path | None:
    for suffix in (".v", ".sv"):
        candidate = directory / f"{stem}{suffix}"
        if candidate.is_file():
            return candidate
    matches = sorted([*directory.glob("*.v"), *directory.glob("*.sv")])
    return matches[0] if matches else None


def _module_name(source: str) -> str | None:
    match = re.search(r"\bmodule\s+([A-Za-z_$][\w$]*)\b", source)
    return match.group(1) if match else None
