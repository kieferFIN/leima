from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class StampType(Enum):
    OFF = 'o'
    ADMIN = 'a'
    BILL = 'b'
    NONBILL = 'n'
    EMPTY = 'e'


@dataclass
class Stamp:
    start: int
    end: int = None  # type: ignore
    type: StampType = StampType.EMPTY
    msg: str = ""
    extras: list[str] = field(default_factory=lambda: [])

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass
class WorkDay:
    stamps: list[Stamp] = field(default_factory=lambda: [])

    def add(self, stamp: Stamp):
        self.stamps.append(stamp)

    @property
    def work_time(self) -> int:
        total = 0
        for s in self.stamps:
            if s.type != StampType.OFF:
                total += s.length
        return total

    def times(self) -> dict[StampType, int]:
        times = defaultdict(int)
        for s in self.stamps:
            times[s.type] += s.length
        return dict(times)

    @property
    def start(self) -> int:
        return self.stamps[0].start

    @property
    def end(self) -> int:
        return self.stamps[-1].end

    def collect(self, filter: Callable[[Stamp], bool]) -> dict[str, int]:
        collected = defaultdict(int)
        for s in self.stamps:
            if (not filter(s)):
                continue
            collected[s.msg] += s.length
        return dict(collected)

    def tickets(self) -> dict[str, int]:
        return self.collect(lambda s: s.type == StampType.BILL and (s.msg == "MR" or s.msg.isdigit()))

    def bills(self) -> dict[str, int]:
        return self.collect(lambda s: s.type == StampType.BILL)


@dataclass
class Correction:
    total: int
    cors: dict[str, int]
