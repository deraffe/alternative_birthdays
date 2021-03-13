#!/usr/bin/env python3
import argparse
import dataclasses
import datetime
import logging

log = logging.getLogger(__name__)

EARTH_ORBITAL_PERIOD = datetime.timedelta(days=365.256363004)


@dataclasses.dataclass
class TrueBirthday:
    birthday: datetime.datetime
    is_true: bool
    true_days: set[datetime.datetime]
    false_days: set[datetime.datetime]


def true_birthday(
    birthday: datetime.datetime,
    timespan: datetime.timedelta = None
) -> TrueBirthday:
    if timespan is None:
        timespan = datetime.timedelta(days=365 * 100)
    max_date = birthday + timespan
    cur_date = birthday
    true_days = set()
    false_days = set()
    log.debug(f'true_birthday({birthday=}, {timespan=})')
    is_true = True
    while cur_date <= max_date:
        cur_date += EARTH_ORBITAL_PERIOD
        log.debug(f'cur_date={cur_date:%F %H:%M:%S %z}')
        if cur_date.day == birthday.day:
            true_days.add(cur_date)
        else:
            false_days.add(cur_date)
            is_true = False
    if not is_true:
        log.debug(f'{birthday=} is false')
    return TrueBirthday(birthday, is_true, true_days, false_days)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loglevel', default='WARNING', help="Loglevel", action='store'
    )
    args = parser.parse_args()
    loglevel = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {}'.format(args.loglevel))
    logging.basicConfig(level=loglevel)
    start = datetime.datetime(1992, 1, 1, 12, 0)
    for i in range(365):
        bday = start + datetime.timedelta(days=1) * i
        log.info(f'{bday=}')
        truebday = true_birthday(bday)
        if truebday.is_true:
            print(bday)


if __name__ == '__main__':
    main()