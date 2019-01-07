# 获取每套网元的caps指标
# 数据来源 dailycaps.unl
import config
import logging
from util.file_exists import file_exists, get_data


@file_exists(config.src_files.get('dailycaps'))
def get_dailycaps(filename):
    caps = get_data(filename)
    caps_dict = {}
    for x in caps:
        try:
            x.remove('')
        except ValueError:
            pass
        caps_dict[x[0]] = float(x[1])
    return caps_dict


def wirte_caps_to_excle(cluters, ws, col, row):
    caps_dict = get_dailycaps()
    # dailycaps中数据不为空，填入日报excel
    if caps_dict:
        for i, x in enumerate(cluters):
            ws.cell(row=row + i, column=col, value=x)
            ws.cell(row=row + i, column=col + 1, value=caps_dict.get(x))
            ws.cell(row=row + i, column=col + 2, value=config.caps_capacity.get(x))
            try:
                ws.cell(row=row + i, column=col + 3,
                        value=format(caps_dict.get(x)/config.caps_capacity.get(x),'.2%'))
            except Exception as e:
                logging.error(str(e))




