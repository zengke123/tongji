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
# 2018-10-10 :增加SCPAS话单流水号
# 2018-10-16 :调整业务指标
# 2018-10-23 :业务指标数据入库ywzb

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
        data = [line.strip("\n").split("|") for line in lines]
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
    max_streamnumber = ""
    max_cluster = ""
    if os.path.exists(record_file):
        record_data = get_data(record_file)
        for x in record_data:
            if re.match('scp[1-9]{3}', str(x[0])):
                max_cluster = x[0]
                max_streamnumber = x[1].strip("\n")
                break
    return max_cluster, max_streamnumber


def get_scpas_streamnumber():
    today = datetime.date.today().strftime("%Y%m%d")
    record_file = config.USERS_PATH + "scpas_stream." + str(today) + ".unl"
    max_streamnumber = ""
    max_cluster = ""
    if os.path.exists(record_file):
        record_data = get_data(record_file)
        record_data.sort(key=lambda x: int(x[1]), reverse=True)
        max_cluster = record_data[0][0]
        max_streamnumber = record_data[0][1]
    return max_cluster, max_streamnumber


# 获取智能网彩铃用户数
def get_vpmn_users():
    today = datetime.date.today().strftime("%Y%m%d")
    vpmn_file = config.USERS_PATH + "vpmnvolteuser." + str(today) + ".unl"
    hjh_file = config.USERS_PATH + "hjhvolteuser." + str(today) + ".unl"
    pyq_file = config.USERS_PATH + "pyqvolteuser." + str(today) + ".unl"
    crbt_file = config.USERS_PATH + "crbttjvolte." + str(today) + ".unl"
    vrbt_file= config.USERS_PATH + "vrbt." + str(today) + ".unl"
    ctxonly_file = config.USERS_PATH + "ctxonly" + str(today) + ".unl"
    ctxuser_file = config.USERS_PATH + "ctx_usernew" + str(today) + ".unl"
    vpmn_volte, hjh_volte, pyq_volte, crbt_volte, vrbt_users, ctx_user, ctx_group = [0] * 7
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
    if os.path.exists(ctxonly_file):
        ctx_user = float(get_data(ctxonly_file)[0][0])
        if os.path.exists(ctxuser_file):
            temps = get_data(ctxuser_file)
            ctx_all = sum([float(x[1]) for x in temps])
            ctx_group = ctx_all - ctx_user
    db.insert("users", date=today, vpmn_volte=vpmn_volte, crbt_volte=crbt_volte, hjh_volte=hjh_volte,
              pyq_volte=pyq_volte, vrbt=vrbt_users, ctx_group=ctx_group, ctx_user=ctx_user)
    return vpmn_volte, crbt_volte, vrbt_users


def get_volte_caps():
    yesterday = (datetime.date.today() - datetime.timedelta(days=1))
    file_date = yesterday.strftime("%Y-%m-%d")
    volte_caps_file = config.QUATO_PATH + "voltecaps" + str(file_date) + ".unl"
    caps_data = []
    caps_dict = {}
    if os.path.exists(volte_caps_file):
        record_data = get_data(volte_caps_file)
        for value in record_data:
            caps_name = config.caps_tilte.get(value[0])
            try:
                caps_value = float(value[1])
            except ValueError:
                # 跳过数据为空
                caps_value = ""
            caps_data.append([caps_name, caps_name.split('_')[0].upper(), caps_value])
            caps_dict[caps_name] = caps_value
        db.insert("caps", date=yesterday.strftime("%Y%m%d"), scp_caps=caps_dict.get('scp_caps',''),
                  scpas_caps=caps_dict.get('scpas_caps',''), catas_caps=caps_dict.get('catas_caps',''),
                  ctx_caps=caps_dict.get('ctx_caps',''))
    else:
        logging.error(str(volte_caps_file) + "原始文件缺失")
    return caps_data, caps_dict


def get_ywzb():
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1))
    ywzb_file = config.QUATO_PATH + "ywzb" + str(today) + ".unl"
    # list用于生成html格式
    ywzb_data = []
    # 数据入库使用，根据数据库表字段匹配ywzb_dict中的key
    # ywzb_dict从原始数据中读取的业务指标
    ywzb_dict = {}
    if os.path.exists(ywzb_file):
        for x in get_data(ywzb_file):
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
    else:
        logging.error(str(ywzb_file) + "原始文件缺失")
    # 数据入库
    try:
        # 需要入库的数据，匹配数据库表字段
        db_data = {}
        db_data['date']= yesterday.strftime("%Y%m%d")
        for k, v in ywzb_dict.items():
            # 指标名称未在config配置,即数据库中无该字段
            if k not in config.ywzb_tilte.keys():
                logging.error('业务指标 ' + k + " 未配置,需添加对应表字段")
            else:
                db_data[k] = ywzb_dict.get(k)[1]
                db_data[k+"_cluster"] = ywzb_dict.get(k)[0]
        db.insert("ywzb", **db_data)
    except Exception as e:
        logging.error("业务指标数据入库错误" + str(e))
    return ywzb_data, ywzb_dict


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
def quato_analyse():
    quato_data = [["指标项", "集群", "指标"]]
    # 汇总业务指标
    ywzb_data, ywzb_dict = get_ywzb()
    quato_data.extend(ywzb_data)
    # 汇总最大话单流水号
    max_cluster, max_streamnumber = get_streamnumber()
    quato_data.append(["SCP最大话单流水号", max_cluster, max_streamnumber])
    scpas_max_cluster, scpas_max_streamnumber = get_scpas_streamnumber()
    quato_data.append(["SCPAS最大话单流水号", scpas_max_cluster, scpas_max_streamnumber])
    # 汇总用户数统计
    vpmn, crbt, vrbt = get_vpmn_users()
    quato_data.extend([["V网Volte用户数","SCPAS", vpmn], ["音频彩铃用户数", "CATAS", crbt],
                       ["视频彩铃用户数", "CATAS", vrbt]])
    # 汇总caps统计
    caps_data, _= get_volte_caps()
    quato_data.extend(caps_data)
    # 将指标填入日报
    wb = load_workbook("templates/d_report.xlsx", data_only=True)
    ws = wb.get_sheet_by_name("用户数&关键指标")
    # 2/3G V网呼叫成功率 2gscp_minsucc
    scp_minsucc = ywzb_dict.get('2gscp_minsucc', '')
    if isinstance(scp_minsucc, list):
        ws.cell(row=40, column=2, value=scp_minsucc[1])
        ws.cell(row=40, column=3, value=scp_minsucc[0])
    # 2/3G 彩铃播放成功率 2gcl_minsucc
    cl_minsucc = ywzb_dict.get('2gcl_minsucc', '')
    if isinstance(cl_minsucc, list):
        ws.cell(row=41, column=2, value=cl_minsucc[1])
        ws.cell(row=41, column=3, value=cl_minsucc[0])
    # SCP忙时CAPS数 2gscp_maxcaps
    scp_maxcaps = ywzb_dict.get('2gscp_maxcaps', '')
    if isinstance(scp_maxcaps, list):
        ws.cell(row=44, column=2, value=scp_maxcaps[1])
        ws.cell(row=44, column=3, value=scp_maxcaps[0])
    # SCP最大话单流水号
    ws.cell(row=45, column=2, value=max_streamnumber)
    ws.cell(row=45, column=3, value=max_cluster)
    # 二卡充值成功率 UCCminsucc
    UCCminsucc = ywzb_dict.get('UCCminsucc', '')
    if isinstance(UCCminsucc, list):
        ws.cell(row=46, column=2, value=UCCminsucc[1])
        ws.cell(row=46, column=3, value=UCCminsucc[0])
    # SCPAS网络接通率 SCPAS_minnetsucc
    SCPAS_minnetsucc = ywzb_dict.get('SCPAS_minnetsucc', '')
    if isinstance(SCPAS_minnetsucc, list):
        ws.cell(row=35, column=2, value=SCPAS_minnetsucc[1])
        ws.cell(row=35, column=3, value=SCPAS_minnetsucc[0])
    # 彩铃AS网络接通率 CLAS_minnetsucc
    CLAS_minnetsucc = ywzb_dict.get('CLAS_minnetsucc', '')
    if isinstance(CLAS_minnetsucc, list):
        ws.cell(row=37, column=2, value=CLAS_minnetsucc[1])
        ws.cell(row=37, column=3, value=CLAS_minnetsucc[0])
    # 彩铃AS invite响应率 CLAS_mininvite
    CLAS_mininvite = ywzb_dict.get('CLAS_mininvite', '')
    if isinstance(CLAS_mininvite, list):
        ws.cell(row=38, column=2, value=CLAS_mininvite[1])
        ws.cell(row=38, column=3, value=CLAS_mininvite[0])
    # 彩铃AS invite响应率 CLAS_mininvite
    SCPAS_mininvite = ywzb_dict.get('SCPAS_mininvite', '')
    if isinstance(SCPAS_mininvite, list):
        ws.cell(row=36, column=2, value=SCPAS_mininvite[1])
        ws.cell(row=36, column=3, value=SCPAS_mininvite[0])
    wb.save('line.xlsx')
    quato_html = parseHtml(quato_data, title="关键业务指标", return_all=False)
    return quato_html


def main():
    today = datetime.date.today()
    cpu_file = config.QUATO_PATH + "maxcpu" + str(today) + ".unl"
    quato_report = "report_maxcpu_" + str(today) + ".html"
    if os.path.exists(quato_report):
        os.remove(quato_report)
    shutil.copy("templates/alarm.html", quato_report)
    t_start = '<table class="tableizer-table" cellspacing=0 width="60%";>\n'
    t_end = '</table>\n'
    zyjh_html, cpu_html = "", ""
    if os.path.exists(cpu_file):
        try:
            zyjh_html, cpu_html = cpu_analyse(cpu_file)
        except Exception as e:
            logging.error(e)
            logging.error("作业计划指标统计生成失败")
    else:
        logging.error(str(cpu_file) + "原始文件缺失")
    quato_html = quato_analyse()
    # 周四生成一周caps 数据
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


if __name__ == '__main__':
    main()



