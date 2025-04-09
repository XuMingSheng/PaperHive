#!/usr/bin/env python3

import subprocess

build_and_run_app = "docker-compose -f docker-compose.yml up --build -d && docker image prune -f"
subprocess.run(build_and_run_app, shell=True)