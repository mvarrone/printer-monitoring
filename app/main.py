import csv
import sys

import requests
from utils import get_configurations, get_devices, send_email


def download_csv_file(device) -> dict:
    protocol = device.get('protocol')
    ip_address = device.get('ip_address')
    port = device.get('port')
    path = device.get('path')
    csv_filename = device.get('csv_filename')

    url = f"{protocol}://{ip_address}:{port}/{path}/{csv_filename}"

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

        results = {
            "error": True,
            "ip_address": "",
            "csv_filename": ""
        }

        return results

    print(f"Connected to {url}")
    with open("csv/" + ip_address + "-" + csv_filename, "wb") as f:
        f.write(response.content)

    results = {
        "error": False,
        "ip_address": ip_address,
        "csv_filename": csv_filename
    }

    return results


def read_csv_file(ip_address, csv_filename) -> dict:
    with open("csv/" + ip_address + "-" + csv_filename, newline='') as csvfile:
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
    data = {key: value for key, value in data.items() if key != ''}
    # print(data)

    # data_json = json.dumps(data, indent=2, sort_keys=True)
    # print(data_json)

    return data


def check_remaining_toner_level(data, configs) -> dict:
    remaining_toner_level = int(data.get("% of Life Remaining(Toner)"))

    THRESHOLD_WARNING_LOW_TONER_LEVEL = 50
    if remaining_toner_level < THRESHOLD_WARNING_LOW_TONER_LEVEL:
        body = f"Printer with toner level minor than {THRESHOLD_WARNING_LOW_TONER_LEVEL} %"
        body += f"<br>Current toner value: {remaining_toner_level} %"

        try:
            send_email(
                sender_email=configs.get("sender_email"),
                receiver_email=configs.get("receiver_email"),
                subject="WARNING: Low toner level",
                body=body,
                data=data,
                reason="Low toner level")
        except Exception as e:
            print("-- Error trying to send an email: --", e)
            message = {
                "error": True,
                "error_message": str(e)
            }

            return message

        message = {
            "error": False
        }

        return message


def check_remaining_drum_unit_level(data, configs):
    # remaining_drum_unit_level = data.get("% of Life Remaining(Drum Unit)")
    # print("% of Life Remaining(Drum Unit): ", remaining_drum_unit_level)
    pass


def some_prestart_checks(devices, configs) -> None:
    if not devices:
        print("File devices.json needs to be configured with at least one device")
        sys.exit(1)

    if configs.get("app_password") == "0000111122223333":
        print("app_password value needs to be generated using Google Account settings")
        sys.exit(1)

    if configs.get("sender_email") == "example@gmail.com":
        print("sender_email value needs to be configured in config.json")
        sys.exit(1)

    if configs.get("receiver_email") == "example@gmail.com":
        print("receiver_email value needs to be configured in config.json")
        sys.exit(1)


def main():
    # 0. Load data
    devices = get_devices()
    configs = get_configurations()

    # 1. Execute some checks before starting
    some_prestart_checks(devices, configs)

    for index, device in enumerate(devices, start=1):
        print(f"\nDevice {index} of {len(devices)}")

        # 2. Download CSV file
        results = download_csv_file(device)

        if results.get("error"):
            # There was an error trying to connect to the device
            # So, the next action will be try to connect to the next device in devices.json
            continue

        # 3. Read CSV file
        data = read_csv_file(
            results.get("ip_address"),
            results.get("csv_filename")
        )

        # 4. Process data
        data = process_data(data)

        # 5. Check remaining toner level
        check_remaining_toner_level(data, configs)

        # 6. Check remaining drum unit level
        check_remaining_drum_unit_level(data, configs)


if __name__ == '__main__':
    main()
