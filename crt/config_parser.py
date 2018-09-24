#!/bin/python2.7

import sys
import json

def parse_pnc_cli_conf(file):
    with open(file, 'r') as f:
        config = json.load(f)
        with open("pnc-cli.conf", "w") as of:
            of.write("[PNC]\n")
            of.write("pncurl = " + config['pncRestAddress'].replace("/pnc-rest/rest","") + "\n")
            of.write("keycloakUrl = " + config['keycloakAddress'] + "\n")
            of.write("keycloakrealm = pncredhat\n")
            of.write("keycloakclientid = pncdirect\n")
            of.write("username = " + config['pncUser'] + "\n")
            of.write("password = " + config['pncPassword'] + "\n")

def main():
    # print command line arguments
    parse_pnc_cli_conf(sys.argv[1])

if __name__ == "__main__":
    main()
