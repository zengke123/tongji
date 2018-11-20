# 获取短号短信及短号彩信下发量
import config
import datetime
import logging
from util import db
from util.file_exists import file_exists


def lines(file):
    for line in file:
        line = line.strip('\t\n')
        yield line


def blocks(file, keywords):
    block = []
    flag = False
    for line in lines(file):
        if keywords in line:
            flag = True
            continue
        if flag:
            if "-"*30 in line:
                break
            else:
                block.append(line)
    return block


@file_exists(config.src_files.get('vsstj'))
def get_vsstj(filename):
    vss_db = {}
    yesterday = (datetime.date.today() - datetime.timedelta(days=1))
    vss_db['date'] = yesterday.strftime("%Y%m%d")
    with open(filename) as file:
        hx_user_temp = blocks(file, keywords="hx_user")
        hx_user = float(hx_user_temp[-1].split(" ")[0])
        vss_data = blocks(file, keywords="---VSS")
        vss_total = sum([float(x.split(" ")[-1]) for x in vss_data[1:]])
        mms_data = blocks(file, keywords="---MMS")
        mms_total = sum([float(x.split(" ")[-1]) for x in mms_data[1:]])
        vss_db['hx_user'] = hx_user
        vss_db['vss_total'] = vss_total
        vss_db['mms_total'] = mms_total
    try:
        db.insert(table="vss", **vss_db)
    except Exception as e:
        logging.error("短号短信数据入库失败： " + str(e))

