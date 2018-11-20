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


# 根据关键字 keywords 从 file 中提取文本块
def blocks(file, keywords):
    block = []
    # 文本提取标志
    flag = False
    for line in lines(file):
        if keywords in line:
            flag = True
            continue
        if flag:
            # 以30个"-"作为文本块结束
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
        # 提取一周活性用户数
        hx_user_temp = blocks(file, keywords="hx_user")
        hx_user = float(hx_user_temp[-1].split(" ")[0])
        # 提取短号短信总下发量
        vss_data = blocks(file, keywords="---VSS")
        vss_total = sum([float(x.split(" ")[-1]) for x in vss_data[1:]])
        # 提取短号彩信总下发量
        mms_data = blocks(file, keywords="---MMS")
        mms_total = sum([float(x.split(" ")[-1]) for x in mms_data[1:]])
        # 数据入库
        vss_db['hx_user'] = hx_user
        vss_db['vss_total'] = vss_total
        vss_db['mms_total'] = mms_total
    try:
        db.insert(table="vss", **vss_db)
    except Exception as e:
        logging.error("短号短信数据入库失败： " + str(e))

