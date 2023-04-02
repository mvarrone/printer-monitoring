import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_devices() -> list:
    with open('devices.json', 'r') as file:
        devices = json.load(file)

    return devices


def get_configurations() -> dict:
    with open('config.json', 'r') as file:
        configs = json.load(file)

    return configs


def send_email(sender_email, receiver_email, subject, body, data, reason) -> None:
    configurations = get_configurations()

    smtp_host = configurations.get("smtp").get("host")
    smtp_port = configurations.get("smtp").get("port")
    app_password = configurations.get("app_password")

    with open('html/template.html', 'r') as file:
        html = file.read()

    # Convert data to HTML table rows
    rows = ''
    for key, value in data.items():
        rows += f"<tr><td>{key}</td><td>{value}</td></tr>"

    # Replace the {rows} placeholder in the HTML template with the actual rows
    html = html.replace('{rows}', rows)

    # Create a multipart message and set the headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # message.attach(MIMEText(body, "plain"))
    message.attach(
        MIMEText(f"<html><body><h3>{body}</h3></body></html>", "html"))
    message.attach(MIMEText(html, "html"))

    # Send the email using a context manager
    with smtplib.SMTP(smtp_host, smtp_port) as session:
        session.starttls()  # enable security
        session.login(sender_email, app_password)

        # Convert message to string and send via email
        text = message.as_string()
        session.sendmail(sender_email, receiver_email, text)

    print(f'Email sent. Reason: {reason}')
