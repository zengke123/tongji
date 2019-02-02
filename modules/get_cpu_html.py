# 生成作业计划中CPU 内存同比\环比结果
# SCPAS及彩铃AS提取最大CPU 内存 IO,并入库,提供日报中绘图的原始数据
import config, datetime
import pandas as pd
from util import db
from util.file_exists import file_exists
from util.TxtParse import TxtParse, parseHtml


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


def get_max_cpu_host(df, col):
    # 将数据按网元类型分组,按col分组,并获取最大CPU和内存占用
    # 按col进行分区，按CPU列进行排序取最大值所在行的索引值
    cpu_max_idx = df.groupby(col)["CPU"].idxmax()
    # 根据最大值索引提取指定列的数据
    cpu_max_df = df.iloc[cpu_max_idx][["网元","主机","CPU"]]
    # 调整网元列为索引
    cpu = cpu_max_df.set_index("网元")
    # 按col进行分区，按内存剩余率列进行排序取最小值所在行的索引值
    men_min_idx = df.groupby(col)["内存"].idxmin()
    # 根据索引提取指定列的数据
    men_min_df = df.iloc[men_min_idx][["网元", "主机", "内存"]]
    # 调整网元列为索引
    mem = men_min_df.set_index("网元")
    io_min_idx = df.groupby(col)["IO"].idxmin()
    io_min_df = df.iloc[io_min_idx][["网元", "主机", "IO"]]
    io = io_min_df.set_index("网元")
    # cluster_types = df[col].drop_duplicates().values
    # 用于入库的格式
    cpu_db = [[col, "最大值项:CPU(%)", "最大值项:MEM(%)","最大值项：IO(%)"]]
    # 显示在邮件正文中的格式
    cpu_data = [[col, "最大值项:CPU(%)","CPU最大值:主机", "最大值项:MEM(%)","内存最大值:主机",
                "最大值项：IO(%)","IO最大值:主机"]]
    cluster_types = []
    cluster_types.extend(config.cluters_dict.get("SCPAS"))
    cluster_types.extend(config.cluters_dict.get("CATAS"))
    cluster_types.extend(config.cluters_dict.get("SICP"))
    cluster_types.extend(["VC3", "VC4", "SMP2"])
    for cluster_type in cluster_types:
        cpu_data.append([cluster_type, cpu.loc[cluster_type]["CPU"], cpu.loc[cluster_type]["主机"],
                         round(100-mem.loc[cluster_type]["内存"],2), mem.loc[cluster_type]["主机"],
                         round(100-io.loc[cluster_type]["IO"],2), io.loc[cluster_type]["主机"]])
        cpu_db.append([cluster_type, cpu.loc[cluster_type]["CPU"], round(100-mem.loc[cluster_type]["内存"],2),
                       round(100-io.loc[cluster_type]["IO"],2)])
    return cpu_db, cpu_data


# CPU&内存分析
@file_exists(config.src_files.get('cpu'))
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
    list_td_grp, list_td_grp_html = get_max_cpu_host(df_td, col="网元")

    # 数据入库
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime("%Y%m%d")
    for values in list_td_grp[1:]:
        # 数值使用float转换，否则插入数据库Mysql会报错
        db.insert("as_pfmc", date=yesterday, cluste=values[0], max_cpu=float(values[1]),max_mem=float(values[2]), max_io=float(values[3]))
    list_ytd_grp= get_max_cpu(df_ytd, col="网元类型")
    list_b4ytd_grp= get_max_cpu(df_b4ytd, col="网元类型")
    list_wk_grp= get_max_cpu(df_wk, col="网元类型")
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
    t_start = '<table class="tableizer-table" cellspacing=0 width="60%";>\n'
    t_end = '</table>\n'
    zyjh_html = parseHtml(output_data, "作业计划指标")
    cpu_today_html = parseHtml(list_td_grp_html, "AS主机昨日性能指标")
    cpu_yes_html = parseHtml(list_ytd_grp, "全网主机昨日性能指标", return_all=True)
    cpu_html = cpu_today_html + t_end + "<br></br>" + t_start + cpu_yes_html
    return zyjh_html, cpu_html