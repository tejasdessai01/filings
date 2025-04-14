import requests
import feedparser
import time
import smtplib
from email.mime.text import MIMEText

# CONFIGURATION
EMAIL_FROM = 'tejasusd@gmail.com'
EMAIL_TO = 'tejasusd@gmail.com'
SMTP_SERVER = 'smtp.sendgrid.net'
SMTP_PORT = 587
SMTP_USERNAME = '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'  # for SendGrid
SMTP_PASSWORD = 'your_sendgrid_api_key'
CHECK_INTERVAL = 3600  # check every hour
LAST_SEEN_FILE = 'last_seen.txt'

# EDGAR RSS feed for new filings
RSS_FEED = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=N-1A&company=&dateb=&owner=include&start=0&count=100&output=atom'


def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


def load_last_seen():
    try:
        with open(LAST_SEEN_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_seen(entry_id):
    with open(LAST_SEEN_FILE, 'w') as f:
        f.write(entry_id)


def check_new_filings():
    feed = feedparser.parse(RSS_FEED)
    last_seen = load_last_seen()
    new_entries = []

    for entry in feed.entries:
        if entry.id == last_seen:
            break
        new_entries.append(entry)

    if new_entries:
        for entry in reversed(new_entries):
            summary = entry.summary.replace('\n', ' ').replace('\r', '').strip()
            body = f"New ETF Filing Detected:\n\nTitle: {entry.title}\nLink: {entry.link}\nDate: {entry.updated}\n\nSummary:\n{summary}"
            send_email(f"New ETF Filing: {entry.title}", body)
            print(f"Sent: {entry.title}")
        save_last_seen(new_entries[0].id)
    else:
        print("No new filings.")


if __name__ == '__main__':
    check_new_filings()
