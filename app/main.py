import concurrent.futures
import csv
import math
import sys
import time

import requests
from utils import get_configurations, get_devices, send_email


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


def pre_send_email(body, reason, subject, current_value, configs, data, alert_type):
    if "life drum unit level" in reason:
        body += f"<br>Current value: {current_value}"
    else:
        body += f"<br>Current value: {current_value} %"

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

    features = configs.get("brands").get(printer_brand).get("features")
    FEATURE_1 = features.get("FEATURE_1")
    remaining_toner_level = int(data.get(FEATURE_1))

    thresholds = configs.get("brands").get(printer_brand).get("thresholds")
    thresholds_for_feature_1 = thresholds.get("FEATURE_1")
    THRESHOLD_ERROR_LOW_TONER_LEVEL = thresholds_for_feature_1.get(
        "THRESHOLD_ERROR_LOW_TONER_LEVEL"
    )
    THRESHOLD_CRITICAL_LOW_TONER_LEVEL = thresholds_for_feature_1.get(
        "THRESHOLD_CRITICAL_LOW_TONER_LEVEL"
    )
    THRESHOLD_WARNING_LOW_TONER_LEVEL = thresholds_for_feature_1.get(
        "THRESHOLD_WARNING_LOW_TONER_LEVEL"
    )

    if remaining_toner_level == THRESHOLD_ERROR_LOW_TONER_LEVEL:
        current_value = remaining_toner_level
        body = "Printer toner level is empty"
        reason = "Empty toner level"
        alert_type = "ERROR"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    if remaining_toner_level <= THRESHOLD_CRITICAL_LOW_TONER_LEVEL:
        current_value = remaining_toner_level
        body = f"Printer with toner level minor than {THRESHOLD_CRITICAL_LOW_TONER_LEVEL} %"
        reason = "Very low toner level"
        alert_type = "CRITICAL"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    if remaining_toner_level <= THRESHOLD_WARNING_LOW_TONER_LEVEL:
        current_value = remaining_toner_level
        body = (
            f"Printer with toner level minor than {THRESHOLD_WARNING_LOW_TONER_LEVEL} %"
        )
        reason = "About toner level"
        alert_type = "WARNING"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    message = {"error": False}
    return message


def check_remaining_drum_unit_level(data, configs, devices, index) -> dict:
    printer_brand = devices[index].get("brand")
    ip_address = data.get("IP Address")

    features = configs.get("brands").get(printer_brand).get("features")
    FEATURE_2 = features.get("FEATURE_2")

    remaining_drum_unit_level = float(data.get(FEATURE_2))
    remaining_drum_unit_level = math.trunc(remaining_drum_unit_level)
    remaining_drum_unit_level = 38

    thresholds = configs.get("brands").get(printer_brand).get("thresholds")
    thresholds_for_feature_2 = thresholds.get("FEATURE_2")
    THRESHOLD_ERROR_LOW_DRUM_UNIT_LEVEL = thresholds_for_feature_2.get(
        "THRESHOLD_ERROR_LOW_DRUM_UNIT_LEVEL"
    )
    THRESHOLD_CRITICAL_LOW_DRUM_UNIT_LEVEL = thresholds_for_feature_2.get(
        "THRESHOLD_CRITICAL_LOW_DRUM_UNIT_LEVEL"
    )
    THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL = thresholds_for_feature_2.get(
        "THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL"
    )

    if remaining_drum_unit_level == THRESHOLD_ERROR_LOW_DRUM_UNIT_LEVEL:
        current_value = remaining_drum_unit_level
        body = "Printer drum unit level is empty"
        reason = "Empty drum unit level"
        alert_type = "ERROR"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    if remaining_drum_unit_level <= THRESHOLD_CRITICAL_LOW_DRUM_UNIT_LEVEL:
        current_value = remaining_drum_unit_level
        body = f"Printer with drum unit level minor than {THRESHOLD_CRITICAL_LOW_DRUM_UNIT_LEVEL} %"
        reason = "Very low drum unit level"
        alert_type = "CRITICAL"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    if remaining_drum_unit_level <= THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL:
        current_value = remaining_drum_unit_level
        body = f"Printer with drum unit level minor than {THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL} %"
        reason = "About drum unit level"
        alert_type = "WARNING"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    message = {"error": False}
    return message


def check_remaining_life_drum_unit_level(data, configs, devices, index) -> dict:
    printer_brand = devices[index].get("brand")
    ip_address = data.get("IP Address")

    features = configs.get("brands").get(printer_brand).get("features")
    FEATURE_3 = features.get("FEATURE_3")
    remaining_life_drum_unit_level = int(data.get(FEATURE_3))

    thresholds = configs.get("brands").get(printer_brand).get("thresholds")
    thresholds_for_feature_3 = thresholds.get("FEATURE_3")
    THRESHOLD_ERROR_LOW_LIFE_DRUM_UNIT_LEVEL = thresholds_for_feature_3.get(
        "THRESHOLD_ERROR_LOW_LIFE_DRUM_UNIT_LEVEL"
    )
    THRESHOLD_CRITICAL_LOW_LIFE_DRUM_UNIT_LEVEL = thresholds_for_feature_3.get(
        "THRESHOLD_CRITICAL_LOW_LIFE_DRUM_UNIT_LEVEL"
    )
    THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT_LEVEL = thresholds_for_feature_3.get(
        "THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT_LEVEL"
    )

    if remaining_life_drum_unit_level == THRESHOLD_ERROR_LOW_LIFE_DRUM_UNIT_LEVEL:
        current_value = remaining_life_drum_unit_level
        body = "Printer life drum unit level is empty"
        reason = "Empty life drum unit level"
        alert_type = "ERROR"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    if remaining_life_drum_unit_level <= THRESHOLD_CRITICAL_LOW_LIFE_DRUM_UNIT_LEVEL:
        current_value = remaining_life_drum_unit_level
        body = f"Printer with life drum unit level minor than {THRESHOLD_CRITICAL_LOW_LIFE_DRUM_UNIT_LEVEL}"
        reason = "Very low life drum unit level"
        alert_type = "CRITICAL"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
        return message

    if remaining_life_drum_unit_level <= THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT_LEVEL:
        current_value = remaining_life_drum_unit_level
        body = f"Printer with life drum unit level minor than {THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT_LEVEL}"
        reason = "About life drum unit level"
        alert_type = "WARNING"
        subject = f"({ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type
        )
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


def display_error(result):
    print(result.get("error_title"))
    print("Error message: ", result.get("error_message"))
    print("Reason to send an email is: ", result.get("reason_to_send_email"), "\n")


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

        # Execution of functions in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 2d. Check remaining toner level
            future1 = executor.submit(
                check_remaining_toner_level, data, configs, devices, index
            )

            # 2e. Check remaining drum unit level
            future2 = executor.submit(
                check_remaining_drum_unit_level, data, configs, devices, index
            )

            # 2f. Check remaining life drum unit level
            future3 = executor.submit(
                check_remaining_life_drum_unit_level, data, configs, devices, index
            )

        # Get task results
        result1 = future1.result()
        result2 = future2.result()
        result3 = future3.result()

        if result1.get("error"):
            display_error(result1)

        if result2.get("error"):
            display_error(result2)

        if result3.get("error"):
            display_error(result3)


if __name__ == "__main__":
    start_time = time.time()

    main()

    print(f"\nTotal execution time: {round(time.time() - start_time, 2)} s")
