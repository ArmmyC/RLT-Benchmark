from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ToolAvailability:
    iverilog: str | None
    vvp: str | None
    yosys: str | None
    iverilog_healthy: bool = True
    vvp_healthy: bool = True
    yosys_healthy: bool = True

    @property
    def has_icarus(self) -> bool:
        return self.iverilog is not None and self.vvp is not None

    @property
    def has_yosys(self) -> bool:
        return self.yosys is not None

    @property
    def healthy_icarus(self) -> bool:
        return self.has_icarus and self.iverilog_healthy and self.vvp_healthy

    @property
    def healthy_yosys(self) -> bool:
        return self.has_yosys and self.yosys_healthy


@dataclass(frozen=True)
class ToolCommandResult:
    returncode: int | None
    stdout: str
    stderr: str
    startup_failed: bool = False


def detect_tools() -> ToolAvailability:
    iverilog = shutil.which("iverilog")
    vvp = shutil.which("vvp")
    yosys = shutil.which("yosys")
    return ToolAvailability(
        iverilog=iverilog,
        vvp=vvp,
        yosys=yosys,
        iverilog_healthy=_probe_tool(iverilog, "-V"),
        vvp_healthy=_probe_tool(vvp, "-V"),
        yosys_healthy=_probe_tool(yosys, "-V"),
    )


def run_tool_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = 30,
) -> ToolCommandResult:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ToolCommandResult(returncode=None, stdout="", stderr="", startup_failed=True)

    return ToolCommandResult(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        startup_failed=_is_runtime_startup_status(result.returncode),
    )


def _probe_tool(path: str | None, version_arg: str) -> bool:
    if path is None:
        return False
    result = run_tool_command([path, version_arg], timeout=5)
    return not result.startup_failed and result.returncode == 0


def _is_runtime_startup_status(returncode: int) -> bool:
    # Windows NTSTATUS failures are returned either signed or unsigned.
    return returncode < 0 or returncode >= 0xC0000000
