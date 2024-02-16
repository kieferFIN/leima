from argparse import ArgumentParser
from datetime import datetime

from lib.io import parse_time, read_stamps, write_corections
from lib.types import Correction


def ft(t: int) -> str:
    return f"{t//60}:{t%60:02d}"


def nearest(number: int, near: int = 15) -> int:
    return round(number/near)*near


def report(args):
    week_stamps = read_stamps(args.week)
    for day in week_stamps:
        times = day.times()
        for t, l in times.items():
            print(f"{t.name:<6}  {l:>3}")
        total = day.work_time
        print(f"total: {ft(total)}")
        print("****")


def correct(args):
    week_stamps = read_stamps(args.week)
    corrections = []
    for day in week_stamps:
        print(f"{ft(day.start)}-{ft(day.end)} -> {ft(day.end-day.start)}")
        print(f"total: {ft(day.work_time)}")
        tickets = day.tickets()
        new_total = parse_time(input("new total? "))
        more_time = new_total - day.work_time
        per_ticket = more_time // len(tickets)
        for msg, t in tickets.items():
            tickets[msg] = nearest(t+per_ticket)
        corrections.append(Correction(new_total, tickets))
    write_corections(args.week, corrections)


def main():
    current_week = datetime.now().isocalendar()[1]
    parser = ArgumentParser()
    sub_parsers = parser.add_subparsers()

    rep_parser = sub_parsers.add_parser('rep')
    rep_parser.add_argument(
        'week', type=int, default=current_week, nargs='?')
    rep_parser.set_defaults(func=report)

    cor_parser = sub_parsers.add_parser('cor')
    cor_parser.add_argument(
        'week', type=int, default=current_week, nargs='?')
    cor_parser.set_defaults(func=correct)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
