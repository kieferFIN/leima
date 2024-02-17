from argparse import ArgumentParser
from datetime import datetime

from lib.io import parse_time, read_corrections, read_stamps, write_corections
from lib.types import Correction


def ft(t: int) -> str:
    return f"{t//60}:{t%60:02d}"


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
        print(f"total: {ft(total)}")
        print("****")

    print(f"\nTOTAL: {ft(week_total)}")


def correct(args):
    week_stamps = read_stamps(args.week)
    old_corrections = read_corrections(args.week)
    if old_corrections == None:
        old_corrections = [None]*len(week_stamps)
    new_corrections = []
    for day, cor in zip(week_stamps, old_corrections):
        print(f"{ft(day.start)}-{ft(day.end)} -> {ft(day.end-day.start)}")
        print(f"total: {ft(day.work_time)}")
        if cor != None:
            print(f"previous correction {ft(cor.total)}")
        input_str = input("new total? ").strip()
        if len(input_str) == 0:
            new_corrections.append(cor)
            continue
        new_total = parse_time(input_str)
        tickets = day.tickets()
        more_time = new_total - day.work_time
        per_ticket = more_time // len(tickets)
        for msg, t in tickets.items():
            tickets[msg] = nearest(t+per_ticket)
        new_corrections.append(Correction(new_total, tickets))
    write_corections(args.week, new_corrections)


def psa(args):
    week_stamps = read_stamps(args.week)
    corrections = read_corrections(args.week)
    if corrections == None:
        corrections = [None]*len(week_stamps)
    for day, cor in zip(week_stamps, corrections):
        non_bill = sum(day.non_bills().values())
        admins = day.admins()
        s_admins = sum(admins.values())

        total = cor.total if cor != None else day.work_time
        bills = total - non_bill - s_admins
        print(f"B  {ft(bills)}")
        if non_bill > 0:
            print(f'NB {ft(non_bill)}')
        if s_admins > 0:
            print(f'A  {ft(s_admins)}')
            print(f"  {', '.join(admins)}")
        print("********")


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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
