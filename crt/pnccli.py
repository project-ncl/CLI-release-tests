from __future__ import print_function
from subprocess import Popen
from subprocess import PIPE
import json
import os
import pytest
import sys
import time

def process_args(command, *args):
    commands = ["pnc", command]
    for arg in args:
        commands.append(str(arg))
    return commands

def try_run(command, *args):
    p = Popen(process_args(command, *args), stdout=PIPE)
    p.wait()
    out = p.stdout.read()
    return out

def run(command, *args):
    commands = process_args(command, *args)
    #print("Running command: " + " ".join(commands))
    p = Popen(commands, stdout=PIPE)
    p.wait()
    out = p.stdout.read()
    #print("Output:\n" + out)
    if p.returncode != 0:
        pytest.fail("Failed running command ("+str(p.returncode)+")'" + " ".join(commands) + "' with output:\n" + out)
    return out

def run_json(command, *args):
    out = run(command, *args)
    if out == "":
        return {}
    try:
        return json.loads(out)
    except ValueError:
        commands = process_args(command, *args)
        print("Failed parsing json output of command '" + " ".join(commands) + "' with output:\n" + out,
              file=sys.stderr)
        raise


def get_environment():
    environments = run_json("list-environments")
    for environment in environments:
        if "Demo Environment" not in environment['name']:
            return environment['id']

def wait_for_build(build_id, retry):
    out = try_run("get-running-build", build_id)
    while retry > 0 and ('"status": "BUILDING"' in out or '"status": "WAITING_FOR_DEPENDENCIES"' in out):
        time.sleep(60)
        out = try_run("get-running-build", build_id)
        retry -= 1

    if '"status": "BUILDING"' in out:
        pytest.fail("Build " + str(build_id) + " is taking too long to finish.")

    build_status = run_json("get-build-record", build_id)['status']
    assert "DONE" == build_status
    return retry
