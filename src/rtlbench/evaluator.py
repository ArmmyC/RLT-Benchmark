from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from rtlbench.types import BenchmarkTask, EvaluationResult

MISMATCH_RE = re.compile(r"mismatches?\s*[:=]\s*(\d+)", re.IGNORECASE)
FAIL_RE = re.compile(r"\b(fail(?:ed|ure)?|error)\b", re.IGNORECASE)
YOSYS_STAT_RE = {
    "wires": re.compile(r"(?:Number of wires:\s+(\d+)|^\s*(\d+)\s+wires?\s*$)", re.MULTILINE),
    "wire_bits": re.compile(r"(?:Number of wire bits:\s+(\d+)|^\s*(\d+)\s+wire bits?\s*$)", re.MULTILINE),
    "cells": re.compile(r"(?:Number of cells:\s+(\d+)|^\s*(\d+)\s+cells?\s*$)", re.MULTILINE),
    "area": re.compile(r"Chip area for module[^:]+:\s*([\d.]+(?:[eE][-+]?\d+)?)"),
}


class IcarusEvaluator:
    def __init__(self, executable: str = "iverilog", timeout: float = 30.0):
        resolved = _find_executable(executable)
        if not resolved:
            raise FileNotFoundError(
                f"{executable!r} was not found. Install Icarus Verilog or set evaluator.executable."
            )
        self.executable = resolved
        self.vvp = _find_executable("vvp")
        if not self.vvp:
            raise FileNotFoundError("'vvp' was not found; install the complete Icarus Verilog package.")
        self.timeout = timeout

    def evaluate(self, task: BenchmarkTask, rtl_path: Path, work_dir: Path) -> EvaluationResult:
        testbench_path = work_dir / "testbench.sv"
        binary_path = work_dir / "simulation.out"
        testbench_path.write_text(task.testbench, encoding="utf-8")
        support_paths: dict[str, Path] = {}
        for filename, contents in task.support_files.items():
            support_path = work_dir / Path(filename).name
            support_path.write_text(contents, encoding="utf-8")
            support_paths[filename] = support_path
        compile_support_paths = [
            support_paths[name]
            for name in task.compile_support_files
            if name in support_paths
        ]
        compile_cmd = [
            self.executable,
            "-g2012",
            "-o",
            str(binary_path.resolve()),
            str(rtl_path.resolve()),
            *(str(path.resolve()) for path in compile_support_paths),
            str(testbench_path.resolve()),
        ]
        try:
            compiled = subprocess.run(
                compile_cmd, capture_output=True, text=True, timeout=self.timeout, check=False, cwd=work_dir
            )
        except subprocess.TimeoutExpired as exc:
            return EvaluationResult(False, False, False, "timeout", _timeout_log("compile", exc))
        compile_log = _command_log(compile_cmd, compiled.stdout, compiled.stderr)
        if compiled.returncode != 0:
            return EvaluationResult(False, False, False, "compile_failure", compile_log)

        sim_cmd = [self.vvp, str(binary_path.resolve())]
        try:
            simulated = subprocess.run(
                sim_cmd, capture_output=True, text=True, timeout=self.timeout, check=False, cwd=work_dir
            )
        except subprocess.TimeoutExpired as exc:
            return EvaluationResult(True, False, False, "timeout", compile_log + _timeout_log("simulation", exc))
        sim_log = _command_log(sim_cmd, simulated.stdout, simulated.stderr)
        output = f"{simulated.stdout}\n{simulated.stderr}"
        mismatch_counts = [int(value) for value in MISMATCH_RE.findall(output)]
        semantic_failure = any(value > 0 for value in mismatch_counts)
        if not mismatch_counts and FAIL_RE.search(output):
            semantic_failure = True
        passed = simulated.returncode == 0 and not semantic_failure
        return EvaluationResult(
            True,
            passed,
            passed,
            "passed" if passed else "simulation_failure",
            compile_log + sim_log,
        )


class VerilatorLintEvaluator:
    def __init__(self, executable: str = "verilator", timeout: float = 60.0):
        resolved = _find_executable(executable)
        if not resolved:
            raise FileNotFoundError(
                f"{executable!r} was not found. Install Verilator or set evaluator.executable."
            )
        self.executable = resolved
        self.timeout = timeout

    def evaluate(self, task: BenchmarkTask, rtl_path: Path, work_dir: Path) -> EvaluationResult:
        command = [
            self.executable,
            "--lint-only",
            "-Wall",
            "-Wno-fatal",
            "--timing",
            "--top-module",
            task.module_name or "top",
            str(rtl_path.resolve()),
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                cwd=work_dir,
            )
        except subprocess.TimeoutExpired as exc:
            return EvaluationResult(False, False, False, "timeout", _timeout_log("verilator_lint", exc))
        log = _command_log(command, completed.stdout, completed.stderr)
        passed = completed.returncode == 0
        return EvaluationResult(
            compile_pass=passed,
            sim_pass=passed,
            final_pass=passed,
            failure_category="passed" if passed else "compile_failure",
            log=log,
        )


class YosysPPAEvaluator:
    def __init__(self, executable: str = "yosys", timeout: float = 120.0, use_abc: bool = True):
        resolved = _find_executable(executable)
        if not resolved:
            raise FileNotFoundError(
                f"{executable!r} was not found. Install Yosys or set evaluator.executable."
            )
        self.executable = resolved
        self.timeout = timeout
        self.use_abc = use_abc

    def evaluate(self, task: BenchmarkTask, rtl_path: Path, work_dir: Path) -> EvaluationResult:
        top = task.module_name or "top"
        liberty_path = _rtlopt_liberty_path(task) if self.use_abc else None
        if self.use_abc and not liberty_path:
            return EvaluationResult(
                False,
                False,
                False,
                "missing_library",
                "Could not locate RTL-OPT Nangate liberty file for Yosys PPA evaluation.\n",
            )
        generated = self._run_stat(
            rtl_path=rtl_path,
            top=top,
            work_dir=work_dir,
            stem="generated",
            liberty_path=liberty_path,
        )
        log = generated["log"]
        metrics: dict[str, Any] = {}
        metrics.update({f"generated_{k}": v for k, v in generated["metrics"].items()})
        metrics.update(_rtlopt_baseline_metrics(task))
        if not self.use_abc:
            for prefix, path, candidate_top in _rtlopt_source_paths(task):
                baseline = self._run_stat(
                    rtl_path=path,
                    top=candidate_top,
                    work_dir=work_dir,
                    stem=prefix,
                    liberty_path=None,
                )
                log += baseline["log"]
                metrics.update({f"{prefix}_{k}": v for k, v in baseline["metrics"].items()})
        _add_ppa_comparisons(metrics)
        required_metric = "generated_area" if self.use_abc else "generated_cells"
        passed = generated["returncode"] == 0 and required_metric in metrics
        return EvaluationResult(
            compile_pass=passed,
            sim_pass=passed,
            final_pass=passed,
            failure_category="passed" if passed else "synthesis_failure",
            log=log,
            metrics=metrics,
        )

    def _run_stat(
        self,
        *,
        rtl_path: Path,
        top: str,
        work_dir: Path,
        stem: str,
        liberty_path: Path | None,
    ) -> dict[str, Any]:
        script_path = work_dir / f"{stem}_yosys.ys"
        report_path = work_dir / f"{stem}_yosys_stat.rpt"
        lines = [
            f"read -sv {rtl_path.resolve()}",
            f"hierarchy -top {top}",
            "proc; fsm; opt; memory; opt",
            "techmap; opt",
        ]
        if liberty_path is not None:
            lines.extend(
                [
                    f"dfflibmap -liberty {liberty_path.resolve()}",
                    f"abc -liberty {liberty_path.resolve()}",
                    f"tee -o {report_path.resolve()} stat -top {top} -liberty {liberty_path.resolve()}",
                ]
            )
        else:
            lines.append(f"tee -o {report_path.resolve()} stat -top {top}")
        lines.extend(["clean", ""])
        script_path.write_text("\n".join(lines), encoding="utf-8")
        command = [self.executable, str(script_path.resolve())]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                cwd=work_dir,
            )
        except subprocess.TimeoutExpired as exc:
            return {"returncode": 124, "metrics": {}, "log": _timeout_log(f"yosys:{stem}", exc)}
        metrics = parse_yosys_stat(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
        return {
            "returncode": completed.returncode,
            "metrics": metrics,
            "log": _command_log(command, completed.stdout, completed.stderr),
        }


class YosysEquivalenceEvaluator:
    def __init__(self, executable: str = "yosys", timeout: float = 120.0, seq_steps: int = 1):
        resolved = _find_executable(executable)
        if not resolved:
            raise FileNotFoundError(
                f"{executable!r} was not found. Install Yosys or set evaluator.executable."
            )
        self.executable = resolved
        self.timeout = timeout
        self.seq_steps = seq_steps
        self.generic = YosysPPAEvaluator(executable, timeout, use_abc=False)

    def evaluate(self, task: BenchmarkTask, rtl_path: Path, work_dir: Path) -> EvaluationResult:
        synth = self.generic.evaluate(task, rtl_path, work_dir)
        if not synth.compile_pass:
            return synth
        source = task.metadata.get("source_rtl")
        if not source:
            return EvaluationResult(
                True,
                False,
                False,
                "equiv_unsupported",
                synth.log + "Missing source_rtl metadata for equivalence check.\n",
                metrics=synth.metrics,
            )

        gold_path = work_dir / "equiv_gold.sv"
        gate_path = work_dir / "equiv_gate.sv"
        try:
            gold_path.write_text(_rename_first_module(Path(str(source)).read_text(encoding="utf-8"), "gold"), encoding="utf-8")
            gate_path.write_text(_rename_first_module(rtl_path.read_text(encoding="utf-8"), "gate"), encoding="utf-8")
        except ValueError as exc:
            return EvaluationResult(
                True,
                False,
                False,
                "equiv_unsupported",
                synth.log + f"Could not prepare equivalence modules: {exc}\n",
                metrics=synth.metrics,
            )

        script_path = work_dir / "equiv_yosys.ys"
        script_path.write_text(
            "\n".join(
                [
                    f"read -sv {gold_path.resolve()}",
                    "prep -top gold",
                    "design -stash gold",
                    "design -reset",
                    f"read -sv {gate_path.resolve()}",
                    "prep -top gate",
                    "design -stash gate",
                    "design -reset",
                    "design -copy-from gold -as gold gold",
                    "design -copy-from gate -as gate gate",
                    "equiv_make gold gate equiv",
                    "hierarchy -top equiv",
                    "proc; opt; memory; opt",
                    f"equiv_simple -seq {self.seq_steps}",
                    "equiv_status -assert",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        command = [self.executable, str(script_path.resolve())]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                cwd=work_dir,
            )
        except subprocess.TimeoutExpired as exc:
            return EvaluationResult(
                True,
                False,
                False,
                "timeout",
                synth.log + _timeout_log("yosys_equiv", exc),
                metrics=synth.metrics,
            )
        log = synth.log + _command_log(command, completed.stdout, completed.stderr)
        proved = completed.returncode == 0 and "Equivalence successfully proven!" in completed.stdout
        metrics = dict(synth.metrics)
        metrics["equivalence_proven"] = 1 if proved else 0
        return EvaluationResult(
            compile_pass=True,
            sim_pass=proved,
            final_pass=proved,
            failure_category="passed" if proved else "equiv_failure",
            log=log,
            metrics=metrics,
        )


def parse_yosys_stat(text: str) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for name, pattern in YOSYS_STAT_RE.items():
        match = pattern.search(text)
        if not match:
            continue
        value = next(group for group in match.groups() if group is not None)
        metrics[name] = float(value) if name == "area" else int(value)
    return metrics


def _rename_first_module(source: str, new_name: str) -> str:
    replaced, count = re.subn(r"\bmodule\s+([A-Za-z_$][\w$]*)\b", f"module {new_name}", source, count=1)
    if count != 1:
        raise ValueError("no module declaration found")
    return replaced


def _rtlopt_liberty_path(task: BenchmarkTask) -> Path | None:
    source = task.metadata.get("source_rtl")
    if not source:
        return None
    source_path = Path(str(source))
    for parent in source_path.parents:
        candidate = parent / "Results" / "RTL-OPT_Yosys" / "nangate45.lib"
        if candidate.is_file():
            return candidate
    return None


def _rtlopt_baseline_metrics(task: BenchmarkTask) -> dict[str, Any]:
    source = task.metadata.get("source_rtl")
    if not source:
        return {}
    source_path = Path(str(source))
    reports_dir = next(
        (
            parent / "Results" / "RTL-OPT_Yosys"
            for parent in source_path.parents
            if (parent / "Results" / "RTL-OPT_Yosys").is_dir()
        ),
        None,
    )
    if reports_dir is None:
        return {}
    metrics: dict[str, Any] = {}
    task_id = task.task_id
    for prefix, report_name in (
        ("baseline", f"{task_id}.rpt"),
        ("reference", f"{task_id}_ref.rpt"),
    ):
        report_path = reports_dir / report_name
        if report_path.is_file():
            parsed = parse_yosys_stat(report_path.read_text(encoding="utf-8"))
            metrics.update({f"{prefix}_{key}": value for key, value in parsed.items()})
    return metrics


def _rtlopt_source_paths(task: BenchmarkTask) -> list[tuple[str, Path, str]]:
    paths: list[tuple[str, Path, str]] = []
    source = task.metadata.get("source_rtl")
    if source:
        paths.append(("generic_baseline", Path(str(source)), task.task_id))
    reference = task.metadata.get("reference_rtl")
    if reference:
        paths.append(("generic_reference", Path(str(reference)), f"{task.task_id}_ref"))
    return paths


def _add_ppa_comparisons(metrics: dict[str, Any]) -> None:
    generated = metrics.get("generated_area")
    baseline = metrics.get("baseline_area")
    reference = metrics.get("reference_area")
    if isinstance(generated, (int, float)) and isinstance(baseline, (int, float)) and baseline:
        metrics["area_vs_baseline_pct"] = ((baseline - generated) / baseline) * 100.0
        metrics["area_ratio_to_baseline"] = generated / baseline
    if isinstance(generated, (int, float)) and isinstance(reference, (int, float)) and reference:
        metrics["area_ratio_to_reference"] = generated / reference
    generated_cells = metrics.get("generated_cells")
    baseline_cells = metrics.get("generic_baseline_cells")
    reference_cells = metrics.get("generic_reference_cells")
    if isinstance(generated_cells, (int, float)) and isinstance(baseline_cells, (int, float)) and baseline_cells:
        metrics["generic_cells_vs_baseline_pct"] = ((baseline_cells - generated_cells) / baseline_cells) * 100.0
        metrics["generic_cells_ratio_to_baseline"] = generated_cells / baseline_cells
    if isinstance(generated_cells, (int, float)) and isinstance(reference_cells, (int, float)) and reference_cells:
        metrics["generic_cells_ratio_to_reference"] = generated_cells / reference_cells


def _command_log(command: list[str], stdout: str, stderr: str) -> str:
    return f"$ {' '.join(command)}\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}\n"


def _timeout_log(stage: str, exc: subprocess.TimeoutExpired) -> str:
    return f"{stage} timed out after {exc.timeout} seconds\nstdout: {exc.stdout or ''}\nstderr: {exc.stderr or ''}\n"


def _find_executable(name: str) -> str | None:
    explicit = Path(name).expanduser()
    if explicit.is_file():
        return str(explicit.resolve())
    resolved = shutil.which(name)
    if resolved:
        return resolved
    candidate = Path(sys.prefix) / ("Scripts" if sys.platform == "win32" else "bin") / name
    return str(candidate) if candidate.is_file() else None
