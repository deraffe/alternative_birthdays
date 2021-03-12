#!/usr/bin/env python3
import argparse
import datetime
import logging
from typing import Iterator

log = logging.getLogger(__name__)


def birthday_days(
    birthday: datetime.date,
    start: datetime.date,
    end: datetime.date,
    granularity: int = 100
) -> Iterator[tuple[int, datetime.date]]:
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
            yield days, date


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
    print(f'Day-birthdays for {birthday}')
    for days, date in birthday_days(birthday, today, future_threshold):
        print(days, date)


if __name__ == '__main__':
    main()
