import datetime
today = datetime.date.today().strftime("%Y%m%d")
today1 = datetime.date.today().strftime("%Y-%m-%d")
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
# 作业计划
# 网元与集群对应关系
cluters_dict = {
    "SCPAS": ["scpas03", "scpas04", "scpas05", "scpas06", "scpas35", "scpas38"],
    "CL": ["sccl16", "sccl17", "sccl18", "sccl19", "sccl20", "sccl21", "sccl22", "sccl23"],
    "BAK_VC": ["VC3"],
    "CLMGR": ["SCCLMGR"],
    "VC": ["VC4"],
    "SCP": ["scp17", "scp18", "scp19", "scp20", "scp21", "scp22", "scp23", "scp24", "scp25", "scp26",
            "scp27", "scp28", "scp29", "scp30", "scp31", "scp32", "scp33", "scp34", "scp36",
            "scp37", "scp39", "scp40", "scp41"],
    "CATAS": ["CLAS03", "CLAS04", "CLAS05", "CLAS06", "CLAS07"],
    "VSS": ["VSS1"],
    "SMP": ["SMP2"],
    "CENTREX": ["CTX02", "CTXAS04"],
    "SICP": ["SICP01", "SICP02", "SICP03", "SICP04"],
    "CCP": ["CCP01"],
    "OMS": ["eboms"],
    "CBAS": ["CBAS", "CDSS01"]
}

cluters_map = {
    "None": "其他",
    "CATAS": "彩铃CATAS",
    "CENTREX": "CENTREX",
    "CLMGR": "彩铃管理库CLMGR",
    "SMP": "智能网SMP",
    "BAK_VC": "智能网容灾VC",
    "VC": "智能网VC",
    "VSS": "短号短信",
    "CL": "彩铃呼叫库CL",
    "SCP": "智能网SCP",
    "SCPAS": "智能网SCPAS",
    "SICP": "智能网SICP",
    "CCP": "智能网CCP",
    "OMS": "网管OMS",
    "CBAS": "彩铃CBAS"
}


# 每日用户数、短号短信统计配置
# 原始文件绝对路径,需保留末尾的路径分隔符
# USERS_PATH = "/home/tongji/"
USERS_PATH = "/Users/EB/PycharmProjects/tongji/data/"
# 原始文件行数，用来检查数据是否缺失
# 智能网彩铃用户数原始文件行数
CRBT_VPMN_LINES = 2128
# 短号短信原始文件行数
SMS_LINES = 220

# 业务指标统计配置
# 原始文件绝对路径,需保留末尾的路径分隔符
# QUATO_PATH = "/home/tongji/tongji/data/"
QUATO_PATH = "/Users/EB/PycharmProjects/tongji/data/"
# maxcpu2018-06-07.unl
# ywzb2018-06-07.unl
# volte_crbt2018-06-06.unl
# volte_scpas2018-06-06.unl
# host2018-06-06.unl
# 指标原始文件

src_files = {
    'streamnumber': USERS_PATH + "tjnew." + str(today) + ".unl",
    'scpas_streamnumber': USERS_PATH + "scpas_stream." + str(today) + ".unl",
    'vpmn_user': USERS_PATH + "vpmnvolteuser." + str(today) + ".unl",
    'hjh_user': USERS_PATH + "hjhvolteuser." + str(today) + ".unl",
    'pyq_user': USERS_PATH + "pyqvolteuser." + str(today) + ".unl",
    'crbt_user': USERS_PATH + "crbttjvolte." + str(today) + ".unl",
    'vrbt_user': USERS_PATH + "vrbt." + str(today) + ".unl",
    'ctxonly_user': USERS_PATH + "ctxonly" + str(today) + ".unl",
    'ctxuser': USERS_PATH + "ctx_usernew" + str(today) + ".unl",
    'caps': QUATO_PATH + "voltecaps" + str(yesterday) + ".unl",
    'ywzb': QUATO_PATH + "ywzb" + str(today1) + ".unl",
    'cpu': QUATO_PATH + "maxcpu" + str(today1) + ".unl",
    'users': QUATO_PATH + "servicetj." + str(today1) + ".unl",
    'dailycaps': QUATO_PATH + "dailycaps" + str(yesterday) + ".unl"
    }
# 每日统计指标配置
# 原始数据文件ywzb.unl
# key与数据库中ywzb表字段名一致,新增指标必须配置,否则无法入库
ywzb_tilte = {
    '2gcl_minsucc': '2/3G 彩铃播放成功率',
    '2gscp_minsucc': '2/3G V网呼叫成功率',
    '2gscp_maxcaps': 'SCP忙时CAPS数',
    'UCCminsucc': '二卡充值成功率',
    'SCPAS_minnetsucc': 'SCPAS网络接通率',
    'CLAS_minnetsucc': '彩铃AS网络接通率',
    'CLAS_mininvite': '彩铃AS invite响应率',
    'SCPAS_mininvite': 'SCPAS invite响应率',
    'CLAS_minplaysucc': '彩铃AS 放音成功率'
}
# 原始数据文件voltecaps.unl
# value与数据库中caps表字段名一致
caps_tilte = {
    'CTX': 'ctx_caps',
    'SCPAS': 'scpas_caps',
    'CLAS': 'catas_caps',
    'SCP': 'scp_caps'
}
# 原始数据文件servicetj.unl
# value与数据库中users表字段名一致
users_tilte = {
    'v2g': 'vpmn_2g',
    'v4g': 'vpmn_volte',
    'h2g': 'hjh_2g',
    'h4g': 'hjh_volte',
    'p2g': 'pyq_2g',
    'p4g': 'pyq_volte',
    'vh2g': 'vh_2g',
    'vh4g': 'vh_volte',
    'vp2g': 'vp_2g',
    'vp4g': 'vp_volte',
    'hp2g': 'hp_2g',
    'hp4g': 'hp_volte',
    'vhp2g': 'vhp_2g',
    'vhp4g': 'vhp_volte'
}

# 各网元caps设计容量, keys 与 dailycaps.unl文件中的网元名保持一致
caps_capacity = {
    'CRBT-CLAS04': '',
    'CRBT-CLAS05': '',
    'CRBT-CLAS06': '',
    'CRBT-sccl20': '',
    'CRBT-sccl22': '',
    'Centrex-CTX02': '',
    'Centrex-CTXAS04': '',
    'SCP-scp17': '',
    'SCP-scp18': '',
    'SCP-scp19': '',
    'SCP-scp20': '',
    'SCP-scp21': '',
    'SCP-scp22': '',
    'SCP-scp23': '',
    'SCP-scp24': '',
    'SCP-scp25': '',
    'SCP-scp26': '',
    'SCP-scp27': '',
    'SCP-scp28': '',
    'SCP-scp29': '',
    'SCP-scp30': '',
    'SCP-scp31': '',
    'SCP-scp32': '',
    'SCP-scp33': '',
    'SCP-scp34': '',
    'SCP-scp37': '',
    'SCP-scp39': '',
    'SCP-scp40': '',
    'SCP-scp41': '',
    'SCP-scpas03': 1800,
    'SCP-scpas04': 1800,
    'SCP-scpas05': 1800,
    'SCP-scpas06': 1800,
    'SCP-scpas35': 1200,
    'SCP-scpas38': 1200
}
