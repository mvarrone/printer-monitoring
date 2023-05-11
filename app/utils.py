import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Union


def get_devices() -> List[Dict[str, Union[str, int]]]:
    with open("app/devices.json", "r") as file:
        devices = json.load(file)
    return devices


def get_configurations() -> Dict[str, Union[str, int]]:
    with open("app/config.json", "r") as file:
        configs = json.load(file)
    return configs


def get_supported_brands(filepath) -> Dict[str, Union[str, int]]:   
    try:
        with open(filepath, "r") as file:
            brand_data = json.load(file)
    except FileNotFoundError as e:
        exc_msg = str(e)
        exc_type = type(e).__name__

        message = {"error": True, "error_message": exc_msg, "error_type": exc_type}
        return message
    return brand_data


def send_email(
    sender_email, receiver_email, subject, body, data, reason, alert_type, devices
) -> None:
    config_data = get_configurations()

    smtp_host = config_data.get("smtp").get("host")
    smtp_port = config_data.get("smtp").get("port")

    app_password = (
        config_data.get("email_addresses")
        .get("senders")
        .get("main")
        .get("app_password")
    )

    with open("app/html/template.html", "r") as file:
        html = file.read()

    # Convert data to HTML table rows
    rows = ""
    for key, value in data.items():
        rows += f"<tr><td>{key}</td><td>{value}</td></tr>"

    # Replace the {rows} placeholder in the HTML template with the actual rows
    html = html.replace("{rows}", rows)

    # Create a multipart message and set the headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # message.attach(MIMEText(body, "plain"))
    message.attach(MIMEText(f"<html><body><h3>{body}</h3></body></html>", "html"))
    message.attach(MIMEText(html, "html"))

    # Send the email using a context manager
    with smtplib.SMTP(smtp_host, smtp_port) as session:
        session.starttls()  # enable security
        session.login(sender_email, app_password)

        # Convert message to string and send via email
        text = message.as_string()
        session.sendmail(sender_email, receiver_email, text)

    device_ip_address = devices.get("ip_address")
    print(
        f"({device_ip_address}) Email sent. Reason: {reason}. Alert type: {alert_type}"
    )
