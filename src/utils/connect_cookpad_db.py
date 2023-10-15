import mysql.connector
import configparser
import pandas as pd

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
    db = mysql.connector.connect(
        host="localhost",
        user=config['Database']['DB_USER'],
        password=config['Database']['DB_PASS'],
        database=config['Database']['DB_NAME'],
        port=int(config['Data']['cookpad_db_port'])
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def execute_sql2df(config, sql):
    db = mysql.connector.connect(
        host="localhost",
        user=config['Database']['DB_USER'],
        password=config['Database']['DB_PASS'],
        database=config['Database']['DB_NAME'],
        port=int(config['Data']['cookpad_db_port'])
    )
    df = pd.read_sql(sql, db)
    return df