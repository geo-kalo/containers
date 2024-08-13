#!/bin/bash
create_venv() {

    python3 -m venv /venv
    source /venv/bin/activate
    pip install jinja2 
    python3 /workdir/file_generator.py
    python3 /workdir/file_generator_teletegraf.py
   
}

create_venv

