import os
import logging
import datetime
from functools import wraps


def file_exists(filename):
    def decorate(func):
        @wraps(func)
        def wrapper():
            if os.path.exists(filename):
                return func(filename)
            else:
                logging.error(filename + "文件不存在")
        return wrapper
    return decorate


def get_data(unl):
    with open(unl, "r") as f:
        lines = f.readlines()
        data = [line.strip("\n").split("|") for line in lines]
    for x in data:
        try:
            x.remove("\n")
        except ValueError:
            pass
    return data


def get_date_range(end_date, delta_day):
    # 转为datetime格式，用于日期计算，str格式无法计算
    begin_date = datetime.datetime.strptime(end_date, "%Y%m%d") - datetime.timedelta(delta_day)
    dates = []
    dt = begin_date
    date = begin_date.strftime("%Y%m%d")
    while date < end_date:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y%m%d")
    return dates
