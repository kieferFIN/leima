from __future__ import annotations
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


@dataclass(frozen=True)
class Time:
    value: int = 0

    def nearest(self, near: int = 15) -> Time:
        return Time(round(self.value/near)*near)

    def __sub__(self, other: int | Time) -> Time:
        if isinstance(other, int):
            return Time(self.value-other)
        return Time(self.value - other.value)

    def __add__(self, other: int | Time) -> Time:
        if isinstance(other, int):
            return Time(self.value + other)
        return Time(self.value + other.value)

    def __radd__(self, other: int | Time) -> Time:
        if isinstance(other, int):
            return Time(other+self.value)
        return other+self

    def __gt__(self, other: int) -> bool:
        return self.value > other

    def __floordiv__(self, number: int) -> Time:
        return Time(self.value//number)

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case 't':
                return f"{self.value//60}:{self.value%60:02d}"
            case 'h':
                return f"{(self.value/60):.2f}"
            case 'th':
                return f"{self:t} -- {self:h}"
            case _:
                return self.value.__format__(format_spec)


@dataclass
class Stamp:
    start: Time
    end: Time = None  # type: ignore
    type: StampType = StampType.EMPTY
    label: str = ""
    extras: list[str] = field(default_factory=lambda: [])

    @property
    def length(self) -> Time:
        return self.end - self.start


StampFilter: TypeAlias = Callable[[Stamp], bool]


@dataclass
class WorkDay:
    stamps: list[Stamp] = field(default_factory=lambda: [])

    def add(self, stamp: Stamp):
        self.stamps.append(stamp)

    @property
    def work_time(self) -> Time:
        total = Time()
        for s in self.stamps:
            if s.type != StampType.OFF:
                total += s.length
        return total

    def times(self) -> dict[StampType, Time]:
        times = defaultdict(Time)
        for s in self.stamps:
            times[s.type] += s.length
        return dict(times)

    @property
    def start(self) -> Time:
        return self.stamps[0].start

    @property
    def end(self) -> Time:
        return self.stamps[-1].end

    def collect(self, filter: StampFilter) -> dict[str, Time]:
        collected = defaultdict(Time)
        for s in self.stamps:
            if (not filter(s)):
                continue
            collected[s.label] += s.length
        return dict(collected)

    def tickets(self) -> dict[str, Time]:
        return self.collect(lambda s: s.type == StampType.BILL and (s.label == "MR" or s.label.isdigit()))

    def bills(self) -> dict[str, Time]:
        return self.collect(lambda s: s.type == StampType.BILL)

    def admins(self) -> dict[str, Time]:
        return self.collect(lambda s: s.type == StampType.ADMIN)

    def non_bills(self) -> dict[str, Time]:
        return self.collect(lambda s: s.type == StampType.NONBILL)

    def find_extras(self, filter: StampFilter) -> set[str]:
        return {e for s in self.stamps for e in s.extras if filter(s)}


@dataclass
class Correction:
    total: Time
    cors: dict[str, Time]


@dataclass
class CorrectedDay:
    workday: WorkDay
    correction: Correction | None

    @property
    def is_corrected(self) -> bool:
        return self.correction is not None

    @property
    def total(self) -> Time:
        return self.correction.total if self.correction is not None else self.workday.work_time

    def corrected(self, filter: StampFilter) -> Iterator[tuple[str, Time]]:
        for label, t in self.workday.collect(filter).items():
            if self.correction is not None:
                yield label, self.correction.cors.get(label) or t
            else:
                yield label, t

    def corrected_tickets(self) -> Iterator[tuple[str, Time]]:
        return self.corrected(lambda s: s.type == StampType.BILL and (s.label == "MR" or s.label.isdigit()))

    def corrected_bills(self) -> Iterator[tuple[str, Time]]:
        return self.corrected(lambda s: s.type == StampType.BILL)
