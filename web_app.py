from flask import Flask,render_template
from monitor.database import query_recent_metrics
import sqlite3
from pathlib import Path

app=Flask(__name__)

DB_PATH=Path(__file__).resolve().parent / "monitor_data.db"

def query_recent_health_checks(limit:int=10):
    #查询最近的健康检查记录
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM health_checks ORDER BY id DESC LIMIT ?",(limit,))
    rows=cursor.fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    #获取最近20条系统指标
    metrics=query_recent_metrics(20)
    #反转，让时间从早到晚显示
    metrics.reverse()

    #获取最近10条健康检查
    checks=query_recent_health_checks(10)
    checks.reverse()

    return render_template("index.html",metrics=metrics,checks=checks)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)