import pytest
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
    config_path = utils_path+"/tests/make-mead/test-cfg/sso.cfg"
    out = pnccli.run("make-mead", "-c", config_path, "-p", prod_name, "-v", "7.1", "-e", environment_id, "-s" + suffix, "-b")

    set_name = prod_name + "-7.1-all" + suffix
    bc_ids = pnccli.run_json("get-build-configuration-set", "-n", set_name)['build_configuration_ids']

    assert len(bc_ids) == 4

    build_ids = []
    running_builds = pnccli.run_json("list-running-builds")
    for running_build in running_builds:
        if running_build['build_configuration_id'] in bc_ids:
            build_ids.append(running_build['id'])

    assert len(build_ids) == 4

    bc_name = "org.keycloak-keycloak-parent-2.4.0.Final" + suffix
    bc = pnccli.run_json("get-build-configuration", "-n", bc_name)

    assert bc['id'] in bc_ids

    bc_ids.remove(bc['id'])
    assert set(bc_ids) == set(bc['dependency_ids'])

    retry = 40
    for build_id in build_ids:
        retry = pnccli.wait_for_build(build_id, retry)
