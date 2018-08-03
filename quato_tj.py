#!/usr/bin/env python
import re
import os
import shutil
import datetime
import logging
import config
import pandas as pd
from util import db
from openpyxl import load_workbook
from util.TxtParse import TxtParse, parseHtml
from chart_tj import get_date_range

# 2018-07-26 :增加ctx_caps指标
# 2018-08-03 :增加视频彩铃指标

# 判断网元类型
def get_cluster_type(cluster):
    _type = "None"
    for cluster_type, clusters in config.cluters_dict.items():
        if cluster in clusters:
            _type = cluster_type
    return _type


# 判断性能指标增长或下降
def check(x):
    if str(x).startswith("-"):
        _flag = "下降"
    else:
        _flag = "增长"
    return _flag + str(x)


def get_max_cpu(df, col):
    # 将数据按网元类型分组,按col分组,并获取最大CPU和内存占用
    grouped = df.groupby(col)
    # 获取最大CPU占用和最小内存剩余
    cpu = grouped.agg("max")["CPU"]
    mem = grouped.agg("min")["内存"]
    io = grouped.agg("min")["IO"]
    cluster_types = df[col].drop_duplicates().values
    cpu_data = [[col, "最大值项:CPU(%)", "最大值项:MEM(%)", "最大值项：IO(%)"]]
    for cluster_type in cluster_types:
        cpu_data.append([cluster_type, cpu[cluster_type],round(100-mem[cluster_type],2),round(100-io[cluster_type],2)])
    return cpu_data


# CPU&内存分析
def cpu_analyse(cpu_file):
    title = ['网元', '主机', 'CPU', '内存', 'IO']
    data = TxtParse(cpu_file, sep='|', titles=title)
    df = data.get_df()
    # 增加对应的网元类型
    df["网元类型"] = list(map(lambda x: get_cluster_type(x), df["网元"]))
    # 数据分割，当天，前一天，前一周
    num = df.index[df['网元'].isin(["全网昨天CPU&内存数据获取"]) == True].tolist()[0]
    num1 = df.index[df['网元'].isin(["全网前天CPU&内存数据"]) == True].tolist()[0]
    num2 = df.index[df['网元'].isin(["全网前一周CPU&内存数据"]) == True].tolist()[0]
    # 昨天AS主机性能数据
    df_td = df.loc[:num - 1]
    # 全网昨天性能数据
    df_ytd = df.loc[num + 1:num1 - 1]
    # 全网前天性能数据
    df_b4ytd = df.loc[num1 + 1:num2 - 1]
    # 全网前一周性能数据
    df_wk = df.loc[num2 + 1:]
    # 将数据进行分组处理,并转成list,方便生成HTML
    list_td_grp = get_max_cpu(df_td, col="网元")

    # 数据入库
    # db.create_engine('root', 'zengke', 'tongji', '127.0.0.1')
    today = datetime.date.today().strftime("%Y%m%d")
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime("%Y%m%d")
    for values in list_td_grp[1:]:
        # 数值使用float转换，否则插入数据库Mysql会报错
        db.insert("as_pfmc", date=yesterday, cluste=values[0], max_cpu=float(values[1]),max_mem=float(values[2]), max_io=float(values[3]))

    list_ytd_grp = get_max_cpu(df_ytd, col="网元类型")
    list_b4ytd_grp = get_max_cpu(df_b4ytd, col="网元类型")
    list_wk_grp = get_max_cpu(df_wk, col="网元类型")
    # 转为DataFrame
    df_ytd_grp = pd.DataFrame(list_ytd_grp[1:], columns=["网元类型", "CPU", "MEM", "IO"])
    df_b4ytd_grp = pd.DataFrame(list_b4ytd_grp[1:], columns=["网元类型", "CPU", "MEM", "IO"])
    df_wk_grp = pd.DataFrame(list_wk_grp[1:], columns=["网元类型", "CPU", "MEM", "IO"])
    # 昨天、前天、上周数据合并为一张表
    df_temp = pd.merge(df_b4ytd_grp, df_wk_grp, how="left", on="网元类型")
    df_merge = pd.merge(df_ytd_grp, df_temp, how="left", on="网元类型")
    # 计算同比增长（前一周比较）
    df_merge["t_cpu_growth"] = (df_merge["CPU"] - df_merge["CPU_y"]) / df_merge["CPU_y"]
    df_merge["t_mem_growth"] = (df_merge["MEM"] - df_merge["MEM_y"]) / df_merge["MEM_y"]
    # 计算环比增长（前一天比较）
    df_merge["h_cpu_growth"] = (df_merge["CPU"] - df_merge["CPU_x"]) / df_merge["CPU_x"]
    df_merge["h_mem_growth"] = (df_merge["MEM"] - df_merge["MEM_x"]) / df_merge["MEM_x"]
    # 将小数转换成百分数
    for col in ["t_cpu_growth", "t_mem_growth", "h_cpu_growth", "h_mem_growth"]:
        df_merge[col] = df_merge[col].apply(lambda x: format(x, ".2%"))
    # 将CPU MEM统一保留2位小数
    for col in ["CPU", "MEM"]:
        df_merge[col] = df_merge[col].apply(lambda x: format(x, ".2f"))
    # 输出表格
    output_data = [["网元类型", "性能指标分析"]]
    for i in range(len(df_merge.index)):
        str = "CPU占用: 最高	{}%	,同比(前一周同一天的数据对比){}	,环比(前一天数据对比){}, 内存占用: 最高	{}%	,同比{}	,环比\
        	{}".format(df_merge.ix[i]["CPU"],check(df_merge.ix[i]["t_cpu_growth"]),check(df_merge.ix[i]["h_cpu_growth"]),df_merge.ix[i]["MEM"],check(df_merge.ix[i]["t_mem_growth"]),check(df_merge.ix[i]["h_mem_growth"]))
        output_data.append([config.cluters_map.get(df_merge.ix[i]["网元类型"]), str])

    zyjh_html = parseHtml(output_data, "作业计划指标")
    cpu_today_html = parseHtml(list_td_grp, "AS主机昨日性能指标")
    cpu_yes_html = parseHtml(list_ytd_grp, "全网主机昨日性能指标")
    # cpu_week_html = parseHtml(list_wk_grp, "全网主机上周性能指标")
    cpu_html = cpu_today_html + cpu_yes_html
    return zyjh_html, cpu_html


# 从unl文件中提取数据
def get_data(unl):
    with open(unl, "r") as f:
        lines = f.readlines()
        data = [line.split("|") for line in lines]
    for x in data:
        try:
            x.remove("\n")
        except ValueError:
            pass
    return data


# 获取话单最大流水号
def get_streamnumber():
    today = datetime.date.today().strftime("%Y%m%d")
    record_file = config.USERS_PATH + "tjnew." + str(today) + ".unl"
    max_streamnumber = None
    max_cluster = None
    if os.path.exists(record_file):
        record_data = get_data(record_file)
        for x in record_data:
            if re.match('scp[1-9]{3}', str(x[0])):
                max_cluster = x[0]
                max_streamnumber = x[1].strip("\n")
                break
    return max_cluster, max_streamnumber


# 获取智能网彩铃用户数
def get_vpmn_users():
    today = datetime.date.today().strftime("%Y%m%d")
    vpmn_file = config.USERS_PATH + "vpmnvolteuser." + str(today) + ".unl"
    hjh_file = config.USERS_PATH + "hjhvolteuser." + str(today) + ".unl"
    pyq_file = config.USERS_PATH + "pyqvolteuser." + str(today) + ".unl"
    crbt_file = config.USERS_PATH + "crbttjvolte." + str(today) + ".unl"
    vrbt_file= config.USERS_PATH + "vrbt." + str(today) + ".unl"
    vpmn_volte = None
    hjh_volte = None
    pyq_volte = None
    crbt_volte = None
    vrbt_users = None
    if os.path.exists(vpmn_file):
        vpmn_volte = float(get_data(vpmn_file)[0][0])
    if os.path.exists(hjh_file):
        hjh_volte = float(get_data(hjh_file)[0][0])
    if os.path.exists(pyq_file):
        pyq_volte = float(get_data(pyq_file)[0][0])
    if os.path.exists(crbt_file):
        crbt_volte = sum([float(x[1]) for x in get_data(crbt_file)])
    if os.path.exists(pyq_file):
        vrbt_users = float(get_data(vrbt_file)[0][0])
    db.insert("users", date=today, vpmn_volte=vpmn_volte, crbt_volte=crbt_volte, hjh_volte=hjh_volte,
              pyq_volte=pyq_volte, vrbt=vrbt_users)
    return vpmn_volte, crbt_volte, vrbt_users


def get_volte_caps():
    yesterday = (datetime.date.today() - datetime.timedelta(days=1))
    file_date = yesterday.strftime("%Y-%m-%d")
    volte_caps_file = config.QUATO_PATH + "voltecaps" + str(file_date) + ".unl"
    scpas_caps = None
    catas_caps = None
    scp_caps = None
    ctx_caps = None
    if os.path.exists(volte_caps_file):
        record_data = get_data(volte_caps_file)
        ctx_caps = float(record_data[0][1])
        scpas_caps = float(record_data[1][1])
        catas_caps = float(record_data[2][1])
        scp_caps = float(record_data[3][1])
        db.insert("caps", date=yesterday.strftime("%Y%m%d"), scp_caps=scp_caps, scpas_caps=scpas_caps,
                  catas_caps=catas_caps, ctx_caps=ctx_caps)
    return scp_caps, scpas_caps, catas_caps, ctx_caps

def get_week_caps():
    today = datetime.datetime.now().strftime("%Y%m%d")
    date_range = get_date_range(today, delta_day=7)
    rows = []
    row_title = ["日期","SCP","SCPAS","CATAS"]
    rows.append(row_title)
    for date in date_range:
        sql = "select * from caps where date = {}".format(date)
        result = db.select(sql)
        try:
            row = list(result[0])
        except IndexError:
            row = ["","","",""]
        rows.append(row)
    caps_html = parseHtml(rows, title="CAPS统计", return_all=False)
    return caps_html

# 业务指标分析
def quato_analyse(quato_file):
    clusters = []
    values = []
    with open(quato_file, "r") as f:
        for line in f.readlines():
            line = line.split("|")
            clusters.append(line[0])
            values.append(line[1])
    max_cluster, max_streamnumber = get_streamnumber()
    vpmn, crbt, vrbt = get_vpmn_users()
    scp_caps, scpas_caps, catas_caps, ctx_caps= get_volte_caps()
    clusters.extend([max_cluster, "SCPAS", "CATAS", "CAVTAS", "SCP", "SCPAS", "CATAS","CTX"])
    values.extend([max_streamnumber, vpmn, crbt, vrbt, scp_caps, scpas_caps, catas_caps, ctx_caps])
    quato_name = ["2/3G 彩铃播放成功率", "2/3G V网呼叫成功率", "SCP忙时CAPS数", "二卡充值成功率","SCPAS网络接通率",
                  "彩铃AS网络接通率","彩铃AS invite响应率",
                  "SCP最大话单流水号", "VPMN用户数", "音频彩铃用户数","视频彩铃用户数",
                  "SCP CAPS", "SCPAS CAPS", "CATAS CAPS", "CTX CAPS"]
    quato_data = list(zip(quato_name, clusters, values))
    # [('2/3G 彩铃播放成功率', 'CRBT-sccl16', '99.78'),
    #  ('2/3G V网呼叫成功率', 'SCP-scp39', '98.8494'),
    # ('SCP忙时CAPS数', 'SCP-scp41', '153.82'),
    # ('二卡充值成功率', 'UCC', '97.58'),
    # ('SCPAS网络接通率', 'SCP-scpas38', '97.58'),
    # ('彩铃AS网络接通率', 'SCP-scpas38', '97.58'),
    # ('彩铃AS invite响应率', 'SCP-scpas38', '97.58'),
    # ('SCP最大话单流水号', 'scp292', '947889930'),
    #  ('VPMN用户数', 'SCPAS', 10838581.0),
    # ('彩铃用户数', 'CATAS', 5310746.0)]
    wb = load_workbook("templates/d_report.xlsx", data_only=True)
    ws = wb.get_sheet_by_name("用户数&关键指标")
    # 2/3G V网呼叫成功率
    ws.cell(row=40,column=2,value=quato_data[1][2])
    ws.cell(row=40, column=3, value=quato_data[1][1])
    # 2/3G 彩铃播放成功率
    ws.cell(row=41, column=2, value=quato_data[0][2])
    ws.cell(row=41, column=3, value=quato_data[0][1])
    # SCP忙时CAPS数
    ws.cell(row=44, column=2, value=quato_data[2][2])
    ws.cell(row=44, column=3, value=quato_data[2][1])
    # SCP最大话单流水号
    ws.cell(row=45, column=2, value=quato_data[7][2])
    ws.cell(row=45, column=3, value=quato_data[7][1])
    # 二卡充值成功率
    ws.cell(row=46, column=2, value=quato_data[3][2])
    ws.cell(row=46, column=3, value=quato_data[3][1])
    # SCPAS网络接通率
    ws.cell(row=35, column=2, value=quato_data[4][2])
    ws.cell(row=35, column=3, value=quato_data[4][1])
    # 彩铃AS网络接通率
    ws.cell(row=37, column=2, value=quato_data[5][2])
    ws.cell(row=37, column=3, value=quato_data[5][1])
    # 彩铃AS invite响应率
    ws.cell(row=38, column=2, value=quato_data[6][2])
    ws.cell(row=38, column=3, value=quato_data[6][1])
    wb.save('line.xlsx')
    quato_data.insert(0, ["指标项", "集群", "指标"])
    quato_html = parseHtml(quato_data, title="关键业务指标", return_all=False)
    return quato_html


def main():
    today = datetime.date.today()
    cpu_file = config.QUATO_PATH + "maxcpu" + str(today) + ".unl"
    quato_file = config.QUATO_PATH + "ywzb" + str(today) + ".unl"
    quato_report = "report_maxcpu_" + str(today) + ".html"
    if os.path.exists(quato_report):
        os.remove(quato_report)
    shutil.copy("templates/alarm.html", quato_report)
    if os.path.exists(cpu_file) and os.path.exists(quato_file):
        try:
            t_start = '<table class="tableizer-table" cellspacing=0 width="60%";>\n'
            t_end = '</table>\n'
            zyjh_html, cpu_html = cpu_analyse(cpu_file)
            quato_html = quato_analyse(quato_file)
            if today.weekday() == 3:
                caps = get_week_caps()
                caps_html = t_start + caps + t_end
            else:
                caps_html = ""
            html = t_start + quato_html + t_end + "<br></br>" + caps_html + "<br></br>" +\
                   t_start + cpu_html + t_end + "<br></br>" + t_start + zyjh_html + t_end
            with open(quato_report, "a") as f:
                f.write(html)
            logging.info("业务指标统计生成成功")
        except Exception as e:
            logging.error(e)
            logging.error("业务指标统计生成失败")
    else:
        logging.error("业务指标原始文件缺失")


if __name__ == '__main__':
    main()



