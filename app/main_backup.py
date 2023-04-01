import csv
import json

import requests

csv_url = "https://drive.google.com/file/d/1RZw5kX0EWEvheSGtz62e2rTB3T2QRg4y/view?usp=sharing"

# Download the CSV file and read its contents
csv_file_id = csv_url.split("/")[-2]
csv_download_link = f"https://drive.google.com/uc?id={csv_file_id}"
csv_file = requests.get(csv_download_link).content.decode('utf-8').splitlines()
csv_file_reader = csv.reader(csv_file)

# Create a dictionary to store the data fields
data_dict = {}

# Loop through each row of the CSV file and add the data to the dictionary
key_list = list()
value_list = list()
for key, value in enumerate(csv_file_reader):
    if key == 0:
        key_list = value
    else:
        value_list = value

# Join both lists
my_dict = dict(zip(key_list, value_list))

# Clean data
data = {key: value for key, value in my_dict.items() if key != ''}

# Dump data
data_json = json.dumps(data, indent=2, sort_keys=True)

print(data_json)
