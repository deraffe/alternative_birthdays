#!/usr/bin/env python3
import argparse
import datetime
import logging
import os
import sys
import zoneinfo
from typing import Callable, Iterator
from dataclasses import dataclass

log = logging.getLogger(__name__)

MORE_THAN_A_LIFETIME = datetime.timedelta(days=50000)


@dataclass
class Birthday:
    date: datetime.datetime
    age: float
    description: str

def birthday_timeunit(
    unit_name: str, seconds: int, decimal_digits: int = 0
) -> Callable:
    granularity = 1 / (10**decimal_digits)
    range_end = MORE_THAN_A_LIFETIME // (
        datetime.timedelta(seconds=seconds) * granularity
    )

    def bday_time(
        birthday: datetime.datetime,
        start: datetime.datetime,
        end: datetime.datetime,
        granularity: float = granularity
    ) -> Iterator[Birthday]:
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
                yield Birthday(date=date, age=units, description=description)

    return bday_time


def birthday_planet(
    planet_name: str,
    orbital_period: datetime.timedelta,
    decimal_digits: int = 0
) -> Callable:
    granularity = 1 / (10**decimal_digits)
    range_end = datetime.timedelta(days=50000
                                   ) // (orbital_period * granularity)

    def bday_planet(
        birthday: datetime.datetime,
        start: datetime.datetime,
        end: datetime.datetime,
        granularity: float = granularity
    ) -> Iterator[Birthday]:
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
                yield Birthday(date=date, age=pyears, description=description)

    return bday_planet


birthday_generators = [
    birthday_timeunit('seconds', 1, -7),
    birthday_timeunit('minutes', 60, -6),
    birthday_timeunit('hours', 60 * 60, -4),
    birthday_timeunit('days', 60 * 60 * 24, -2),
    birthday_timeunit('weeks', 60 * 60 * 24 * 7, -2),
    birthday_planet('Mercury', datetime.timedelta(seconds=7600530.24)),
    birthday_planet('Venus', datetime.timedelta(seconds=19414166.4)),
    birthday_planet('Earth', datetime.timedelta(days=365.256363004)),
    birthday_planet('Mars', datetime.timedelta(seconds=59354294.4)),
    birthday_planet('Jupiter', datetime.timedelta(seconds=374335776), 1),
    birthday_planet('Saturn', datetime.timedelta(seconds=929596608), 1),
    birthday_planet('Uranus', datetime.timedelta(seconds=2651486400), 2),
    birthday_planet('Neptune', datetime.timedelta(seconds=5199724800), 2),
    birthday_planet('Pluto', datetime.timedelta(seconds=7824384000), 2),
]


@dataclass
class Parameters:
    birthday: datetime.datetime
    today: datetime.datetime
    input_timezone: datetime.tzinfo
    output_timezone: datetime.tzinfo


def set_default_subparser(self, name, args=None, index=None):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    https://stackoverflow.com/a/26379693
    """
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
        if not subparser_found:
            if args is None:
                log.debug(f"{sys.argv=}")
                sys.argv.insert(index or 1, name)
                log.debug(f"{sys.argv=}")
            else:
                args.insert(index or 1, name)


def parse_date(
    input_str: str, timezone: zoneinfo.ZoneInfo
) -> datetime.datetime:
    year, month, day = input_str.split('-', 2)
    date = datetime.datetime(
        int(year), int(month), int(day), 12, 0, tzinfo=timezone
    )
    return date


def parse_datetime(
    input_str: str, timezone: zoneinfo.ZoneInfo
) -> datetime.datetime:
    datestr, timestr = input_str.split(' ', 1)
    date = parse_date(datestr, timezone)
    hour, minute = timestr.split(':', 1)
    date = date.replace(hour=int(hour), minute=int(minute))
    return date


def _birthdays(birthday, start, end) -> Iterator[Birthday]:
    for generator in birthday_generators:
        yield from generator(birthday, start, end)


def birthdays(args, params: Parameters) -> None:
    itz = params.input_timezone
    today = params.today
    birthday = params.birthday
    otz = params.output_timezone
    if args.start:
        start = parse_date(args.start, itz)
    else:
        start = today
    if args.end:
        end = parse_date(args.end, itz)
    else:
        end = today + datetime.timedelta(days=365 * 3)
    birthday_list: list[Birthday] = list(_birthdays(birthday, start, end))
    for b in sorted(birthday_list, key=lambda b: b.date):
        odate = b.date.astimezone(tz=otz)
        print(f"{odate:%F %H:%M %z} {b.description}")


def _configure_common_options(parser: argparse.ArgumentParser) -> None:
    local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    supported_timezones = sorted(list(zoneinfo.available_timezones()))
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    parser.add_argument(
        "birthday", help="Birthday in ISO format (YYYY-MM-DD HH:MM), time is optional"
    )
    parser.add_argument(
        '--input-timezone',
        type=str,
        default=local_tz,
        choices=supported_timezones,
        help=f'Input timezone (default: {local_tz})'
    )
    parser.add_argument(
        '--output-timezone',
        type=str,
        default=local_tz,
        choices=supported_timezones,
        help=f'Output timezone (default: {local_tz})'
    )


def main():
    if "DEBUG" in os.environ:
        logging.basicConfig(level=logging.DEBUG)
    argparse.ArgumentParser.set_default_subparser = set_default_subparser
    main_parser = argparse.ArgumentParser()
    subparsers = main_parser.add_subparsers()

    birthdays_parser = subparsers.add_parser(
        "birthdays", help="Display birthdays in a range"
    )
    _configure_common_options(birthdays_parser)
    birthdays_parser.set_defaults(func=birthdays)
    birthdays_parser.add_argument(
        "--start", help="start date in ISO format (YYYY-MM-DD)"
    )
    birthdays_parser.add_argument("--end", help="end date in ISO format (YYYY-MM-DD)")

    main_parser.set_default_subparser("birthdays")
    args = main_parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)

    def get_tz(tz: str | datetime.tzinfo):
        if isinstance(tz, datetime.tzinfo):
            return tz
        else:
            return zoneinfo.ZoneInfo(tz)

    itz = get_tz(args.input_timezone)
    otz = get_tz(args.output_timezone)

    if ':' in args.birthday:
        log.debug('birthday has time')
        birthday = parse_datetime(args.birthday, itz)
    else:
        log.debug('birthday is blank date, assuming 12:00')
        birthday = parse_date(args.birthday, itz)
    log.debug(f'{birthday=}')
    today = datetime.datetime.now(tz=itz)
    log.debug(f'{today=}')

    params = Parameters(
        birthday=birthday, today=today, input_timezone=itz, output_timezone=otz
    )
    args.func(args, params)


if __name__ == '__main__':
    main()
