from __future__ import annotations

import shlex
import sys
from dataclasses import dataclass
from pathlib import Path


BENCHMARKS = ("verilogeval", "rtllm2", "rtlopt")
PROFILES = (
    "neutral_baseline",
    "strict_rtl_only",
    "low_area_low_power",
    "no_explanation_code_only",
)
LARGER_PROFILES = ("neutral_baseline", "strict_rtl_only")
LARGER_LIMITS = {
    "verilogeval": 20,
    "rtllm2": 10,
    "rtlopt": 10,
}
CONFIGS = {
    benchmark: Path(f"configs/experiments/v0.3_qwen36_27b_{benchmark}_prompt_smoke.yaml")
    for benchmark in BENCHMARKS
}
OUTPUT_ROOT = Path("outputs/experiments/v0.3_prompt_profiles")
LARGER_OUTPUT_ROOT = Path("outputs/experiments/v0.3_prompt_profiles_larger")


@dataclass(frozen=True)
class SmokeCommand:
    benchmark: str
    profile: str
    output_dir: Path
    argv: tuple[str, ...]

    def display(self) -> str:
        return shlex.join(self.argv)


def parse_selection(value: str, allowed: tuple[str, ...], label: str) -> tuple[str, ...]:
    selected = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(selected) - set(allowed))
    if not selected:
        raise ValueError(f"At least one {label} is required")
    if unknown:
        raise ValueError(f"Unknown {label}: {', '.join(unknown)}; available: {', '.join(allowed)}")
    return tuple(item for item in allowed if item in selected)


def build_smoke_commands(
    *,
    base_url: str,
    benchmarks: tuple[str, ...] = BENCHMARKS,
    profiles: tuple[str, ...] = PROFILES,
    workers: int = 1,
    limit: int = 3,
    notes_prefix: str = "v0.3 prompt smoke",
    python: str = sys.executable,
) -> list[SmokeCommand]:
    if workers < 1 or limit < 1:
        raise ValueError("workers and limit must be at least 1")

    commands: list[SmokeCommand] = []
    for benchmark in benchmarks:
        for profile in profiles:
            output_dir = OUTPUT_ROOT / benchmark / profile
            notes = f"{notes_prefix}: {benchmark} / {profile}"
            argv = (
                python,
                "-m",
                "rtlbench.cli",
                "--config",
                str(CONFIGS[benchmark]),
                "--model-preset",
                "qwen36-27b",
                "--base-url",
                base_url,
                "--prompt-profile",
                profile,
                "--output-dir",
                str(output_dir),
                "--workers",
                str(workers),
                "--limit",
                str(limit),
                "--notes",
                notes,
            )
            commands.append(SmokeCommand(benchmark, profile, output_dir, argv))
    return commands


def build_larger_commands(
    *,
    base_url: str,
    benchmarks: tuple[str, ...] = BENCHMARKS,
    profiles: tuple[str, ...] = LARGER_PROFILES,
    workers: int = 1,
    notes_prefix: str = "v0.3 prompt larger validation",
    python: str = sys.executable,
) -> list[SmokeCommand]:
    if workers < 1:
        raise ValueError("workers must be at least 1")
    unknown_profiles = sorted(set(profiles) - set(LARGER_PROFILES))
    if unknown_profiles:
        raise ValueError(
            "Larger validation supports only "
            f"{', '.join(LARGER_PROFILES)}; got: {', '.join(unknown_profiles)}"
        )

    commands: list[SmokeCommand] = []
    for benchmark in benchmarks:
        limit = LARGER_LIMITS[benchmark]
        for profile in profiles:
            output_dir = LARGER_OUTPUT_ROOT / benchmark / profile
            notes = f"{notes_prefix}: {benchmark} / {profile}"
            argv = (
                python,
                "-m",
                "rtlbench.cli",
                "--config",
                str(CONFIGS[benchmark]),
                "--model-preset",
                "qwen36-27b",
                "--base-url",
                base_url,
                "--prompt-profile",
                profile,
                "--output-dir",
                str(output_dir),
                "--workers",
                str(workers),
                "--limit",
                str(limit),
                "--notes",
                notes,
            )
            commands.append(SmokeCommand(benchmark, profile, output_dir, argv))
    return commands
