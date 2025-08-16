# app/alerting.py
import time
import requests
import smtplib
from email.message import EmailMessage
from config import SLACK_WEBHOOK, TEAMS_WEBHOOK, EMAIL_SMTP, ALERT_COOLDOWN_SECONDS


class Alerting:
    def __init__(self):
        self.last_alert_time = {}

    def _cooldown_ok(self, key):
        now = time.time()
        last = self.last_alert_time.get(key, 0)
        if now - last < ALERT_COOLDOWN_SECONDS:
            return False
        self.last_alert_time[key] = now
        return True


    def slack(self, text: str):
        if not SLACK_WEBHOOK:
            return
        if not self._cooldown_ok("slack"):
            return
        payload = {"text": text}
        try:
            resp = requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
            resp.raise_for_status()
        except Exception as e:
            print("Slack alert failed:", e)


    def teams(self, text: str):

        if not TEAMS_WEBHOOK:
            return
        if not self._cooldown_ok("teams"):
            return
        payload = {"text": text}
        try:
            resp = requests.post(TEAMS_WEBHOOK, json=payload, timeout=5)
            resp.raise_for_status()
        except Exception as e:
            print("Teams alert failed:", e)


    def email(self, subject: str, body: str, to: str, smtp_server: str = None, smtp_port: int = None):
        if not EMAIL_SMTP:
            return
        if not self._cooldown_ok("email"):
            return
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_SMTP
        msg["To"] = to
        msg.set_content(body)
        try:
            host = smtp_server or "localhost"
            port = smtp_port or 25
            print(f"📧 Connecting to SMTP server at {host}:{port}...")   
            # with smtplib.SMTP(host, port) as s:                         #this was for testing  
            #     s.send_message(msg)
            # print("Email sent!")
            with smtplib.SMTP("smtp.gmail.com", 587) as s:
                s.starttls()
                s.login("", "")
                s.send_message(msg)
        except Exception as e:
            print("Email failed:", e)




if __name__ == "__main__":                                              #this is for testing the file, comment this in actual pipeline implementation
    alerter = Alerting()
    
    # # Test Teams
    # alerter.teams("🚨 Test Alert from LogBERT → Teams is working!")
    
    # # Test Slack
    # alerter.slack("🚨 Test Alert from LogBERT → Slack is working!")
    alerter.email(
        subject="🚨 Test Email Alert",
        body="This is a test alert from LogBERT pipeline",
        to="akshit.agrawal999@gmail.com",
        smtp_server="localhost",
        smtp_port=1025
    )


