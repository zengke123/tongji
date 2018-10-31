# 提取话单最大流水号
import config
from util.file_exists import file_exists, get_data


@file_exists(config.src_files.get('streamnumber'))
def get_streamnumber(filename):
    import re
    max_streamnumber = ""
    max_cluster = ""
    record_data = get_data(filename)
    for x in record_data:
        if re.match('scp[1-9]{3}', str(x[0])):
            max_cluster = x[0]
            max_streamnumber = x[1].strip("\n")
            break
    return max_cluster, max_streamnumber


@file_exists(config.src_files.get('scpas_streamnumber'))
def get_scpas_streamnumber(filename):
    record_data = get_data(filename)
    record_data.sort(key=lambda x: int(x[1]), reverse=True)
    max_cluster = record_data[0][0]
    max_streamnumber = record_data[0][1]
    return max_cluster, max_streamnumber