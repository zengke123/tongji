import datetime
from util import db


def get_data_by_node(cluters):
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    result = {}
    for x in cluters:
        cluter = x.split('-')[1]
        sql = "select max_cpu from as_pfmc where cluste='{}' and date='{}'".format(cluter, yesterday)
        data = db.select(sql)
        if data:
            result[x] = data[0][0]
        else:
            result[x] = 0
    return result


def wirte_cpu_to_excle(cluters, ws, col, row):
    cpu_dict = get_data_by_node(cluters)
    if cpu_dict:
        for i, x in enumerate(cluters):
            ws.cell(row=row + i, column=col, value=(cpu_dict.get(x)/100))

