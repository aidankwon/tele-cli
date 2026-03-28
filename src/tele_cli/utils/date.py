from datetime import datetime, timedelta
from typing import Tuple

import re
import dateparser
from dateparser.search import search_dates

def parse_duration(duration_str: str) -> timedelta | None:
    match = re.match(r'^(\d+)([dwmy])$', duration_str.strip().lower())
    if not match:
        return None
    val = int(match.group(1))
    unit = match.group(2)
    if unit == 'd':
        return timedelta(days=val)
    elif unit == 'w':
        return timedelta(weeks=val)
    elif unit == 'm':
        return timedelta(days=val * 30)
    elif unit == 'y':
        return timedelta(days=val * 365)
    return None

def parse_date_range(
    from_str: str | None = None,
    to_str: str | None = None,
    range_str: str | None = None,
) -> Tuple[datetime | None, datetime | None]:
    date_from: datetime | None = None
    if from_str:
        parsed = dateparser.parse(from_str)
        if parsed:
            date_from = parsed.replace(hour=0, minute=0, second=0, microsecond=0)

    date_to: datetime | None = None
    if to_str:
        parsed = dateparser.parse(to_str)
        if parsed:
            date_to = parsed.replace(hour=23, minute=59, second=59, microsecond=0)

    date_span: list[datetime] | None = None
    if range_str and range_str == "this week":
        start_date = dateparser.parse("sunday")
        if start_date:
            date_span = [start_date, start_date + timedelta(days=6)]
    elif range_str:
        dates = search_dates(range_str, settings={"RETURN_TIME_SPAN": True}) or []
        if len(dates) == 2:
            # https://github.com/scrapinghub/dateparser/blob/cd5f226454e0ed3fe93164e7eff55b00f57e57c7/dateparser/search/search.py#L202
            start = next((x for (s, x) in dates if "start" in s), None)
            end = next((x for (s, x) in dates if "end" in s), None)
            if start and end:
                date_span = [start, end]

    if date_span:
        return (date_span[0], date_span[1])
    return (date_from, date_to)
