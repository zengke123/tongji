# 提供周报需要的前一周caps指标
import datetime
from util import db
from util.TxtParse import parseHtml
from util.file_exists import get_date_range


def get_week_caps():
    today = datetime.datetime.now().strftime("%Y%m%d")
    date_range = get_date_range(today, delta_day=7)
    rows = []
    row_title = ["日期","SCP","SCPAS","CATAS"]
    rows.append(row_title)
    for date in date_range:
        sql = "select * from caps where date = {}".format(date)
        result = db.select(sql)
        try:
            row = list(result[0])
        except IndexError:
            row = ["","","",""]
        rows.append(row)
    caps_html = parseHtml(rows, title="CAPS统计", return_all=False)
    return caps_html