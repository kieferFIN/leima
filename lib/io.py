from pathlib import Path
from lib.types import Correction, Stamp, StampType, WorkDay


def read_stamps(week: int) -> list[WorkDay]:
    week_stamps = []
    current_day = WorkDay()
    current_stamp = None
    with open(f"aikaleimat/{week:02d}.txt", 'r') as f:
        for line in f:
            line = line.strip()

            if len(line) == 0:
                week_stamps.append(current_day)
                current_day = WorkDay()
                current_stamp = None
            elif line[0] == '#':
                continue
            else:
                splitted = line.split(' ')
                t = parse_time(splitted[0])
                if current_stamp != None:
                    current_stamp.end = t
                    current_day.add(current_stamp)
                current_stamp = Stamp(t)
                if len(splitted) > 1:
                    current_stamp.type = StampType(splitted[1][0])
                    current_stamp.label = splitted[1][1:].replace("_", " ")
                    if len(splitted) > 2:
                        current_stamp.extras = [
                            s.replace("_", " ") for s in splitted[2:]]

    if len(current_day.stamps) > 0:
        week_stamps.append(current_day)

    return week_stamps


def write_corections(week: int, corrections: list[Correction]) -> None:
    with open(f"aikaleimat/{week:02d}c.txt", 'w') as f:
        for cor in corrections:
            if cor != None:
                f.write(f"{cor.total}\n")
                for msg, t in cor.cors.items():
                    f.write(f"{msg} {t}\n")
            f.write("\n")


def read_corrections(week: int) -> list[Correction] | None:
    ret = []
    current_total = 0
    current_cors: dict[str, int] = dict()
    file = Path(f"aikaleimat/{week:02d}c.txt")
    if not file.is_file():
        return None
    with file.open('r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                if current_total == 0:
                    ret.append(None)
                else:
                    ret.append(Correction(current_total, current_cors))
                current_total = 0
                current_cors = dict()
            elif line[0] == '#':
                continue
            else:
                splitted = line.split(' ')
                if len(splitted) == 1:
                    current_total = int(splitted[0])
                else:
                    current_cors[splitted[0]] = int(splitted[1])

    return ret


def parse_time(t: str) -> int:
    m = int(t[-2:])
    h = int(t[:-2])
    return h * 60 + m
