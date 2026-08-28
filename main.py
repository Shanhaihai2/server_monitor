import time
import schedule
import logging
from pathlib import Path
import yaml
from datetime import datetime

from monitor.collector import collect_all
from monitor.checker import check_all
from monitor.database import init_db, save_system_metrics, save_health_check, query_recent_metrics
from monitor.log_analyzer import analyze_log_file
from monitor.notifier import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger=logging.getLogger(__name__)

def load_config():
    config_path=Path(__file__).resolve().parent/"config"/"config.yaml"
    with open(config_path,"r",encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_monitor_once():
    #执行一次完整的采集和检查
    logger.info("=" *50)
    logger.info("开始执行监控任务......")

    config=load_config()

    #初始化数据库
    init_db()

    #采集系统指标
    logger.info("[1]采集系统指标")
    metrics=collect_all()
    save_system_metrics(metrics)
    logger.info(f" CPU:{metrics['cpu']['cpu_percent']}%,内存:{metrics['memory']['percent']}% (used:{metrics['memory']['used_mb']}MB),磁盘:{metrics['disk']['percent']}% (used:{metrics['disk']['used_gb']}GB)")

    #健康检查
    logger.info("[2]执行服务健康检查")
    checks=check_all(config["monitor_targets"])
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_health_check(checks,timestamp)

    alert_messages=[]#收集所有异常信息用于告警

    for check in checks:
        if check["status"] != "UP":
            msg=f"服务异常:{check['target']} - {check['status']}"
            if "error" in check:
                msg+=f" 错误:{check['error']}"
            elif "http_code" in check:
                msg+=f" HTTP状态码:{check['http_code']},响应时间:{check.get('response_time_ms','N/A')}ms"
            alert_messages.append(msg)
            logger.warning(msg)
        else:
            logger.info(f" √{check['target']} - UP")

    #日志分析
    if config.get("log_analysis",{}).get("enabled"):
        logger.info("[3]分析日志文件")
        for log_file in config["log_analysis"]["log_files"]:
            matches=analyze_log_file(log_file,config["log_analysis"]["error_patterns"])
            if matches:
                for m in matches[:5]: #只取前5条避免告警内容过长
                    if "error" in m:
                        logger.warning(f" 日志文件{m['file']} 分析异常：{m['error']}")
                    else:
                        line_info=f" 日志文件{m['file']} 第{m['line']}行匹配模式 '{m['pattern']}':{m['content']}"
                        logger.warning(line_info)
                        alert_messages.append(line_info)

    #发送告警
    if alert_messages:
        alert_subject=f" [服务器监控告警] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        alert_content="\n".join(alert_messages)
        logger.info("[4]发送告警通知")
        send_alert(alert_subject,alert_content,config.get("alert",{}))
    else:
        logger.info("[4]无异常，不发送告警")

    #查看最近记录
    logger.info("[5]数据库中最近的系统指标记录")
    recent=query_recent_metrics(3)
    for row in recent:
        logger.info(f" {row[1]} | CPU: {row[3]}% | 内存：{row[4]}% | 磁盘：{row[5]}%")

    logger.info("监控任务执行完成")

def run_scheduler():
    #启动定时调度器
    config=load_config()
    interval=config.get("schedule",{}).get("interval_minutes",5)

    logger.info(f"启动定时监控，每{interval}分钟执行一次")

    #启动后立即执行一次
    run_monitor_once()

    #设置定时任务
    schedule.every(interval).minutes.do(run_monitor_once)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__=="__main__":
    run_scheduler()