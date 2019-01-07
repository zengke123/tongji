import logging
import report_excel
import users_excel
import quato_tj
import chart_tj
from util import db


# 日志输出
def logger():
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(funcName)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename="info.log")

if __name__ == "__main__":
    # 日志记录
    logger()
    # 数据库连接
    db.create_engine('root', 'zengke', 'tongji', '127.0.0.1')
    # db.create_engine('root', '123456', 'tongji', '127.0.0.1')
    try:
        logging.info("生成AS业务报表及主机性能报表")
        report_excel.main()
    except Exception as e:
        logging.error(e)
    try:
        logging.info("生成智能网彩铃统计报表")
        users_excel.main()
    except Exception as e:
        logging.error(e)
    try:
        logging.info("生成业务指标及作业计划指标")
        quato_tj.main()
    except Exception as e:
        logging.error(e)
    try:
        logging.info("生成日报图表")
        chart_tj.main()
    except Exception as e:
        logging.error(e)





