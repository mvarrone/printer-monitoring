# Printer monitor app

Python app built to monitor values from network printers

## Software used

- Python v3.11.1

## Tested on

- Brand: Brother Industries, Ltd
- Model: [HL-1210W series](https://support.brother.com/g/b/downloadtop.aspx?c=es&lang=es&prod=hl1210w_eu_as)

For this printer in particular, a csv file is downloaded from `/etc/mnt_info.csv` path

You need to manually check the full URI of each device in your network

## Starting

### Step 1/3: Clone the repo, create a virtual environment and install dependencies

a) Clone repository into your machine

```md
git clone https://github.com/mvarrone/printer-monitoring.git
cd printer-monitoring
```

b) Create a virtual environment and install dependencies

<details>
<summary>On Windows</summary>
1.Creating a virtual environment

```md
python -m venv venv
```

2.Activating it

a) Using CMD

```md
.\venv\Scripts\activate.bat
```

b) Using PowerShell

```md
.\venv\Scripts\Activate.ps1
```

3.Installing dependencies

```md
pip install -r requirements.txt
```

4.(OPTIONAL) Deactivating the virtual environment

```md
deactivate
```
</details>

<details>
<summary>On Linux/Mac</summary>
1. Creating a virtual environment

```md
python3 -m venv venv
```

2.Activating it

```md
source venv/bin/activate
```

3.Installing dependencies

```md
pip install -r requirements.txt
```

4.(OPTIONAL) Deactivating the virtual environment

```md
deactivate
```
</details>

### Step 2/3: Some changes before running

1) This project was tested using a Gmail account so you need to create an `application password` inside Google Account settings

    a) Go to [Google Account](https://myaccount.google.com/)

    b) Security tab

    c) How to access to Google > 2-step verification
    
    d) App passwords

* Once there, create an entry like this:

    a) Select app: Other. Name it whatever you want, for example, Python script

    b) Click on the Generate button

    c) Copy the 16 characters in length code that was generated

    d) Paste it in the `app_password` value in the `config.json`

2) Modify `sender_email` and `receiver_email` values in `config.json`

3) Modify `devices.json` in order to add your network printer devices

    Example:
    ```md
    [
        {
            "protocol": "http",
            "ip_address": "192.168.1.5",
            "port": 80,
            "path": "etc",
            "csv_filename": "mnt_info.csv"
        }
    ]
    ```

### Step 3/3: Run the script

<details>
<summary>On Windows</summary>

```md
cd app && python .\main.py 
```
</details>

<details>
<summary>On Linux/Mac</summary>

```md
cd app && python3 .\main.py 
```
</details>

## Example provided
A python3 script and a csv file were provided. See [example](https://github.com/mvarrone/printer-monitoring/tree/main/app/example)

* The intention of providing an example is for you to know how the data was originally downloaded from the printer device and how is processed in the python file

* I found it might be useful for cases where: 
    - there is no printer available in your network
    - the printer exports some other format file
    - the printer does not provide a way to export data and you want to test it anyway
    - the csv file has not the same structure

## Contributing
Contributions to this project are welcome. If you find any issues or have suggestions for improvement, feel free to open an issue or submit a pull request

## License
This project is licensed under the MIT License. See the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) file for details