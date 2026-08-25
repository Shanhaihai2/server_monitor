import socket
import requests
import logging

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger=logging.getLogger(__name__)

def check_port(host:str,port:int,timeout:int=3)->dict:
    #检查TCP端口是否连接
    result={
        "target":f"{host}:{port}",
        "type":"port",
        "status":"UP"
    }
    try:
        sock=socket.create_connection((host,port),timeout=timeout)
        sock.close()
    except Exception as e:
        result["status"]="DOWN"
        result["error"]=str(e)
        logger.warning(f"端口检查失败{host}:{port} - {e}")
    return result

def check_http(url:str,timeout:int=5)->dict:
    #检查HTTP服务器是否可访问，返回状态码和响应时间
    result={
        "target":url,
        "type":"http",
        "status":"UP"
    }
    try:
        resp=requests.get(url,timeout=timeout)
        result["http_code"]=resp.status_code
        result["response_time_ms"]=round(resp.elapsed.total_seconds() * 1000,2)
        if resp.status_code>=400:
            result["status"]="DOWN"
            logger.warning(f"HTTP检查异常{url} - 状态码{resp.status_code}")
    except Exception as e:
        result["status"]="DOWN"
        result["error"]=str(e)
        logger.warning(f"HTTP 检查失败{url} - {e}")
    return result

def check_all(targets:list)->list:
    #批量检查，targets格式：[{"type": "port", "host": "...", "port": 80}, {"type": "http", "url": "..."}]
    results=[]
    for t in targets:
        if t["type"]=="port":
            results.append(check_port(t["host"],t["port"]))
        elif t["type"]=="http":
            results.append(check_http(t["url"]))
    return results