#!/bin/bash
create_venv() {

    python3 -m venv /venv
    source /venv/bin/activate
    pip install -U pip
    pip install -r /tmp/packets
    #fastapi run main.py &
}

create_venv


#/etc/init.d/apache2 start 
