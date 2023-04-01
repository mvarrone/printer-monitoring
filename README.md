# Printer monitor app

Python app built to monitor values from network printers

## Software used

- Python v3.11.1

## Tested on

- Brand: Brother Industries, Ltd
- Model: [HL-1210W series](https://support.brother.com/g/b/downloadtop.aspx?c=es&lang=es&prod=hl1210w_eu_as)

For this printer in particular, a csv file is downloaded from `/etc/mnt_info.csv`

You need to manually check the full URI of each device in your network

## Before start

1) This project was tested using a Gmail account so you need to create an application password in Google Account settings

    a) Go to [Google Account](https://myaccount.google.com/)

    b) Security tab

    c) How to access to Google > 2 step verification
    
    d) App passwords

* Once there, create an entry like this:

    a) Select app: Other. Name it wherever you want, for example, Python script

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

## Example provided
A python3 script and a csv file were provided. See [example](https://github.com/mvarrone/printer-monitoring/tree/main/app/html)

* The intention of providing an example is for you to know how the data was originally downloaded from the printer device and how is processed in the python file

* I found it might be useful for cases where: 
    - there is no printer available in your network
    - or maybe the printer exports some other format file
    - or maybe the printer does not provide a way to export data
    - or the csv file has not the same structure

## Contributing
Contributions to this project are welcome. If you find any issues or have suggestions for improvement, feel free to open an issue or submit a pull request

## License
This project is licensed under the MIT License. See the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 file for details