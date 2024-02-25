from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterator, TypeAlias


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
    label: str = ""
    extras: list[str] = field(default_factory=lambda: [])

    @property
    def length(self) -> int:
        return self.end - self.start


StampFilter: TypeAlias = Callable[[Stamp], bool]


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

    def collect(self, filter: StampFilter) -> dict[str, int]:
        collected = defaultdict(int)
        for s in self.stamps:
            if (not filter(s)):
                continue
            collected[s.label] += s.length
        return dict(collected)

    def tickets(self) -> dict[str, int]:
        return self.collect(lambda s: s.type == StampType.BILL and (s.label == "MR" or s.label.isdigit()))

    def bills(self) -> dict[str, int]:
        return self.collect(lambda s: s.type == StampType.BILL)

    def admins(self) -> dict[str, int]:
        return self.collect(lambda s: s.type == StampType.ADMIN)

    def non_bills(self) -> dict[str, int]:
        return self.collect(lambda s: s.type == StampType.NONBILL)

    def find_extras(self, filter: StampFilter) -> set[str]:
        return {e for s in self.stamps for e in s.extras if filter(s)}


@dataclass
class Correction:
    total: int
    cors: dict[str, int]


@dataclass
class CorrectedDay:
    workday: WorkDay
    correction: Correction | None

    @property
    def is_corrected(self) -> bool:
        return self.correction is not None

    @property
    def total(self) -> int:
        return self.correction.total if self.correction is not None else self.workday.work_time

    def corrected(self, filter: StampFilter) -> Iterator[tuple[str, int]]:
        for label, t in self.workday.collect(filter).items():
            if self.correction is not None:
                yield label, self.correction.cors.get(label) or t
            else:
                yield label, t

    def corrected_tickets(self) -> Iterator[tuple[str, int]]:
        return self.corrected(lambda s: s.type == StampType.BILL and (s.label == "MR" or s.label.isdigit()))

    def corrected_bills(self) -> Iterator[tuple[str, int]]:
        return self.corrected(lambda s: s.type == StampType.BILL)
