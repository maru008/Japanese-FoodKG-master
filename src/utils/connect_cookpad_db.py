import mysql.connector
import configparser

def get_config(filename):
    """
    与えられた設定ファイル名から、データベース接続に必要な設定を読み取ります。

    Parameters:
    filename (str): 設定ファイル名

    Returns:
    configparser.ConfigParser: データベース接続設定を含むconfigparser.ConfigParserオブジェクト
    """
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def execute_sql(config, sql):
    """
    与えられた設定とSQL文を用いて、データベースに接続し、SQL文を実行します。
    結果をフェッチし、全ての行を返します。

    Parameters:
    config (configparser.ConfigParser): データベース接続設定を含むconfigparser.ConfigParserオブジェクト
    sql (str): 実行するSQL文

    Returns:
    list: SQL文の実行結果を含むリスト
    """
    db = mysql.connector.connect(
        host="localhost",
        user=config['DataBase']['DB_USER'],
        password=config['DataBase']['DB_PASS'],
        database=config['DataBase']['DB_NAME'],
        port=int(config['Data']['cookpad_db_port'])
    )

    cursor = db.cursor()
    cursor.execute(sql)

    result = cursor.fetchall()

    return result
