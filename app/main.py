import concurrent.futures
import csv
import math
import sys
import time
from typing import Dict, List, Union

import requests
from utils import get_configurations, get_devices, get_supported_brands, send_email


def download_csv_file(device) -> Dict[str, Union[bool, str]]:
    protocol = device.get("protocol")
    ip_address = device.get("ip_address")
    port = device.get("port")
    path = device.get("path")
    csv_filename = device.get("csv_filename")

    url = f"{protocol}://{ip_address}:{port}{path}{csv_filename}"

    connect_timeout = 2  # seconds
    read_timeout = 2  # seconds

    try:
        print(f"Connecting to {url}...")
        response = requests.get(url, timeout=(connect_timeout, read_timeout))
    except Exception as e:
        exc_type = type(e).__name__
        exc_msg = str(e)
        exc_args = str(e.args)

        print(f"Error trying to connect to {url}")
        # print(f"\nException type: {exc_type}")
        # print(f"\nException message: {exc_msg}")
        # print(f"\nException args: {exc_args}\n")

        results = {"error": True, "ip_address": "", "csv_filename": ""}
        return results

    print(f"Connected to {url}")
    with open("app/csv/" + ip_address + "-" + csv_filename, "wb") as f:
        f.write(response.content)

    results = {"error": False, "ip_address": ip_address, "csv_filename": csv_filename}

    return results


def read_csv_file(ip_address, csv_filename) -> Dict[str, str]:
    with open("app/csv/" + ip_address + "-" + csv_filename, newline="") as csvfile:
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


def process_data(data) -> Dict[str, str]:
    # Clean data
    data = {key: value for key, value in data.items() if key != ""}
    # print(data)

    # print(json.dumps(data, indent=2, sort_keys=True))
    return data


def using_first_backup_email_address(
    configs, receiver_email, subject, body, data, reason, alert_type, devices
):
    print("\n-- EXCEPTION: Daily user sending quota exceeded --")
    print(f"-- Address email with problems: {sender_email} --")

    sender_email = (
        configs.get("email_addresses")
        .get("senders")
        .get("first_backup")  # Using another account to send data: address
        .get("address")
    )

    app_password = (
        configs.get("email_addresses")
        .get("senders")
        .get("first_backup")  # Using another account to send data: password
        .get("app_password")
    )

    print(f"New account to be used: {sender_email}")

    send_email(
        sender_email=sender_email,
        receiver_email=receiver_email,
        subject=subject,
        body=body,
        data=data,
        reason=reason,
        alert_type=alert_type,
        devices=devices,
    )


def pre_send_email(
    body, reason, subject, current_value, configs, data, alert_type, devices
) -> Dict[str, Union[bool, str]]:
    if "life drum unit level" in reason:
        body += f"<br>Current value: {current_value}"
    else:
        body += f"<br>Current value: {current_value} %"

    sender_email = (
        configs.get("email_addresses").get("senders").get("main").get("address")
    )
    receiver_email = configs.get("email_addresses").get("receiver").get("address")

    try:
        send_email(
            sender_email=sender_email,
            receiver_email=receiver_email,
            subject=subject,
            body=body,
            data=data,
            reason=reason,
            alert_type=alert_type,
            devices=devices,
        )
    except Exception as e:
        # TODO

        # print(f"\nException in pre_send_email(...) > send_email(...): {e}")

        # if "Daily user sending quota exceeded" in str(e):
        #     using_first_backup_email_address(
        #         configs,
        #         receiver_email,
        #         subject,
        #         body,
        #         data,
        #         reason,
        #         alert_type,
        #         devices,
        #     )

        message = {
            "error": True,
            "error_title": f"({devices.get('ip_address')}) Error trying to send an email",
            "error_message": str(e),
            "reason_to_send_email": reason,
        }
        return message

    message = {"error": False}
    return message


def check_remaining_toner_level(data, configs, devices) -> Dict[str, Union[bool, str]]:
    printer_brand = devices.get("brand").lower()
    printer_ip_address = devices.get("ip_address")

    brand_data = get_supported_brands(f"app/supported_brands/{printer_brand}.json")
    if brand_data.get("error"):
        brand_data["ip_address"] = printer_ip_address
        return brand_data

    features = brand_data.get("features")
    FEATURE_1 = features.get("FEATURE_1")
    remaining_toner_level = int(data.get(FEATURE_1))

    thresholds = brand_data.get("thresholds")
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
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    if remaining_toner_level <= THRESHOLD_CRITICAL_LOW_TONER_LEVEL:
        current_value = remaining_toner_level
        body = f"Printer with toner level minor than {THRESHOLD_CRITICAL_LOW_TONER_LEVEL} %"
        reason = "Very low toner level"
        alert_type = "CRITICAL"
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    if remaining_toner_level <= THRESHOLD_WARNING_LOW_TONER_LEVEL:
        current_value = remaining_toner_level
        body = (
            f"Printer with toner level minor than {THRESHOLD_WARNING_LOW_TONER_LEVEL} %"
        )
        reason = "About toner level"
        alert_type = "WARNING"
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    message = {"error": False}
    return message


def check_remaining_drum_unit_level(
    data, configs, devices
) -> Dict[str, Union[bool, str]]:
    printer_brand = devices.get("brand").lower()
    printer_ip_address = devices.get("ip_address")

    brand_data = get_supported_brands(f"app/supported_brands/{printer_brand}.json")
    if brand_data.get("error"):
        brand_data["ip_address"] = printer_ip_address
        return brand_data

    features = brand_data.get("features")
    FEATURE_2 = features.get("FEATURE_2")

    remaining_drum_unit_level = float(data.get(FEATURE_2))
    remaining_drum_unit_level = math.trunc(remaining_drum_unit_level)
    remaining_drum_unit_level = 38

    thresholds = brand_data.get("thresholds")
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
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    if remaining_drum_unit_level <= THRESHOLD_CRITICAL_LOW_DRUM_UNIT_LEVEL:
        current_value = remaining_drum_unit_level
        body = f"Printer with drum unit level minor than {THRESHOLD_CRITICAL_LOW_DRUM_UNIT_LEVEL} %"
        reason = "Very low drum unit level"
        alert_type = "CRITICAL"
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    if remaining_drum_unit_level <= THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL:
        current_value = remaining_drum_unit_level
        body = f"Printer with drum unit level minor than {THRESHOLD_WARNING_LOW_DRUM_UNIT_LEVEL} %"
        reason = "About drum unit level"
        alert_type = "WARNING"
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    message = {"error": False}
    return message


def check_remaining_life_drum_unit_level(
    data, configs, devices
) -> Dict[str, Union[bool, str]]:
    printer_brand = devices.get("brand").lower()
    printer_ip_address = devices.get("ip_address")

    brand_data = get_supported_brands(f"app/supported_brands/{printer_brand}.json")
    if brand_data.get("error"):
        brand_data["ip_address"] = printer_ip_address
        return brand_data

    features = brand_data.get("features")
    FEATURE_3 = features.get("FEATURE_3")
    remaining_life_drum_unit_level = int(data.get(FEATURE_3))

    thresholds = brand_data.get("thresholds")
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
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    if remaining_life_drum_unit_level <= THRESHOLD_CRITICAL_LOW_LIFE_DRUM_UNIT_LEVEL:
        current_value = remaining_life_drum_unit_level
        body = f"Printer with life drum unit level minor than {THRESHOLD_CRITICAL_LOW_LIFE_DRUM_UNIT_LEVEL}"
        reason = "Very low life drum unit level"
        alert_type = "CRITICAL"
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    if remaining_life_drum_unit_level <= THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT_LEVEL:
        current_value = remaining_life_drum_unit_level
        body = f"Printer with life drum unit level minor than {THRESHOLD_WARNING_LOW_LIFE_DRUM_UNIT_LEVEL}"
        reason = "About life drum unit level"
        alert_type = "WARNING"
        subject = f"({printer_ip_address}) {alert_type}: {reason}"

        message = pre_send_email(
            body, reason, subject, current_value, configs, data, alert_type, devices
        )
        return message

    message = {"error": False}
    return message


def some_prestart_checks(devices, configs) -> None:
    if not devices:
        print("File devices.json needs to be configured with at least one device")
        sys.exit(1)

    if (
        configs.get("email_addresses").get("senders").get("main").get("app_password")
        == "to_be_completed"
    ):
        print(
            "app_password value for the main email address needs to be generated using Google Account settings and set in app/config.json"
        )
        sys.exit(1)

    if (
        configs.get("email_addresses").get("senders").get("main").get("address")
        == "to_be_completed@gmail.com"
    ):
        print("Main email sender address needs to be set in app/config.json")
        sys.exit(1)

    if (
        configs.get("email_addresses").get("receiver").get("address")
        == "to_be_completed@gmail.com"
    ):
        print("A receiver email address needs to be set in app/config.json")
        sys.exit(1)

    # OPTIONAL CHECKS
    # address for the 1st backup account
    # app_password for the 1st backup account


def display_error(result) -> None:
    if result.get("error_type") == "FileNotFoundError":
        ip_address = result.get("ip_address")
        error_message = result.get("error_message")
        print(f"({ip_address}) Error message: {error_message}")
    else:
        print("\n", result.get("error_title"))
        print("Error message: ", result.get("error_message"))
        print("Reason to send an email is: ", result.get("reason_to_send_email"), "\n")


def general_treatment(device, configs) -> Dict[str, Union[bool, str]]:
    # 2a. Download CSV file
    results = download_csv_file(device)

    if results.get("error"):
        return {
            "status": False,
            "device_IP": device.get("ip_address"),
        }  # if connection was not OK

    # 2b. Read CSV file
    raw_data = read_csv_file(results.get("ip_address"), results.get("csv_filename"))

    # 2c. Process data
    clean_data = process_data(raw_data)

    # 2d. Parallel task execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 2d.1. Check remaining toner level
        future1 = executor.submit(
            check_remaining_toner_level, clean_data, configs, device
        )

        # 2d.2. Check remaining drum unit level
        future2 = executor.submit(
            check_remaining_drum_unit_level, clean_data, configs, device
        )

        # 2d.3. Check remaining life drum unit level
        future3 = executor.submit(
            check_remaining_life_drum_unit_level, clean_data, configs, device
        )

    # 2e. Get task results
    result1 = future1.result()
    result2 = future2.result()
    result3 = future3.result()

    if result1.get("error"):
        display_error(result1)

    if result2.get("error"):
        display_error(result2)

    if result3.get("error"):
        display_error(result3)

    return {
        "status": True,
        "device_IP": device.get("ip_address"),
    }  # if connection was OK


def gather_connection_data(futures) -> Dict[str, Union[int, List[str]]]:
    results = {"successes": 0, "failures": 0, "conn_ok": [], "conn_nok": []}

    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        device_ip = result.get("device_IP")

        if result.get("status"):
            results["successes"] += 1
            results["conn_ok"].append(device_ip)
        else:
            results["failures"] += 1
            results["conn_nok"].append(device_ip)

    return results


def display_connection_data(results) -> None:
    successes = results.get("successes")
    failures = results.get("failures")
    conn_ok = results.get("conn_ok")
    conn_nok = results.get("conn_nok")

    total_devices = successes + failures
    percentage_OK = 100 * round(successes / total_devices, 2)
    percentage_NOK = 100 * round(failures / total_devices, 2)

    print("\n--- Results on connections---")

    print(f"Successful connections: {successes}/{total_devices} ({percentage_OK} %)")
    for device in conn_ok:
        print(f"  - {device}")

    print(f"Failed connections:     {failures}/{total_devices} ({percentage_NOK} %)")
    for device in conn_nok:
        print(f"  - {device}")


def main() -> None:
    # 0. Load data
    devices = get_devices()
    configs = get_configurations()

    # 1. Execute some checks before starting
    some_prestart_checks(devices, configs)

    # 2. Parallel device connection
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(general_treatment, device, configs) for device in devices
        ]

    # 3. Data about connections
    # 3a. Gather data
    results = gather_connection_data(futures)

    # 3b. Print data results
    display_connection_data(results)


if __name__ == "__main__":
    start_time = time.time()

    main()

    print(f"\nTotal execution time: {round(time.time() - start_time, 2)} s")
