from __future__ import annotations

import subprocess
from pathlib import Path

from rtlbench.evaluator import (
    YosysTechmapResolution,
    resolve_yosys_techmap,
    yosys_techmap_command,
)
from scripts import check_yosys_techmap


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("// techmap\n", encoding="utf-8")
    return path


def test_explicit_env_var_techmap_path_resolution(tmp_path: Path) -> None:
    techmap = touch(tmp_path / "custom" / "techmap.v")

    resolved = resolve_yosys_techmap("missing-yosys", {"RTLBench_YOSYS_TECHMAP": str(techmap)})

    assert resolved.path == techmap.resolve()
    assert resolved.mode == "RTLBench_YOSYS_TECHMAP"


def test_yosys_techmap_env_var_is_second_explicit_resolution(tmp_path: Path) -> None:
    techmap = touch(tmp_path / "custom" / "techmap.v")

    resolved = resolve_yosys_techmap("missing-yosys", {"YOSYS_TECHMAP": str(techmap)})

    assert resolved.path == techmap.resolve()
    assert resolved.mode == "YOSYS_TECHMAP"


def test_yosys_datdir_resolution(tmp_path: Path) -> None:
    techmap = touch(tmp_path / "yosys-data" / "techmap.v")

    resolved = resolve_yosys_techmap("missing-yosys", {"YOSYS_DATDIR": str(techmap.parent)})

    assert resolved.path == techmap.resolve()
    assert resolved.mode == "YOSYS_DATDIR"


def test_oss_cad_suite_share_yosys_near_executable_resolution(tmp_path: Path) -> None:
    yosys = touch(tmp_path / "oss-cad-suite" / "bin" / "yosys.exe")
    techmap = touch(tmp_path / "oss-cad-suite" / "share" / "yosys" / "techmap.v")

    resolved = resolve_yosys_techmap(yosys, {})

    assert resolved.path == techmap.resolve()
    assert resolved.mode == "near_yosys_executable"


def test_fallback_to_bare_techmap_when_no_file_exists(tmp_path: Path) -> None:
    yosys = touch(tmp_path / "bin" / "yosys.exe")

    resolved = resolve_yosys_techmap(yosys, {})

    assert resolved.path is None
    assert resolved.mode == "bare"
    assert yosys_techmap_command(resolved) == "techmap; opt"


def test_generated_script_uses_explicit_techmap_map(tmp_path: Path) -> None:
    techmap = touch(tmp_path / "share" / "yosys" / "techmap.v")
    resolution = YosysTechmapResolution(techmap.resolve(), "test")

    command = yosys_techmap_command(resolution)

    assert "techmap -map" in command
    assert str(techmap.resolve()).replace("\\", "/") in command
    assert command.endswith("; opt")


def test_preflight_script_uses_bare_fallback_when_no_file_exists(tmp_path: Path) -> None:
    verilog = tmp_path / "tiny.sv"
    verilog.write_text("module tiny; endmodule\n", encoding="utf-8")

    script = check_yosys_techmap.build_preflight_script(
        verilog,
        YosysTechmapResolution(None, "bare"),
    )

    assert "techmap; opt" in script
    assert "techmap -map" not in script


def test_preflight_argument_parser_defaults_to_yosys() -> None:
    args = check_yosys_techmap.build_parser().parse_args([])

    assert args.yosys == "yosys"
    assert args.timeout == 30.0


def test_preflight_main_constructs_yosys_command_without_real_yosys(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    yosys = touch(tmp_path / "oss" / "bin" / "yosys.exe")
    techmap = touch(tmp_path / "oss" / "share" / "yosys" / "techmap.v")
    calls = []
    generated_scripts = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        generated_scripts.append(Path(command[1]).read_text(encoding="utf-8"))
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(check_yosys_techmap.subprocess, "run", fake_run)

    assert check_yosys_techmap.main(["--yosys", str(yosys)]) == 0

    out = capsys.readouterr().out
    assert "PASS techmap_mode=near_yosys_executable:" in out
    assert str(techmap.resolve()) in out
    assert calls
    assert calls[0][0][0] == str(yosys.resolve())
    assert "techmap -map" in generated_scripts[0]
