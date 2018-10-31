# 提取caps指标
import config
import datetime
import logging
from util import db
from util.file_exists import file_exists, get_data


@file_exists(config.src_files.get('caps'))
def get_caps(filename):
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    caps_data = []
    caps_db = {}
    record_data = get_data(filename)
    for value in record_data:
        caps_name = config.caps_tilte.get(value[0])
        try:
            caps_value = float(value[1])
        except ValueError:
            # 跳过数据为空
            caps_value = ""
        caps_data.append([caps_name, caps_name.split('_')[0].upper(), caps_value])
        caps_db[caps_name] = caps_value
    caps_db['date'] = yesterday
    try:
        db.insert("caps",**caps_db)
    except Exception as e:
        logging.error("CAPS数据入库错误" + str(e))
    return caps_data