from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime

from lib.io import parse_time, read_data, read_stamps, write_corections
from lib.types import Correction


WEEKDAYS = ["MA", "TI", "KE", "TO", "PE"]


def time(t: int) -> str:
    return f"{t//60}:{t%60:02d}"


def hours(t: int) -> str:
    return f"{(t/60):.2f}"


def both(t: int) -> str:
    return f"{time(t)} -- {hours(t)}"


def nearest(number: int, near: int = 15) -> int:
    return round(number/near)*near


def report(args):
    week_stamps = read_stamps(args.week)
    week_total = 0
    for day in week_stamps:
        times = day.times()
        for t, l in times.items():
            print(f"{t.name:<6}  {l:>3}")
        total = day.work_time
        week_total += total
        print(f"total: {both(total)}")
        print("****")

    print(f"\nTOTAL: {both(week_total)}")


def correct(args):

    new_corrections = []
    for data, day in zip(read_data(args.week), WEEKDAYS):
        print(day)
        print(f"{time(data.workday.start)}-{time(data.workday.end)} -> {both(data.workday.end-data.workday.start)}")
        print(f"total: {both(data.workday.work_time)}")
        if data.is_corrected:
            print(f"previous correction {time(data.correction.total)}")  # type: ignore
        input_str = input("new total? ").strip()
        if len(input_str) == 0:
            new_corrections.append(data.correction)
            continue
        new_total = parse_time(input_str)
        tickets = data.workday.tickets()
        more_time = new_total - data.workday.work_time
        per_ticket = more_time // len(tickets)
        for msg, t in tickets.items():
            tickets[msg] = nearest(t+per_ticket)
        new_corrections.append(Correction(new_total, tickets))
    write_corections(args.week, new_corrections)


def psa(args):
    for data, day_name in zip(read_data(args.week), WEEKDAYS):
        print(day_name)
        non_bill = sum(data.workday.non_bills().values())
        admins = data.workday.admins()
        s_admins = sum(admins.values())

        total = data.total
        bills = total - non_bill - s_admins
        print(f"B  {both(bills)}")
        if non_bill > 0:
            print(f'NB {both(non_bill)}')
        if s_admins > 0:
            print(f'A  {both(s_admins)}')
            for label, t in admins.items():
                print(f"    {label:<10}   {both(t)}")
                extras = data.workday.find_extras(lambda s: s.label is label)
                if len(extras) > 0:
                    print(f"    {','.join(extras)}")

        print("********")


def jir(args):
    tickets = defaultdict(lambda: [[0]*5 for _ in range(len(args.weeks))])
    for w, week in enumerate(args.weeks):
        for i, data in enumerate(read_data(week)):
            for label, t in data.corrected_tickets():
                tickets[label][w][i] = t

    for label, data in tickets.items():
        print(label)
        for w, times in zip(args.weeks, data):
            print(f"{w}:  {'  '.join([hours(t) for t in times])}")


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

    psa_parser = sub_parsers.add_parser('psa')
    psa_parser.add_argument(
        'week', type=int, default=current_week, nargs='?')
    psa_parser.set_defaults(func=psa)

    jir_parser = sub_parsers.add_parser("jir")
    jir_parser.add_argument(
        'weeks', type=int, default=current_week, nargs='*')
    jir_parser.set_defaults(func=jir)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
