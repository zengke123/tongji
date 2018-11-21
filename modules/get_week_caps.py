# 提供周报需要的前一周caps指标及短号短信指标
import datetime
from util import db
from util.TxtParse import parseHtml
from util.file_exists import get_date_range


def get_week_caps():
    today = datetime.datetime.now().strftime("%Y%m%d")
    # 获取日期区间
    date_range = get_date_range(today, delta_day=7)
    rows = []
    row_title = ["日期", "SCP", "SCPAS", "CATAS", "短号短信下发量", "短号彩信下发量"]
    rows.append(row_title)
    for date in date_range:
        caps_sql = "select date,scp_caps,scpas_caps,catas_caps from caps where date = {}".format(date)
        vss_sql = "select vss_total,mms_total from vss where date = {}".format(date)
        # 提取一周的caps数据
        caps_result = db.select(caps_sql)
        # 提取一周的短号短信数据
        vss_result = db.select(vss_sql)
        try:
            caps_row = list(caps_result[0])
        except IndexError:
            caps_row = [date, "", "", ""]
        try:
            vss_row = list(vss_result[0])
        except IndexError:
            vss_row = ["", ""]
        row = caps_row + vss_row
        rows.append(row)
    caps_html = parseHtml(rows, title="周报数据", return_all=False)
    return caps_html