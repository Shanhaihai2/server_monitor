import psutil
import platform
from datetime import datetime

def collect_cpu():
    #采集CPU使用率和负载
    return {
        "cpu_percent":psutil.cpu_percent(interval=1),#interval为采样间隔
        "cpu_count":psutil.cpu_count(),
        "load_avg":list(psutil.getloadavg()) if hasattr(psutil,"getloadavg") else []#平均负载
    }

def collect_memory():
    #采集内存使用情况（单位MB）
    mem=psutil.virtual_memory()
    return {
        "total_mb":round(mem.total/1024/1024,2),
        "used_mb":round(mem.used/1024/1024,2),
        "percent":mem.percent
    }

def collect_disk():
    #采集磁盘使用情况(根分区)
    disk=psutil.disk_usage("/")
    return {
        "total_gb":round(disk.total/1024/1024/1024,2),
        "used_gb":round(disk.used/1024/1024/1024,2),
        "percent":disk.percent
    }

def collect_network():
    #采集网络收发字节数（累计值）
    net=psutil.net_io_counters()
    return {
        "bytes_sent":net.bytes_sent,
        "bytes_recv":net.bytes_recv
    }

def collect_all():
    #采集全部系统指标，返回一个字典
    data={
        "timestamp":datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
        "hostname":platform.node(),
        "cpu":collect_cpu(),
        "memory":collect_memory(),
        "disk":collect_disk(),
        "network":collect_network()
    }
    return data

if __name__=="__main__":
    import json
    print(json.dumps(collect_all(), indent=2, ensure_ascii=False))