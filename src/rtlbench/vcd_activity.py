from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class VCDActivityError(ValueError):
    pass


@dataclass(frozen=True)
class VCDToggleResult:
    total_toggles: int
    signal_toggles: dict[str, int]
    start_time: int | None
    end_time: int | None
    excluded_signals: tuple[str, ...]


@dataclass
class _Signal:
    code: str
    name: str
    width: int


def count_vcd_toggles(
    vcd_text: str,
    *,
    exclude_signals: set[str] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
) -> VCDToggleResult:
    if not isinstance(vcd_text, str) or not vcd_text.strip():
        raise VCDActivityError("VCD input is empty")
    if start_time is not None and end_time is not None and end_time < start_time:
        raise VCDActivityError("end_time must be greater than or equal to start_time")

    excluded = exclude_signals or set()
    signals: dict[str, _Signal] = {}
    values: dict[str, str] = {}
    toggles: dict[str, int] = {}
    current_time = 0
    saw_time = False
    in_header = True

    for raw_line in vcd_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("$var"):
            signal = _parse_var(line)
            if signal.code in signals:
                raise VCDActivityError(f"duplicate VCD identifier: {signal.code}")
            signals[signal.code] = signal
            toggles[signal.name] = 0
            continue
        if line == "$enddefinitions $end":
            in_header = False
            continue
        if line.startswith("$"):
            continue
        if line.startswith("#"):
            try:
                current_time = int(line[1:])
            except ValueError as exc:
                raise VCDActivityError(f"invalid VCD timestamp: {line}") from exc
            saw_time = True
            in_header = False
            continue
        if in_header:
            continue
        if not signals:
            raise VCDActivityError("VCD contains no signal definitions")
        code, value = _parse_value_change(line)
        if code not in signals:
            raise VCDActivityError(f"value change references unknown VCD identifier: {code}")
        signal = signals[code]
        if signal.name in excluded:
            values[code] = value
            continue
        previous = values.get(code)
        values[code] = value
        if previous is None or previous == value:
            continue
        if _inside_window(current_time, start_time, end_time):
            toggles[signal.name] += 1

    if not signals:
        raise VCDActivityError("VCD contains no signal definitions")
    if not saw_time:
        raise VCDActivityError("VCD contains no timestamps")

    visible_toggles = {name: count for name, count in toggles.items() if name not in excluded}
    return VCDToggleResult(
        total_toggles=sum(visible_toggles.values()),
        signal_toggles=visible_toggles,
        start_time=start_time,
        end_time=end_time,
        excluded_signals=tuple(sorted(excluded)),
    )


def count_vcd_file(
    path: str | Path,
    *,
    exclude_signals: set[str] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
) -> VCDToggleResult:
    vcd_path = Path(path)
    if not vcd_path.is_file():
        raise FileNotFoundError(f"VCD file not found: {vcd_path}")
    return count_vcd_toggles(
        vcd_path.read_text(encoding="utf-8"),
        exclude_signals=exclude_signals,
        start_time=start_time,
        end_time=end_time,
    )


def _parse_var(line: str) -> _Signal:
    parts = line.split()
    if len(parts) < 6 or parts[0] != "$var" or parts[-1] != "$end":
        raise VCDActivityError(f"malformed VCD $var line: {line}")
    try:
        width = int(parts[2])
    except ValueError as exc:
        raise VCDActivityError(f"invalid VCD signal width: {line}") from exc
    if width <= 0:
        raise VCDActivityError(f"invalid VCD signal width: {line}")
    code = parts[3]
    name = parts[4]
    if not code or not name:
        raise VCDActivityError(f"malformed VCD $var line: {line}")
    return _Signal(code=code, name=name, width=width)


def _parse_value_change(line: str) -> tuple[str, str]:
    if line[0] in "01xXzZ":
        return line[1:], line[0].lower()
    if line[0] in "bB":
        parts = line.split()
        if len(parts) != 2 or len(parts[0]) == 1:
            raise VCDActivityError(f"malformed VCD vector change: {line}")
        return parts[1], parts[0].lower()
    raise VCDActivityError(f"unsupported VCD value change: {line}")


def _inside_window(time_value: int, start_time: int | None, end_time: int | None) -> bool:
    if start_time is not None and time_value < start_time:
        return False
    if end_time is not None and time_value > end_time:
        return False
    return True
