#!/usr/bin/env python3
import argparse
import datetime
import logging
from typing import Callable, Iterator

log = logging.getLogger(__name__)


def birthday_hours(
    birthday: datetime.date,
    start: datetime.date,
    end: datetime.date,
    granularity: int = 10000
) -> Iterator[tuple[datetime.date, str]]:
    hour_start = (start - birthday).total_seconds() / (60 * 60)
    hour_end = (end - birthday).total_seconds() / (60 * 60)
    for i in range(1, 120):
        hours = i * granularity
        if hours < hour_start:
            continue
        if hours > hour_end:
            break
        date = birthday + datetime.timedelta(hours=hours)
        if start < date < end:
            yield date, f"{hours} hours"


def birthday_days(
    birthday: datetime.date,
    start: datetime.date,
    end: datetime.date,
    granularity: int = 100
) -> Iterator[tuple[datetime.date, str]]:
    day_start = (start - birthday).total_seconds() / (60 * 60 * 24)
    day_end = (end - birthday).total_seconds() / (60 * 60 * 24)
    for i in range(1, 500):
        days = i * granularity
        if days < day_start:
            continue
        if days > day_end:
            break
        date = birthday + datetime.timedelta(days=days)
        if start < date < end:
            yield date, f"{days} days"


def birthday_planet(
    planet_name: str,
    orbital_period: datetime.timedelta,
    granularity: float = 1.0
) -> Callable:
    range_end = datetime.timedelta(days=50000
                                   ) // (orbital_period * granularity)

    def bday_planet(
        birthday: datetime.date,
        start: datetime.date,
        end: datetime.date,
        granularity: float = granularity
    ) -> Iterator[tuple[datetime.date, str]]:
        planet_start = (start - birthday) / orbital_period
        planet_end = (end - birthday) / orbital_period
        for i in range(1, range_end):
            pyears = i * granularity
            if pyears < planet_start:
                continue
            if pyears > planet_end:
                break
            date = birthday + pyears * orbital_period
            if start < date < end:
                if granularity < 1:
                    description = f"{pyears:.2f} {planet_name} years"
                else:
                    description = f"{pyears:.0f} {planet_name} years"
                yield date, description

    return bday_planet


birthday_generators = [
    birthday_hours,
    birthday_days,
    birthday_planet('Mercury', datetime.timedelta(seconds=7600530.24)),
    birthday_planet('Venus', datetime.timedelta(seconds=19414166.4)),
    birthday_planet('Earth', datetime.timedelta(seconds=31558149.7635)),
    birthday_planet('Mars', datetime.timedelta(seconds=59354294.4)),
    birthday_planet('Jupiter', datetime.timedelta(seconds=374335776), 0.1),
    birthday_planet('Saturn', datetime.timedelta(seconds=929596608), 0.01),
    birthday_planet('Uranus', datetime.timedelta(seconds=2651486400), 0.01),
    birthday_planet('Neptune', datetime.timedelta(seconds=5199724800), 0.01),
    birthday_planet('Pluto', datetime.timedelta(seconds=7824384000), 0.01),
]


def parse_date(input_str: str) -> datetime.date:
    year, month, day = input_str.split('-', 2)
    date = datetime.date(int(year), int(month), int(day))
    return date


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument('birthday', help='Birthday in ISO format (YYYY-MM-DD)')
    parser.add_argument(
        '--start', help='start date in ISO format (YYYY-MM-DD)'
    )
    parser.add_argument('--end', help='end date in ISO format (YYYY-MM-DD)')
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)

    birthday = parse_date(args.birthday)
    today = datetime.date.today()
    if args.start:
        start = parse_date(args.start)
    else:
        start = today
    if args.end:
        end = parse_date(args.end)
    else:
        end = today + datetime.timedelta(days=365 * 5)
    birthday_list: list[tuple[datetime.date, str]] = list()
    for generator in birthday_generators:
        birthday_list += list(generator(birthday, start, end))
    for date, description in sorted(birthday_list):
        print(date, description)


if __name__ == '__main__':
    main()
