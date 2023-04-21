import csv
import math
import sys

import requests
from utils import get_configurations, get_devices, send_email
from datetime import datetime
import time


def download_csv_file(device) -> dict:
    protocol = device.get("protocol")
    ip_address = device.get("ip_address")
    port = device.get("port")
    path = device.get("path")
    csv_filename = device.get("csv_filename")

    url = f"{protocol}://{ip_address}:{port}{path}{csv_filename}"

    try:
        print(f"\nConnecting to {url}...")
        response = requests.get(url)
    except Exception as e:
        exc_type = type(e).__name__
        exc_msg = str(e)
        exc_args = str(e.args)

        print(f"Error trying to connect to {url}")
        print(f"\nException type: {exc_type}")
        print(f"\nException message: {exc_msg}")
        print(f"\nException args: {exc_args}\n")

        results = {"error": True, "ip_address": "", "csv_filename": ""}

        return results

    print(f"Connected to {url}\n")
    with open("csv/" + ip_address + "-" + csv_filename, "wb") as f:
        f.write(response.content)

    results = {"error": False, "ip_address": ip_address, "csv_filename": csv_filename}

    return results


def read_csv_file(ip_address, csv_filename) -> dict:
    with open("csv/" + ip_address + "-" + csv_filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        key_list = list()
        value_list = list()
        for key, value in enumerate(reader):
            if key == 0:
                key_list = value
            else:
                value_list = value

    data = dict(zip(key_list, value_list))

    return data


def process_data(data) -> dict:
    # Clean data
    data = {key: value for key, value in data.items() if key != ""}
    # print(data)

    # data_json = json.dumps(data, indent=2, sort_keys=True)
    # print(data_json)

    return data


def pre_send_email(
    body, reason, subject, remaining_toner_level, configs, data, alert_type
):
    body += f"<br>Current toner value: {remaining_toner_level} %"

    sender_email = configs.get("email_addresses").get("sender")
    receiver_email = configs.get("email_addresses").get("receiver")

    try:
        send_email(
            sender_email=sender_email,
            receiver_email=receiver_email,
            subject=subject,
            body=body,
            data=data,
            reason=reason,
            alert_type=alert_type,
        )
    except Exception as e:
        message = {
            "error": True,
            "error_title": "Error trying to send an email",
            "error_message": str(e),
            "reason_to_send_email": reason,
        }
        return message

    message = {"error": False}
    return message


def check_remaining_toner_level(data, configs, devices, index) -> dict:
    printer_brand = devices[index].get("brand")
    ip_address = data.get("IP Address")

    # FEATURE_1 = "% of Life Remaining(Toner)"
    # THRESHOLD_ERROR_LOW_TONER_LEVEL = 0
    # THRESHOLD_CRITICAL_LOW_TONER_LEVEL = 10
    # THRESHOLD_WARNING_LOW_TONER_LEVEL = 50

    features = configs.get("brands").get(printer_brand).get("features")
    FEATURE_1 = features.get("FEATURE_1")
    remaining_toner_level = int(data.get(FEATURE_1))

    thresholds = (
        configs.get("brands").get(printer_brand).get("thresholds").get("FEATURE_1")
    )
    THRESHOLD_ERROR_LOW_TONER_LEVEL = thresholds.get("THRESHOLD_ERROR_LOW_TONER_LEVEL")
    THRESHOLD_CRITICAL_LOW_TONER_LEVEL = thresholds.get(
        "THRESHOLD_CRITICAL_LOW_TONER_LEVEL"
    )
    THRESHOLD_WARNING_LOW_TONER_LEVEL = thresholds.get(
        "THRESHOLD_WARNING_LOW_TONER_LEVEL"
    )

    if remaining_toner_level == THRESHOLD_ERROR_LOW_TONER_LEVEL:
        body = f"Printer toner level is 0 %"
        reason = "Empty toner level"
        alert_type = "ERROR"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, remaining_toner_level, configs, data, alert_type
        )
        return message

    if remaining_toner_level <= THRESHOLD_CRITICAL_LOW_TONER_LEVEL:
        body = f"Printer with toner level minor than {THRESHOLD_CRITICAL_LOW_TONER_LEVEL} %"
        reason = "Very low toner level"
        alert_type = "CRITICAL"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, remaining_toner_level, configs, data, alert_type
        )
        return message

    if remaining_toner_level <= THRESHOLD_WARNING_LOW_TONER_LEVEL:
        body = (
            f"Printer with toner level minor than {THRESHOLD_WARNING_LOW_TONER_LEVEL} %"
        )
        reason = "Middle toner level"
        alert_type = "WARNING"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, remaining_toner_level, configs, data, alert_type
        )
        return message

    message = {"error": False}
    return message


def check_remaining_drum_unit_level(data, configs) -> dict:
    FEATURE_2 = "% of Life Remaining(Drum Unit)"
    remaining_drum_unit_level = float(data.get(FEATURE_2))

    remaining_drum_unit_level = math.trunc(remaining_drum_unit_level)

    THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL = 90
    if remaining_drum_unit_level <= THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL:
        body = f"Printer with drum unit level minor than {THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL} %"
        body += f"<br>Current drum unit value: {remaining_drum_unit_level} %"
        reason = "Low drum unit level"
        ip_address = data.get("IP Address")
        sender_email = configs.get("email_addresses").get("sender")
        receiver_email = configs.get("email_addresses").get("receiver")
        subject = f"({ip_address}) WARNING: {reason}"

        try:
            send_email(
                sender_email=sender_email,
                receiver_email=receiver_email,
                subject=subject,
                body=body,
                data=data,
                reason=reason,
            )
        except Exception as e:
            message = {
                "error": True,
                "error_title": "Error trying to send an email",
                "error_message": str(e),
                "reason_to_send_email": reason,
            }
            return message

        message = {"error": False}
        return message

    message = {"error": False}
    return message


def check_remaining_life_drum_unit_level(data, configs) -> dict:
    FEATURE_3 = "Remaining Life(Drum Unit)"
    remaining_life_drum_unit_level = int(data.get(FEATURE_3))

    THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT = 8000
    if remaining_life_drum_unit_level <= THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT:
        body = f"Printer with life drum unit value minor than {THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT}"
        body += f"<br>Current life drum unit value: {remaining_life_drum_unit_level}"
        reason = "Low life drum unit level"
        ip_address = data.get("IP Address")
        sender_email = configs.get("email_addresses").get("sender")
        receiver_email = configs.get("email_addresses").get("receiver")
        subject = f"({ip_address}) WARNING: {reason}"

        try:
            send_email(
                sender_email=sender_email,
                receiver_email=receiver_email,
                subject=subject,
                body=body,
                data=data,
                reason=reason,
            )
        except Exception as e:
            message = {
                "error": True,
                "error_title": "Error trying to send an email",
                "error_message": str(e),
                "reason_to_send_email": reason,
            }
            return message

        message = {"error": False}
        return message

    message = {"error": False}
    return message


def some_prestart_checks(devices, configs) -> None:
    if not devices:
        print("File devices.json needs to be configured with at least one device")
        sys.exit(1)

    if configs.get("app_password") == "to_be_completed":
        print("app_password value needs to be generated using Google Account settings")
        sys.exit(1)

    if configs.get("email_addresses").get("sender") == "to_be_completed@gmail.com":
        print("Sender email needs to be set in config.json")
        sys.exit(1)

    if configs.get("email_addresses").get("receiver") == "to_be_completed@gmail.com":
        print("Receiver email needs to be set in config.json")
        sys.exit(1)


def display_error(message):
    print(message.get("error_title"))
    print("Error message: ", message.get("error_message"))
    print(
        "Reason to send an email is: ",
        message.get("reason_to_send_email"),
        "\n",
    )


def main():
    # 0. Load data
    devices = get_devices()
    configs = get_configurations()

    # 1. Execute some checks before starting
    some_prestart_checks(devices, configs)

    # 2. Each device
    for index, device in enumerate(devices):
        print(f"\nDevice {index+1} of {len(devices)}")

        # 2a. Download CSV file
        results = download_csv_file(device)

        if results.get("error"):
            # There was an error trying to connect to the device
            # So, script will skip this device and will try to connect to the next device in devices.json
            continue

        # 2b. Read CSV file
        data = read_csv_file(results.get("ip_address"), results.get("csv_filename"))

        # 2c. Process data
        data = process_data(data)

        # 2d. Check remaining toner level
        message = check_remaining_toner_level(data, configs, devices, index)
        if message.get("error"):
            display_error(message)

        # # 2e. Check remaining drum unit level
        # message = check_remaining_drum_unit_level(data, configs)
        # if message.get("error"):
        #     display_error(message)

        # # 2f. Check remaining life drum unit level
        # message = check_remaining_life_drum_unit_level(data, configs)
        # if message.get("error"):
        #     display_error(message)


if __name__ == "__main__":
    start_time = time.time()

    main()

    print(f"\nTotal execution time: {round(time.time() - start_time, 2)} s")
