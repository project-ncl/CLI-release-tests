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
    out = p.communicate()[0]
    out = str(out, encoding="utf-8")
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
    environments = run_json("environment", "list", "-o")
    for environment in environments:
        if "builder-rhel-7-j8-mvn3.6.0" in environment['systemImageId'] and not environment['deprecated']:
            return environment['id']

