import re
from pathlib import Path

def analyze_log_file(log_file:str,error_patterns:list)->list:
    #分析日志文件，返回匹配到的错误行列表
    log_path=Path(log_file)
    if not log_path.exists():
        return [{"file":log_file,"error":"日志文件不存在"}]

    matches=[]
    try:
        with open(log_path,"r",encoding="utf-8",errors="ignore") as f:
            for line_num,line in enumerate(f,1):
                for pattern in error_patterns:
                    if re.search(pattern,line,re.IGNORECASE):
                        matches.append({
                            "file":log_file,
                            "line":line_num,
                            "content":line.strip(),
                            "pattern":pattern
                        })
    except Exception as e:
        matches.append({"file":log_file,"error":str(e)})
    return matches