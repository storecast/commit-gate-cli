from jenkinsapi.api import *
from jenkinsapi.build import *

def get_job(jenkinsurl, jobname):
    jenkinsci = Jenkins(jenkinsurl)
    job = jenkinsci[jobname]
    return job


def get_source_branch(build):
    return build.get_actions().get("parameters")[0]['value']


def is_own_build(branch_name, build):
    return get_source_branch(build) == branch_name


def get_owned_builds(job, branch_name):
    build_dict = job.get_build_dict()
    build_ids = [buildid for buildid in sorted(build_dict.keys(), reverse=True)]
    builds = []
    for build_id in build_ids:
        build = job.get_build(build_id)
        if (is_own_build(branch_name, build)):
            builds.append(build)
    return builds


def get_new_status(build):
    """
     new because build.is_running() triggers poll.
     """
    if(build.is_running()):
        return "RUNNING"
    return build._data["result"]


def get_resultset(build):
    #todo copied from jenkinsapi.api and commented out FailedNoResults exception. Find out why and fix in the jenkinsapi library
    """
    Obtain detailed results for this build.
    """
    result_url = build.get_result_url()
    if build.STR_TOTALCOUNT not in build.get_actions():
        raise NoResults("%s does not have any published results" % str(build))
    buildstatus = build.get_status()
    #    if buildstatus in [ STATUS_FAIL, RESULTSTATUS_FAILURE, STATUS_ABORTED ]:
    #        raise FailedNoResults( build.STR_TPL_NOTESTS_ERR % ( str(build), buildstatus ) )
    if not build.get_actions()[build.STR_TOTALCOUNT]:
        raise NoResults(build.STR_TPL_NOTESTS_ERR % ( str(build), buildstatus ))
    obj_results = ResultSet(result_url, build=build)
    return obj_results


def has_build_started(job, original_build_no, source):
    return not is_own_build(source, job.get_last_build()) or original_build_no >= job.get_last_buildnumber()


def get_url(build):
    return build._data['url']


def get_test_cases(build):
    cases = []
    try:
        resultset = get_resultset(build)
    except NoResults:
        return cases
    for result_module in resultset._data['childReports']:
        for suites in result_module['result']['suites']:
            for case in suites['cases']:
                cases.append(case)
    return cases


def get_total_count(build):
    try:
        resultset = get_resultset(build)
    except NoResults:
        return 0
    total_count_ = resultset._data['totalCount']
    return total_count_


def get_fail_count(build):
    try:
        resultset = get_resultset(build)
    except NoResults:
        return 0
    fail_count_ = resultset._data['failCount']
    return fail_count_