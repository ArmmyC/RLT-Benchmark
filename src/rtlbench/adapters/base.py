from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator

from rtlbench.types import BenchmarkTask


class BenchmarkAdapter(ABC):
    name: str
    extract_all_modules = False
    evaluator_name = "icarus"

    def __init__(self, root: Path, split: str | None = None):
        self.root = root
        self.split = split

    @abstractmethod
    def load_tasks(self) -> Iterator[BenchmarkTask]:
        raise NotImplementedError

    @abstractmethod
    def build_prompt(self, task: BenchmarkTask) -> str:
        raise NotImplementedError
