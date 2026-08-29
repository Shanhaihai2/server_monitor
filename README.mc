# 服务器健康监控与日志告警工具

基于 Python 的服务器监控工具，定时采集系统指标、检测服务健康状态、分析日志错误关键字，异常时发送告警，并提供 Web 面板展示监控数据。

## 技术栈

- Python 3.x
- psutil（系统指标采集）
- Requests（HTTP 健康检查）
- SQLite（数据存储）
- schedule（定时任务）
- Flask（Web 面板）
- smtplib / 钉钉 Webhook（告警通知）

## 项目结构

server_monitor/
├── monitor/
│   ├── collector.py       # 系统指标采集（CPU/内存/磁盘/网络）
│   ├── checker.py         # 服务健康检查（端口/HTTP）
│   ├── database.py        # SQLite 数据存储
│   ├── log_analyzer.py    # 日志错误关键字分析
│   └── notifier.py        # 邮件/钉钉告警
├── config/
│   └── config.yaml        # 监控目标和告警配置
├── templates/
│   └── index.html         # Web 面板页面
├── main.py                # 定时监控主程序
├── web_app.py             # Web 可视化面板
├── requirements.txt
└── README.md

## 核心功能

- 定时采集 CPU、内存、磁盘、网络指标
- 端口连通性和 HTTP 服务健康检查
- 日志文件错误关键字分析
- 异常时邮件/钉钉告警通知
- SQLite 持久化存储监控数据
- Flask Web 面板可视化展示
- 配置驱动，监控目标可灵活扩展

## 快速开始

# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 修改 config/config.yaml 配置监控目标和告警方式

# 4. 启动定时监控
python main.py

# 5. 启动 Web 面板（另一个终端）
python web_app.py
# 访问 http://127.0.0.1:5000

## 配置说明

config/config.yaml 中可配置：
- monitor_targets：需要监控的端口和 HTTP 服务
- log_analysis：需要分析的日志文件路径和错误关键字
- alert：邮件和钉钉告警配置
- schedule：监控执行间隔（分钟）

## 扩展方向

- 增加更多系统指标（进程数、网络连接数等）
- 支持 Prometheus 格式指标输出
- 增加历史数据趋势图表
- 支持多服务器分布式监控
- 使用 APScheduler 替代 schedule 支持更复杂调度