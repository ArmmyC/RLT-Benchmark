from __future__ import annotations

import argparse
import subprocess

try:
    from scripts.v0_3_prompt_smoke_lib import BENCHMARKS, LARGER_PROFILES, build_larger_commands, parse_selection
except ModuleNotFoundError:  # Direct execution adds scripts/, not the repository root, to sys.path.
    from v0_3_prompt_smoke_lib import BENCHMARKS, LARGER_PROFILES, build_larger_commands, parse_selection


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print or execute qwen36-27b v0.3 larger prompt-validation commands")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--profiles", default=",".join(LARGER_PROFILES))
    parser.add_argument("--benchmarks", default=",".join(BENCHMARKS))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--notes-prefix", default="v0.3 prompt larger validation")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        benchmarks = parse_selection(args.benchmarks, BENCHMARKS, "benchmark")
        profiles = parse_selection(args.profiles, LARGER_PROFILES, "prompt profile")
        commands = build_larger_commands(
            base_url=args.base_url,
            benchmarks=benchmarks,
            profiles=profiles,
            workers=args.workers,
            notes_prefix=args.notes_prefix,
        )
    except ValueError as exc:
        parser.error(str(exc))

    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"{mode}: {len(commands)} qwen36-27b larger-validation command(s)")
    for command in commands:
        print(command.display())
        if args.execute:
            subprocess.run(command.argv, check=True)
    if not args.execute:
        print("No commands executed. Pass --execute only after reviewing this larger-validation plan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
