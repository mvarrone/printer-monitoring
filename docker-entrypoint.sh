#!/bin/bash

apk add --no-cache bash
chmod +x app/main.py
/bin/bash -c "while true; do python app/main.py; sleep 60; done"
