from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from rtlbench.evaluator import (
    _find_executable,
    _yosys_path,
    resolve_yosys_techmap,
    yosys_techmap_command,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preflight Yosys techmap resolution for RTLBench")
    parser.add_argument("--yosys", default="yosys", help="Yosys executable path or command")
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser


def build_preflight_script(verilog_path: Path, resolution) -> str:
    return "\n".join(
        [
            f"read_verilog -sv {_yosys_path(verilog_path.resolve())}",
            "hierarchy -top tiny",
            "proc; opt",
            yosys_techmap_command(resolution),
            "stat",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    yosys = _find_executable(args.yosys)
    if yosys is None:
        print(f"FAIL yosys_not_found executable={args.yosys}", file=sys.stderr)
        return 1

    resolution = resolve_yosys_techmap(yosys)
    with tempfile.TemporaryDirectory(prefix="rtlbench-yosys-techmap-") as tmp:
        work_dir = Path(tmp)
        verilog_path = work_dir / "tiny.sv"
        script_path = work_dir / "techmap_preflight.ys"
        verilog_path.write_text(
            "module tiny(input logic a, input logic b, output logic y); assign y = a ^ b; endmodule\n",
            encoding="utf-8",
        )
        script_path.write_text(build_preflight_script(verilog_path, resolution), encoding="utf-8")
        try:
            completed = subprocess.run(
                [yosys, str(script_path)],
                capture_output=True,
                text=True,
                timeout=args.timeout,
                check=False,
                cwd=work_dir,
            )
        except subprocess.TimeoutExpired as exc:
            print(f"FAIL timeout={exc.timeout} techmap_mode={resolution.describe()}", file=sys.stderr)
            return 1

    if completed.returncode == 0:
        print(f"PASS techmap_mode={resolution.describe()}")
        return 0
    print(f"FAIL returncode={completed.returncode} techmap_mode={resolution.describe()}", file=sys.stderr)
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
