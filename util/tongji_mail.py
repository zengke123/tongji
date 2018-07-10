#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import datetime
import logging
from MailSender import MailSender
from collections import namedtuple


def check_file(filename):
    File = namedtuple("File", "name is_exist")
    return File(filename, True) if os.path.exists(filename) else File(filename, False)


def logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filename="mail.log")

if __name__ == "__main__":
    logger()
    date = datetime.date.today().strftime("%Y%m%d")
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    logging.info(" 开始发送每日统计邮件")
    filename_xlsx = "tj." + str(date) + ".tar.gz"
    filename_txt = str(date) + ".tar.gz"
    filename1 = "maxcpu" + str(datetime.date.today()) + ".unl"
    filename2 = "ywzb" + str(datetime.date.today()) + ".unl"
    catas_xlsx = "volte_crbt_" + str(yesterday) + ".xlsx"
    scpas_xlsx = "volte_vpmn_" + str(yesterday) + ".xlsx"
    host_xlsx = "host_pfmc_" + str(yesterday) + ".xlsx"
    quato_report = "report_maxcpu_" + str(datetime.date.today()) + ".html"

    # 邮件附件文件，判断文件是否存在
    file_temp = [filename_xlsx, filename_txt, filename1, filename2, catas_xlsx, scpas_xlsx, host_xlsx, quato_report]
    file_list = list(map(check_file, file_temp))
    for i in file_list:
        if i.is_exist:
            logging.info(" 原始文件：" + i.name + " 存在")
        else:
            logging.error("原始文件：" + i.name + " 不存在")
    # 邮件服务器配置
    server = "smtp.exmail.qq.com"
    mail_user = 'zengke@ebupt.com'
    mail_password = 'ZengKe1232798290'
    send_addr = "249626102@qq.com"
    #send_addr="zengke@ebupt.com,chenling@ebupt.com,huangzhenhai@ebupt.com,liuyan2@ebupt.com,\
    #panajie@ebupt.com,shupeng@ebupt.com,wangbin@ebupt.com,wangtao@ebupt.com,\
    #zhangjieming@ebupt.com,zhangrui@ebupt.com,zhuguang@ebupt.com,huangjiang@ebupt.com"
    Mail = MailSender(server, mail_user, mail_password)
    # 添加邮件主题和正文
    sub_title = "今日指标统计（用户数、主机性能、AS业务报表）" + str(date)
    content = ""
    if os.path.exists(quato_report):
        with open(quato_report, "r") as f:
            lines = f.readlines()
        for line in lines:
            content = content + line
    else:
        content = "<br>作业计划指标原始文件缺失</br>"

    if os.path.exists(filename_xlsx) or os.path.exists(filename_txt):
        content = content + "<br>智能网用户数及短号短信统计见附件.(tj为自动生成的excel文件，另一个为原始数据)</br>"
    else:
        content = content + "<br>今日用户数统计异常，请检查newsap1上原始数据或FTP</br>"
    Mail.add_content(sub_title, content)
    # 添加附件
    for file in file_list:
        if file.is_exist and file.name != quato_report:
            Mail.add_attachment(file.name)
            logging.info(" 添加附件：" + file.name)

    if Mail.send(send_addr):
        logging.info(" 邮件发送成功")
        for file in file_list:
            if file.is_exist:
                os.remove(file.name)
                logging.info(" 删除文件：" + file.name)
    else:
        logging.error(" 邮件发送失败,建议检查网络是否异常")
    Mail.close()
