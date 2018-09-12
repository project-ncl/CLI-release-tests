from __future__ import print_function
from subprocess import Popen
from subprocess import PIPE
import pytest
import json
import sys
import os

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