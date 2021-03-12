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
    hour_start = (start - birthday).days * 24
    hour_end = (end - birthday).days * 24
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
    day_start = (start - birthday).days
    day_end = (end - birthday).days
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
    planet_name: str, orbital_period: datetime.timedelta
) -> Callable:
    granularity = 1
    range_end = datetime.timedelta(days=50000) // orbital_period

    def bday_planet(
        birthday: datetime.date,
        start: datetime.date,
        end: datetime.date,
        granularity: int = granularity
    ) -> Iterator[tuple[datetime.date, str]]:
        planet_start = (start - birthday) // orbital_period
        planet_end = (end - birthday) // orbital_period
        for i in range(1, range_end):
            pyears = i * granularity
            if pyears < planet_start:
                continue
            if pyears > planet_end:
                break
            date = birthday + pyears * orbital_period
            if start < date < end:
                yield date, f"{pyears} {planet_name} years"

    return bday_planet


birthday_generators = [
    birthday_hours, birthday_days,
    birthday_planet('Mercury', datetime.timedelta(seconds=7600530.24)),
    birthday_planet('Venus', datetime.timedelta(seconds=19414166.4)),
    birthday_planet('Earth', datetime.timedelta(seconds=31558149.7635))
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument('birthday', help='Birthday in ISO format (YYYY-MM-DD)')
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)
    bday_year, bday_month, bday_day = args.birthday.split('-', 2)
    birthday = datetime.date(int(bday_year), int(bday_month), int(bday_day))
    today = datetime.date.today()
    future_threshold = today + datetime.timedelta(days=365 * 5)
    birthday_list: list[tuple[datetime.date, str]] = list()
    for generator in birthday_generators:
        birthday_list += list(generator(birthday, today, future_threshold))
    for date, description in sorted(birthday_list):
        print(date, description)


if __name__ == '__main__':
    main()
