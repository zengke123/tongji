import functools
import logging
import time
import threading
import mysql.connector

#计算函数运行时间
def timelog(func):
    @functools.wraps(func)
    def wrapper(*args,**kw):
        begin = time.time()
        result = func(*args,**kw)
        runtime = time.time() - begin
        logging.info('%s executed in %s ms' % (func.__name__, runtime))
        return result
    return wrapper

engine = None


def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    global engine
    params = dict(user=user, password=password, database=database, host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
    for k,v in defaults.items():
        params[k] = kw.pop(k,v)
    params.update(kw)
    params['buffered'] = True
    engine = Engine(**params)
    logging.info('Mysql Engine Init')


    #engine.connect()  创建数据库连接


class Engine():
    def __init__(self,**kw):
        self._params = kw

    def connect(self):
        return mysql.connector.connect(**self._params)


def with_connection(func):
    # 自动获取连接，获取游标cursor,结束自动断开 通过ConnectionCtx类实现
    @functools.wraps(func)
    def wrapper(*args, **kw):
        with ConnectionCtx():
            return func(*args, **kw)
    return wrapper


# 数据库惰性连接
class DB_CTX(threading.local):
    def __init__(self):
        self.connection = None

    def is_init(self):
        return self.connection is not None

    def init(self):
        self.connection = engine.connect()
        logging.info('[CONNECTION] [OPEN] connection <%s> ' % hex(id(self.connection)))

    def cursor(self):
        return self.connection.cursor()

    def cleanup(self):
        if self.connection:
            _connection = self.connection
            self.connection.close()
            self.connection = None
            logging.info('[CONNECTION] [CLOSE] connection <%s> ' % hex(id(_connection)))

    def commit(self):
        return self.connection.commit()

    def rollback(self):
        return self.connection.rollback()

db_ctx = DB_CTX()

#实现with方法，调用方便，自动连接和释放
class ConnectionCtx():
    def __enter__(self):
        global db_ctx
        self.should_cleanup = False
        if not db_ctx.is_init():
            logging.info('[CONNECTION] [INIT]')
            db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global db_ctx
        if self.should_cleanup:
            db_ctx.cleanup()


@timelog
@with_connection
def insert(table, **kw):
    cols = kw.keys()
    args = kw.values()
    #print(cols,args)
    sql = 'insert into %s(%s) values (%s)' % (table, ','.join(['%s' % col for col in cols]),','.join('%s' for i in range(len(args))))
    return update(sql, *args)

@timelog
@with_connection
def update(sql,*args):
    global db_ctx
    cursor = None
    try:
        cursor = db_ctx.cursor()
        cursor.execute(sql,args)
        #logging.info('[SUCCESS] SQL: %s ,ARGS: %s' % (sql, args))
        r = cursor.rowcount
        logging.info('[Query OK] %s rows affected: %s ,ARGS: %s' % (r,sql, args))
        db_ctx.commit()
    except Exception as e:
        logging.warning('[ERROR] %s: %s ,ARGS: %s' % (str(e),sql, args))


    finally:
        if cursor:
            cursor.close()


@timelog
@with_connection
def select(sql, *args):
    global db_ctx
    cursor = None
    try:
        cursor = db_ctx.cursor()
        logging.info('[Query OK] SQL: %s ,ARGS: %s' % (sql, args))
        cursor.execute(sql, args)
        result = cursor.fetchall()
        return result
    finally:
        if cursor:
            cursor.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    create_engine('root', 'zengke', 'tongji', '127.0.0.1')
    # select("select code from stock where macd_flag='1'")
    # sql = 'update user set password = %s where name = %s'
    # sql = 'insert into user(id,name,password) values(%s,%s,%s)'
    # sql = 'delete from user where name=%s'
    # update(sql,'guest123456','guest')
    # insert('users',date="20180529",crbt_volte='456')
    # vpmn_users = select('select vpmn_volte from users where date="20180530"')[0][0]
    # print(vpmn_users)