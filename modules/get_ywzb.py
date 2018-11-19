# 每日统计中业务指标,响应率\接通率等
import config
import logging
import datetime
from util import db
from util.file_exists import file_exists, get_data


@file_exists(config.src_files.get('ywzb'))
def get_ywzb(filename):
    # list用于生成html格式
    ywzb_data = []
    # 数据入库使用，根据数据库表字段匹配ywzb_dict中的key
    # ywzb_dict从原始数据中读取的业务指标
    ywzb_dict = {}
    # 入库的格式
    ywzb_db = {}
    yesterday = (datetime.date.today() - datetime.timedelta(days=1))
    ywzb_db['date']= yesterday.strftime("%Y%m%d")
    for x in get_data(filename):
        try:
            x.remove('')
        except ValueError:
            pass
        zb_name_id = x[0].strip(' ')
        zb_name = config.ywzb_tilte.get(zb_name_id, zb_name_id)
        if len(x) != 3:
            value = [zb_name, '', '']
        else:
            zb_cluster = x[1].strip(' ')
            zb_value = x[2].strip(' ')
            value = [zb_name, zb_cluster, zb_value]
            ywzb_dict[zb_name_id] = [zb_cluster, zb_value]
        ywzb_data.append(value)
    # 数据入库
    try:
        # 需要入库的数据，匹配数据库表字段
        for k, v in ywzb_dict.items():
            # 指标名称未在config配置,即数据库中无该字段
            if k not in config.ywzb_tilte.keys():
                logging.error('业务指标 ' + k + " 未配置,需添加对应表字段")
            else:
                ywzb_db[k] = ywzb_dict.get(k)[1]
                ywzb_db[k+"_cluster"] = ywzb_dict.get(k)[0]
        db.insert("ywzb", **ywzb_db)
    except Exception as e:
        logging.error("业务指标数据入库错误" + str(e))
    return ywzb_data, ywzb_dict