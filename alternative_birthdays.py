#!/usr/bin/env python3
import argparse
import datetime
import logging
from typing import Callable, Iterator

log = logging.getLogger(__name__)

MORE_THAN_A_LIFETIME = datetime.timedelta(days=50000)


def birthday_timeunit(
    unit_name: str, seconds: int, granularity: int = 1
) -> Callable:
    range_end = MORE_THAN_A_LIFETIME // (
        datetime.timedelta(seconds=seconds) * granularity
    )

    def bday_time(
        birthday: datetime.datetime,
        start: datetime.datetime,
        end: datetime.datetime,
        granularity: float = granularity
    ) -> Iterator[tuple[datetime.datetime, str]]:
        time_start = (start - birthday).total_seconds() / seconds
        time_end = (end - birthday).total_seconds() / seconds
        for i in range(1, range_end):
            units = i * granularity
            if units < time_start:
                continue
            if units > time_end:
                break
            date = birthday + units * datetime.timedelta(seconds=seconds)
            if start < date < end:
                if granularity < 0.1:
                    description = f"{units:.2f} {unit_name}"
                elif granularity < 1:
                    description = f"{units:.1f} {unit_name}"
                else:
                    description = f"{units:.0f} {unit_name}"
                yield date, description

    return bday_time


def birthday_planet(
    planet_name: str,
    orbital_period: datetime.timedelta,
    granularity: float = 1.0
) -> Callable:
    range_end = datetime.timedelta(days=50000
                                   ) // (orbital_period * granularity)

    def bday_planet(
        birthday: datetime.datetime,
        start: datetime.datetime,
        end: datetime.datetime,
        granularity: float = granularity
    ) -> Iterator[tuple[datetime.datetime, str]]:
        planet_start = (start - birthday) / orbital_period
        planet_end = (end - birthday) / orbital_period
        for i in range(1, range_end):
            pyears = i * granularity
            if pyears < planet_start:
                continue
            if pyears > planet_end:
                break
            time_passed = pyears * orbital_period
            date = birthday + time_passed
            log.debug(
                f'{birthday=} {granularity=} {i=} {pyears=} {date=} {planet_name=} {time_passed=}'
            )
            if start < date < end:
                if granularity < 0.1:
                    description = f"{pyears:.2f} {planet_name} years"
                elif granularity < 1:
                    description = f"{pyears:.1f} {planet_name} years"
                else:
                    description = f"{pyears:.0f} {planet_name} years"
                yield date, description

    return bday_planet


birthday_generators = [
    birthday_timeunit('seconds', 1, 10000000),
    birthday_timeunit('minutes', 60, 1000000),
    birthday_timeunit('hours', 60 * 60, 10000),
    birthday_timeunit('days', 60 * 60 * 24, 100),
    birthday_timeunit('weeks', 60 * 60 * 24 * 7, 100),
    birthday_planet('Mercury', datetime.timedelta(seconds=7600530.24)),
    birthday_planet('Venus', datetime.timedelta(seconds=19414166.4)),
    birthday_planet('Earth', datetime.timedelta(days=365.256363004)),
    birthday_planet('Mars', datetime.timedelta(seconds=59354294.4)),
    birthday_planet('Jupiter', datetime.timedelta(seconds=374335776), 0.1),
    birthday_planet('Saturn', datetime.timedelta(seconds=929596608), 0.1),
    birthday_planet('Uranus', datetime.timedelta(seconds=2651486400), 0.01),
    birthday_planet('Neptune', datetime.timedelta(seconds=5199724800), 0.01),
    birthday_planet('Pluto', datetime.timedelta(seconds=7824384000), 0.01),
]


def parse_date(input_str: str) -> datetime.datetime:
    year, month, day = input_str.split('-', 2)
    date = datetime.datetime(int(year), int(month), int(day), 12, 0)
    return date


def parse_datetime(input_str: str) -> datetime.datetime:
    datestr, timestr = input_str.split(' ', 1)
    date = parse_date(datestr)
    hour, minute = timestr.split(':', 1)
    date = date.replace(hour=int(hour), minute=int(minute))
    return date


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument(
        'birthday',
        help='Birthday in ISO format (YYYY-MM-DD HH:MM), time is optional'
    )
    parser.add_argument(
        '--start', help='start date in ISO format (YYYY-MM-DD)'
    )
    parser.add_argument('--end', help='end date in ISO format (YYYY-MM-DD)')
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)

    if ':' in args.birthday:
        log.debug('birthday has time')
        birthday = parse_datetime(args.birthday)
    else:
        log.debug('birthday is blank date, assuming 12:00')
        birthday = parse_date(args.birthday)
    today = datetime.datetime.today()
    if args.start:
        start = parse_date(args.start)
    else:
        start = today
    if args.end:
        end = parse_date(args.end)
    else:
        end = today + datetime.timedelta(days=365 * 3)
    birthday_list: list[tuple[datetime.datetime, str]] = list()
    for generator in birthday_generators:
        birthday_list += list(generator(birthday, start, end))
    for date, description in sorted(birthday_list):
        print(f"{date:%F %H:%M %z} {description}")


if __name__ == '__main__':
    main()
