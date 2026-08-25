import sqlite3
import json
from pathlib import Path

DB_PATH=Path(__file__).resolve().parent.parent/"monitor_data.db"

def init_db():
    #初始化数据库，创建监控指标表和健康检查表
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()

    #系统指标表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            hostname TEXT NOT NULL,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL,
            bytes_sent INTEGER,
            bytes_recv INTEGER
        )
    """)

    #健康检查表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            target TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            detail TEXT
        )
    """)

def save_system_metrics(data:dict):
    #保存系统指标到数据库
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    cursor.execute("""
        INSERT INTO system_metrics 
        (timestamp, hostname, cpu_percent, memory_percent, disk_percent, bytes_sent, bytes_recv)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,(
        data["timestamp"],
        data["hostname"],
        data["cpu"]["cpu_percent"],
        data["memory"]["percent"],
        data["disk"]["percent"],
        data["network"]["bytes_sent"],
        data["network"]["bytes_recv"]
    )) 
    conn.commit()
    conn.close()

def save_health_check(checks:list,timestamp:str):
    #保存健康检查结果到数据库
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    for check in checks:
        detail=json.dumps(check,ensure_ascii=False)
        cursor.execute("""
            INSERT INTO health_checks (timestamp, target, type, status, detail)
            VALUES (?, ?, ?, ?, ?)
        """,(
            timestamp,
            check.get("target",""),
            check.get("type",""),
            check.get("status","UNKNOWN"),
            detail
        ))
    conn.commit()
    conn.close()

def query_recent_metrics(limit:int = 10):
    #查询最近的系统指标记录
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM system_metrics ORDER BY id DESC LIMIT ?",(limit,))
    rows=cursor.fetchall()
    conn.close()
    return rows

if __name__=="__main__":
    init_db()
    print("数据库初始化完成：",DB_PATH)