import pytest
import time
import os
from crt import pnccli
from crt import common

def test_scenarion_10():
    utils_path = os.environ.get('PNC_UTILS_PATH')
    if utils_path is None:
        pytest.fail("You need to specify PNC_UTILS_PATH env. variable.")


    prod_name = "Red Hat Single Sign-On"
    prod_short = "RH-SSO"
    out = pnccli.try_run("get-product", "-n", prod_name)
    if prod_name in out:
        prod_id = pnccli.run_json("get-product", "-n", prod_name)['id']
    else:
        prod_id = pnccli.run_json("create-product", prod_name, prod_short)['id']

    environment_id = pnccli.get_environment()
    if environment_id is None:
        pytest.fail("Couldn't find proper build environment")

    suffix = "-tc10-" + common.rand_string(8)
    # make-mead -c sso-real.cfg -p "Red Hat Single Sign-On" -v 7.1 -e 3 -s _npm_ANYTHING -b
    out = pnccli.run("make-mead", "-c", utils_path+"/make-mead/test-cfg/sso.cfg", "-p", "Red Hat Single Sign-On", "-v", "7.1", "-e", environment_id, "-s" + suffix, "-b")

