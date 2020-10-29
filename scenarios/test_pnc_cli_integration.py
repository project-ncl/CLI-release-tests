
import pytest
import logging
from crt import pnccli
from crt import common

def test_scenarion_25():
    suffix = common.rand_string(8)
    logging.warning('Suffix is: ' + suffix)

    prod_name = "Testcase 25 product " + suffix
    prod_short = "TCP-" + suffix
    prod_id = pnccli.run_json("product", "create", "-o", prod_name, "--abbreviation", prod_short)['id']

    prod_version = "1.0"
    prod_version_id = pnccli.run_json("product-version", "create", "-o", prod_version, "--product-id", prod_id)['id']

    prod_milestone = "0.ER1"
    prod_milestone_version = prod_version + "." + prod_milestone
    prod_milestone_start = "2017-01-01"
    prod_milestone_end = "2027-12-31"
    prod_milestone_id = pnccli.run_json("product-milestone", "create", "-o", prod_milestone_version,
                                        "--product-version-id", prod_version_id, "--starting-date", prod_milestone_start,
                                        "--end-date", prod_milestone_end)['id']

    proj_name = "Testcase 25 project " + suffix
    proj_id = pnccli.run_json("project", "create", "-o", proj_name)['id']

    environment_id = pnccli.get_environment()
    if environment_id is None:
        pytest.fail("Couldn't find proper build environment")

    repository_url = "https://github.com/michalszynkiewicz/empty.git"
    found_repository = pnccli.run_json("scm-repository", "list", "-o", "--search-url", repository_url)
    if found_repository:
        repository_id = found_repository[0]['id']
    else:
        repository_id = pnccli.run_json("scm-repository", "create-and-sync", "-o", repository_url)['id']

    bc_name = "testcase-25-bc-01-" + suffix
    bc_revision = "master"
    bc_script = "mvn clean deploy"
    bc_id = pnccli.run_json("build-config", "create", "-o", bc_name, "--project-id", proj_id,
                            "--environment-id", environment_id, "--scm-repository-id", repository_id,
                            "--scm-revision", bc_revision, "--build-script", bc_script)['id']

    bc_desc = "This is testcase 25 BC " + suffix
    pnccli.run("build-config", "update", bc_id, "--description", bc_desc, "--product-version-id", prod_version_id)

    bc = pnccli.run_json("build-config", "get", "-o", bc_id,)
    assert bc['id'] == bc_id
    assert bc['description'] == bc_desc
    assert bc['productVersion']['id'] == prod_version_id

    group_name = "Testcase 25 BC set " + suffix
    group_id = pnccli.run_json("group-config", "create", "-o", group_name, "--product-version-id", prod_version_id)['id']

    pnccli.run("group-config", "add-build-config", group_id, "--bc-id", bc_id)

    group_build_id = pnccli.run_json("group-build", "start", "-o", group_id, "--wait")['id']
    builds = pnccli.run_json("group-build", "list-builds", "-o", group_build_id)

    build_id = None
    for build in builds:
        if build['buildConfigRevision']['id'] == bc_id:
            build_id = build['id']
            break
    if build_id is None:
        pytest.fail("Couldn't find build of Build Configuration " + str(bc_id))

    artifacts = pnccli.run_json("build", "list-built-artifacts", "-o", build_id)
    print("TODO, assert correct number of atifacts", len(artifacts), artifacts)


    out = pnccli.run("product-milestone", "close", prod_milestone_id)
    print("TODO, what with close-milestone output?", out)
