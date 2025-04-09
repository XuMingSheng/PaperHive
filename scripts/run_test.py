#!/usr/bin/env python3

import subprocess

build_and_run_test = (
    "docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit && docker image prune -f"
)
subprocess.run(build_and_run_test, shell=True)