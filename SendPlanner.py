import calendar
import threading
import time

import pandas as pd
import datetime
from datetime import datetime
from dateutil.parser import parse
from flask import json

import DataLoader


def create_send_dates(since, period=None, period_type=None, until=None):
    frequencies = {
        'day': 'D',
        'week': 'W',
        'month': 'ME',
        'year': 'YE'
    }
    if period_type is not None and until is not None and frequencies.__contains__(period_type):
        series = {
            'day': [date.strftime("%Y-%m-%d") for date in pd.date_range(start=since, end=until, freq='D')],
            'week': [date.strftime("%Y-%m-%d") for date in pd.date_range(start=since, end=until, freq='W')],
            'month': [date.strftime("%Y-%m-") + str(pd.to_datetime(since).day) for date in
                      pd.date_range(start=since, end=until, freq='ME')],
            'year': [str(date.year) + '-' + str(pd.to_datetime(since).month) + '-' + str(pd.to_datetime(since).day) for
                     date in pd.date_range(start=since, end=until, freq='YE')],
        }
        series = series[period_type]
        if period_type == 'month':
            tmp = list()
            for pos_date in series:
                try:
                    parse(pos_date)
                    tmp.append(pos_date)
                except ValueError:
                    year = int(pos_date[:4])
                    tmp.append(datetime(year, 2, 29 if calendar.isleap(year) else 28).strftime("%Y-%m-%d"))
            series = tmp
        if period is not None and period != 1:
            series = limit_dates(series, period)
        return series
    else:
        return [since]


def limit_dates(dates, every):
    counter = 1
    tmp = [dates[0]]
    while counter < len(dates):
        counter += every
        if counter < len(dates):
            tmp.append(dates[counter])
    return tmp


def is_today(date):
    return datetime.today().strftime("%Y-%m-%d") == date


def today(hour=15, minute=0, second=0, without_hour=False):
    date = datetime.today()
    date = date.strftime("%Y-%m-%d")
    if without_hour:
        return date
    hour = str(hour) if hour is not None and type(hour) is int and hour // 24 == 0 else '00'
    minute = str(minute) if minute is not None and type(minute) is int and minute // 60 == 0 else '00'
    second = str(second) if second is not None and type(second) is int and second // 60 == 0 else '00'
    date += ' ' + ('0' if len(hour) == 1 else '') + hour + (':0' if len(minute) == 1 else ':') + minute + (
        ':0' if len(second) == 1 else ':') + second
    return date


def tomorrow(hour=15, minute=0, second=0, without_hour=False):
    date = today(hour=hour, minute=minute, second=second, without_hour=without_hour)
    parts = date.split(' ')
    date = parse(parts[0])
    date += pd.Timedelta(days=1)
    date = date.strftime("%Y-%m-%d")
    if without_hour:
        return date
    else:
        return date + ' ' + parts[1]


def seconds_until_next_run(hour=15, minute=0, second=0):
    now = datetime.today()
    pos_today = parse(today(hour=hour, minute=minute, second=second))
    pos_tomorrow = parse(tomorrow(hour=hour, minute=minute, second=second))
    if now > pos_today:
        remaining = (pos_tomorrow - now).total_seconds()
        print(f'next run in {remaining}s at {pos_tomorrow}')
        return remaining
    else:
        remaining = (pos_today - now).total_seconds()
        print(f'next run in {remaining}s at {pos_today}')
        return remaining


class SendPlanner:
    def __init__(self, hour=15, minute=0, second=0):
        self.auto_sends = DataLoader.load_auto_sends()
        self.send_hour = hour
        self.send_minute = minute
        self.send_second = second
        self.send_loop = threading.Thread(target=lambda: self.send_wishes())
        self.send_loop.start()
        self.discord_bot = None

    def send_wishes(self):
        while True:
            remaining = seconds_until_next_run(hour=self.send_hour, minute=self.send_minute, second=self.send_second)
            time.sleep(remaining)
            print(f'it\'s {self.send_hour}:{self.send_minute}:{self.send_second}')
            for_today = self.get_planned_for_today()
            self.send_via_discord(for_today)

    def get_planned_for_today(self):
        return [plan for plan in self.auto_sends if [date for date in plan['dates'] if is_today(date)].__len__() >= 1]

    def save_plan(self, data: json):
        plan = {
            'user': data['username'],
            'dates': create_send_dates(data['date'], period=int(data['period']), period_type=data['period_type'],
                                       until=data['until']),
            'receiver': dict(),
            'wish_lines': data['wish_content'].split('\n')
        }
        if data['platforms'].__contains__('Discord'):
            plan['receiver']['Discord'] = data[
                'discord_id']  # {'discord_id': data['discord_id']} if we wanted to store more data, however we need only id therefore we're saving only a string
        DataLoader.save_auto_send(plan)
        self.auto_sends.append(plan)

    def send_via_discord(self, to_send):
        if self.discord_bot is None:
            print('Discord bot not linked to planner, sending aborted')
            return
        to_send = [plan for plan in to_send if plan['receiver'].__contains__('Discord')]
        for plan in to_send:
            discord_id = plan['receiver']['Discord']
            wish = ''
            for line in plan['wish_lines']:
                wish += line
            result = self.discord_bot.send(discord_id, wish)
            print(f'{discord_id}: {result}')
        print(f'{len(to_send)} wishes sent via Discord')

    def get_planned_by(self, user):
        return [plan for plan in self.auto_sends if plan['user'] == user]
