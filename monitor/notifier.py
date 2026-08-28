import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.header import Header

logger=logging.getLogger(__name__)

def send_email_alert(subject:str,content:str,config:dict):
    #发送邮件警告，config需要包含smtp配置
    try:
        msg=MIMEText(content,"plain","utf-8")
        msg["Subject"]=Header(subject,"utf-8")
        msg["From"]=config["smtp"]["sender"]
        msg["To"]=config["smtp"]["receivers"]

        server=smtplib.SMTP_SSL(config["smtp"]["host"],config["smtp"]["port"])
        server.login(config["smtp"]["sender"],config["smtp"]["password"])
        server.sendmail(config["smtp"]["sender"],config["smtp"]["receivers"].split(","),msg.as_string())
        server.quit()
        logger.info("邮件告警发送成功")
        return True
    except Exception as e:
        logger.error(f"邮件告警发送失败：{e}")
        return False

def send_dingtalk_alert(webhook_url:str,content:str):
    #发送钉钉机器人告警
    try:
        data={
            "msgtype":"text",
            "text":{
                "content":content
            }
        }
        resp=requests.post(webhook_url,json=data,timeout=5)
        if resp.status_code==200 and resp.json().get("errcode")==0:
            logger.info("钉钉告警发送成功")
            return True
        else:
            logger.error(f"钉钉告警发送失败：{resp.text}")
            return False
    except Exception as e:
        logger.error(f"钉钉告警发送异常：{e}")
        return False

def send_alert(subject:str,content:str,alert_config:dict):
    #根据配置发送告警
    if alert_config.get("email",{}).get("enabled"):
        send_email_alert(subject,content,alert_config["email"])
    if alert_config.get("dingtalk",{}).get("enabled"):
        send_dingtalk_alert(alert_config["dingtalk"]["webhook_url"],content)