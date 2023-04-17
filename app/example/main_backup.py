import csv
import json

# Loop through each row of the CSV file and add the data to a dictionary
key_list = list()
value_list = list()

filename = "mnt_info_casa_nico"
with open(f"{filename}.csv", newline='') as csvfile:
    reader = csv.reader(csvfile)
    for key, value in enumerate(reader):
        if key == 0:
            key_list = value
        else:
            value_list = value

# Join both lists
my_dict = dict(zip(key_list, value_list))

# Clean data
data = {key: value for key, value in my_dict.items() if key != ''}
# print(data)

data_json = json.dumps(data, indent=2, sort_keys=True)
print(data_json)

with open(f"results-{filename}.json", "w") as f:
    f.write(data_json)
