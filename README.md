# Printer monitor App

Python app built to monitor values from network printers

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

    Once there, create an entry like this:

        a) Select app: Other. Name it wherever you want, for example, Python script

        b) Click on the Generate button

        c) Copy the 16 characters in length code that was generated

        d) Paste it in the `app_password` value in the `config.json`

2) Modify `sender_email` and `receiver_email` values in `config.json`

3) Modify `devices.json` in order to add your network printer

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

## Contributing
Contributions to this project are welcome. If you find any issues or have suggestions for improvement, feel free to open an issue or submit a pull request

## License
This project is licensed under the MIT License. See the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 file for details