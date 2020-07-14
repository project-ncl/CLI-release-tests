#!/bin/python2.7

import sys
import json

def parse_pnc_cli_conf(file):
    with open(file, 'r') as f:
        config = json.load(f)
        with open("config.yaml", "w") as of:
            of.write("profile:\n")
            of.write('- name: "default"\n')
            of.write('  pnc:\n')
            of.write('      url: "' + config['pncRestAddress'].replace("/rest-new","") + '"\n')
            of.write('      bifrostBaseurl: ""\n')
            of.write('  keycloak:\n')
            of.write('      url: "' + config['keycloakAddress'] + '"\n')
            of.write('      realm: "pncredhat"\n')
            of.write('      username: "' + config['pncUser'] + '"\n')
            of.write('      clientSecret: "' + config['pncPassword'] + '"\n')

def main():
    # print command line arguments
    parse_pnc_cli_conf(sys.argv[1])

if __name__ == "__main__":
    main()
