import config
import datetime
import logging
from util import db
from util.file_exists import file_exists, get_data


@file_exists(config.src_files.get('vpmn_user'))
def get_vpmn_user(filename):
    vpmn_volte = float(get_data(filename)[0][0])
    return vpmn_volte


@file_exists(config.src_files.get('hjh_user'))
def get_hjh_user(filename):
    hjh_volte = float(get_data(filename)[0][0])
    return hjh_volte


@file_exists(config.src_files.get('pyq_user'))
def get_pyq_user(filename):
    pyq_volte = float(get_data(filename)[0][0])
    return pyq_volte


@file_exists(config.src_files.get('crbt_user'))
def get_crbt_user(filename):
    crbt_volte = sum([float(x[1]) for x in get_data(filename)])
    return crbt_volte


@file_exists(config.src_files.get('vrbt_user'))
def get_vrbt_user(filename):
    vrbt_users = float(get_data(filename)[0][0])
    return vrbt_users


@file_exists(config.src_files.get('ctxonly_user'))
def get_ctxonly_user(filename):
    ctx_user = float(get_data(filename)[0][0])
    return ctx_user


@file_exists(config.src_files.get('ctxuser'))
def get_all_ctxuser(filename):
    temps = get_data(filename)
    ctx_all = sum([float(x[1]) for x in temps])
    return ctx_all


def get_ctx_group():
    ctx_user = get_ctxonly_user()
    ctx_all = get_all_ctxuser()
    if ctx_user and ctx_all:
        ctx_group = ctx_all - ctx_user
        return ctx_group


# 汇总
def get_all_users():
    today = datetime.date.today().strftime("%Y%m%d")
    vpmn = get_vpmn_user() if get_vpmn_user() else 0
    pyq = get_pyq_user() if get_pyq_user() else 0
    hjh = get_hjh_user() if get_hjh_user() else 0
    crbt = get_crbt_user() if get_crbt_user() else 0
    vrbt = get_vrbt_user() if get_vrbt_user() else 0
    ctx_only = get_ctxonly_user() if get_ctxonly_user() else 0
    ctx_group = get_ctx_group() if get_ctxonly_user() else 0
    # 转换格式，方便直接入库，key与数据库中表字段一致
    users_db = {
        'date': today,
        'vpmn_volte': vpmn,
        'crbt_volte': crbt,
        'hjh_volte': hjh,
        'pyq_volte': pyq,
        'ctx_group': ctx_group,
        'ctx_user': ctx_only,
        'vrbt': vrbt
    }
    try:
        db.insert('users',**users_db)
    except Exception as e:
        logging.error("用户数入库错误" + str(e))
    return users_db
