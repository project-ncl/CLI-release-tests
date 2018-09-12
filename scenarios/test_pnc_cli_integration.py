
import pytest
import time
from crt import pnccli
from crt import common

def test_scenarion_25():
    suffix = common.rand_string(8)

    prod_name = "Testcase 25 product " + suffix
    prod_short = "TCP-" + suffix
    prod_id = pnccli.run_json("create-product", prod_name, prod_short)['id']

    prod_version = "1.0"
    prod_version_id = pnccli.run_json("create-product-version", prod_id, prod_version)['id']

    prod_milestone = "0.ER1"
    prod_milestone_start = "2017-01-01"
    prod_milestone_end = "2027-12-31"
    prod_milestone_url = "http://example.com"
    prod_milestone_id = pnccli.run_json("create-milestone", prod_version_id, prod_milestone, prod_milestone_start,
                                        prod_milestone_end, prod_milestone_url)['id']

    proj_name = "Testcase 25 project " + suffix
    proj_id = pnccli.run_json("create-project", proj_name)['id']

    environments = pnccli.run_json("list-environments")
    environment_id = pnccli.get_environment()
    if environment_id is None:
        pytest.fail("Couldn't find proper build environment")

    repository_url = "https://github.com/michalszynkiewicz/empty.git"
    found_repository = pnccli.run_json("search-repository-configuration", repository_url)
    if found_repository:
        repository_id = found_repository[0]['id']
    else:
        repository_id = pnccli.run_json("create-repository-configuration", repository_url)['id']

    bc_name = "testcase-25-bc-01-" + suffix
    bc_revision = "master"
    bc_script = "mvn clean deploy"
    bc_id = pnccli.run_json("create-build-configuration", bc_name, proj_id, environment_id,
                                      repository_id, bc_revision, bc_script)['id']

    bc_desc = "This is testcase 25 BC " + suffix
    pnccli.run("update-build-configuration", bc_id, "-d", bc_desc, "-pvi", prod_version_id)

    bc = pnccli.run_json("get-build-configuration", "-i", bc_id)
    assert bc['id'] == bc_id
    assert bc['description'] == bc_desc
    assert bc['product_version_id'] == prod_version_id

    group_name = "Testcase 25 BC set " + suffix
    group_id = pnccli.run_json("create-build-configuration-set", group_name, "-pvi", prod_version_id)['id']

    pnccli.run("add-build-configuration-to-set", "-sid", group_id, "-cid", bc_id)

    pnccli.run("build-set", "-i", group_id)

    running_builds = pnccli.run_json("list-running-builds")
    build_id = None
    for running_build in running_builds:
        if running_build['build_configuration_id'] == bc_id:
            build_id = running_build['id']
            break
    if build_id is None:
        pytest.fail("Couldn't find running build of Build Configuration " + str(bc_id))

    out = pnccli.try_run("get-running-build", build_id)
    retry = 40
    while retry > 0 and '"status": "BUILDING"' in out:
        time.sleep(30)
        out = pnccli.try_run("get-running-build", build_id)
        retry -= 1

    if '"status": "BUILDING"' in out:
        pytest.fail("Build " + str(build_id) + " is taking too long to finish.")

    build_status = pnccli.run_json("get-build-record", build_id)['status']
    assert "DONE" == build_status

    artifacts = pnccli.run_json("list-built-artifacts", build_id)
    print("TODO, asser correct number of atifacts", len(artifacts), artifacts)


    out = pnccli.run("close-milestone", prod_milestone_id, "--wait")
    print("TODO, what with close-milestone output?", out)
