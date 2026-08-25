from pathlib import Path
import yaml
from datetime import datetime

from monitor.collector import collect_all
from monitor.checker import check_all
from monitor.database import init_db, save_system_metrics, save_health_check, query_recent_metrics

def load_config():
    config_path=Path(__file__).resolve().parent/"config"/"config.yaml"
    with open(config_path,"r",encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_once():
    #执行一次完整的采集和检查
    print("=" * 50)
    print("开始执行监控采集")

    #初始化数据库
    init_db()

    #采集系统指标
    print("\n[1]采集系统指标")
    metrics=collect_all()
    print(f" CPU:{metrics['cpu']['cpu_percent']}%")
    print(f" 内存:{metrics['memory']['percent']}% (used:{metrics['memory']['used_mb']}MB)")
    print(f" 磁盘:{metrics['disk']['percent']}% (used:{metrics['disk']['used_gb']}GB)")
    save_system_metrics(metrics)
    print(" -> 已保存到SQLite")

    #健康检查
    print("\n[2]执行服务健康检查")
    config=load_config()
    checks=check_all(config["monitor_targets"])
    for check in checks:
        status_icon="√" if check["status"] == "UP" else "×"
        print(f" {status_icon} {check['target']} - {check['status']}")
        if "http_code" in check:
            print(f" HTTP状态码:{check['http_code']},响应时间:{check.get('response_time_ms','N/A')}ms")
        if "error" in check:
            print(f" 错误:{check['error']}")
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_health_check(checks,timestamp)
    print(" -> 已保存到SQLite")

    #查看最近记录
    print("\n [3]数据库中最近的系统指标记录")
    recent=query_recent_metrics(5)
    for row in recent:
        print(f" {row[1]} | CPU: {row[3]}% | 内存：{row[4]}% | 磁盘：{row[5]}%")

    print("\n监控采集完成！")

if __name__=="__main__":
    run_once()