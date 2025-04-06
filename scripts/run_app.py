#!/usr/bin/env python3

import subprocess

cmd = (
    "docker-compose -f docker-compose.yml up --build -d"
)

subprocess.run(cmd, shell=True)