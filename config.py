
# 网元与集群对应关系
cluters_dict ={
    "SCPAS":["scpas03","scpas04","scpas05","scpas06","scpas35","scpas38"],
    "CL":["sccl16","sccl17","sccl18","sccl19","sccl20","sccl21","sccl22","sccl23"],
    "BAK_VC":["VC3"],
    "CLMGR":["SCCLMGR"],
    "VC" :["VC4"],
    "SCP" :["scp17", "scp18", "scp19", "scp20", "scp21", "scp22", "scp23", "scp24", "scp25", "scp26",
            "scp27", "scp28", "scp29", "scp30", "scp31", "scp32", "scp33", "scp34", "scp36",
            "scp37", "scp39", "scp40", "scp41"],
    "CATAS" :["CLAS03","CLAS04","CLAS05","CLAS06","CLAS07"],
    "VSS" : ["VSS1"],
    "SMP":["SMP2"],
    "CENTREX":["CTX02","CTXAS04"],
    "SICP":["SICP01","SICP02","SICP03","SICP04"],
    "CCP":["CCP01"],
    "OMS":["eboms"],
    "CBAS":["CBAS","CDSS01"]
}

cluters_map = {
    "None":"其他",
    "CATAS":"彩铃CATAS",
    "CENTREX":"CENTREX",
    "CLMGR":"彩铃管理库CLMGR",
    "SMP":"智能网SMP",
    "BAK_VC":"智能网容灾VC",
    "VC":"智能网VC",
    "VSS":"短号短信",
    "CL":"彩铃呼叫库CL",
    "SCP":"智能网SCP",
    "SCPAS":"智能网SCPAS",
    "SICP":"智能网SICP",
    "CCP":"智能网CCP",
    "OMS":"网管OMS",
    "CBAS":"彩铃CBAS"
}


# 每日用户数、短号短信统计配置
# 原始文件路径,需保留末尾的路径分隔符
USERS_PATH = "data/"
# 原始文件行数，用来检查数据是否缺失
# 智能网彩铃用户数原始文件行数
CRBT_VPMN_LINES = 2131
# 短号短信原始文件行数
SMS_LINES = 220

# 业务指标统计配置
# 原始文件路径,需保留末尾的路径分隔符
QUATO_PATH = "data/"
# maxcpu2018-06-07.unl
# ywzb2018-06-07.unl
# volte_crbt2018-06-06.unl
# volte_scpas2018-06-06.unl
# host2018-06-06.unl
