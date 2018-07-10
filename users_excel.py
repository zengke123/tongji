#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 生成每日用户数统计

import os
import re
import openpyxl
import logging
import datetime
import config


# 提取txt文本中数据，并处理成2维数组
def txt_list(txt_name):
    data = []
    logging.info("正在处理原始数据" + txt_name)
    file = open(txt_name, 'r')
    for line in file.readlines():
        line = line.strip('\n')
        line = re.split("[ |]", line)
        line_ret = [strs for strs in line if strs not in ['', '', None]]
        data.append(line_ret)
    file.close()
    return data


# 将数据写入excel文件中，字符串数字转换成浮点型
def data_xlsx(filename, xlsxname, data):
    logging.info("正在生成统计报表: " + xlsxname)
    wb = openpyxl.load_workbook(filename)
    ws = wb.get_sheet_by_name(u'原始数据')
    for i in range(len(data)):
        nums = len(data[i])
        for j in range(nums):
            try:
                data[i][j] = float(data[i][j])
            except ValueError:
                pass
            finally:
                ws.cell(row=i + 1, column=j + 1, value=data[i][j])
    wb.save(xlsxname)
    wb.close()


# 原始数据检测
def check(data_list, nums):
    if len(data_list) == nums:
        logging.info("检查原始数据正常")
        return True
    elif len(data_list) < nums:
        logging.info("原始数据缺失")
        return False
    elif len(data_list) > nums:
        logging.info("原始数据增多")
        return False


def main():
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    today = today.strftime("%Y%m%d")
    yesterday = yesterday.strftime("%Y%m%d")
    today1 = datetime.datetime.today().strftime("%Y-%m-%d")
    # input
    crbt_filename = config.USERS_PATH + "crbt-vpn.total." + str(today) + ".txt"
    sms_filename = config.USERS_PATH + "sms.total." + str(today) + ".txt"
    # output
    crbt_xlsxname = u'智能网和彩铃用户统计' + str(today) + '.xlsx'
    sms_xlsxname = u'短号短（彩）信业务统计' + str(yesterday) + '.xlsx'
    # 原始数据行数，用于检查数据是否缺失
    if os.path.exists(crbt_filename):
        crbt_list = txt_list(crbt_filename)
        if check(crbt_list, config.CRBT_VPMN_LINES):
            data_xlsx(filename='templates' + os.sep + 'crbt_vpn_tj.xlsx', xlsxname=crbt_xlsxname, data=crbt_list)
        else:
            logging.error("智能网和彩铃用户统计原始数据异常，需手工处理")
    else:
        logging.error(crbt_filename + "原始文件不存在")

    if os.path.exists(sms_filename):
        sms_list = txt_list(sms_filename)
        if check(sms_list, config.SMS_LINES):
            data_xlsx(filename='templates' + os.sep + 'sms_tj.xlsx', xlsxname=sms_xlsxname, data=sms_list)
        else:
            logging.error("短号短（彩）信业务统计原始数据异常，需手工处理")
    else:
        logging.error(sms_filename + "原始文件不存在")

    os.environ['today1'] = str(today1)
    os.environ['crbt_xlsxname'] = str(crbt_xlsxname)
    os.environ['sms_xlsxname'] = str(sms_xlsxname)
    if os.path.exists(crbt_xlsxname) and os.path.exists(sms_xlsxname):
        tar_cmd = 'tar zcf  tj.${today1}.tar.gz $crbt_xlsxname $sms_xlsxname --remove-files'
        os.system(tar_cmd)
    elif os.path.exists(crbt_xlsxname):
        tar_cmd = 'tar zcf  tj.${today1}.tar.gz $crbt_xlsxname --remove-files'
        os.system(tar_cmd)
    elif os.path.exists(sms_xlsxname):
        tar_cmd = 'tar zcf  tj.${today1}.tar.gz $sms_xlsxname --remove-files'
        os.system(tar_cmd)


if __name__ == '__main__':
    main()
    logging.info("Done.")
