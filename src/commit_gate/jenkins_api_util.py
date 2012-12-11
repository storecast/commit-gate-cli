from jenkinsapi.api import *
from jenkinsapi.build import *

def get_job(jenkinsurl, jobname):
    jenkinsci = Jenkins(jenkinsurl)
    job = jenkinsci[jobname]
    return job


def get_source_branch(build):
    return build.get_actions().get("parameters")[0]['value']


def get_owned_builds(jenkinsurl, jobname, branch_name):
    job = get_job(jenkinsurl, jobname)
    build_dict = job.get_build_dict()
    build_ids = [buildid for buildid in sorted(build_dict.keys(), reverse=True)]
    builds = []
    for build_id in build_ids:
        build = job.get_build(build_id)
        if (get_source_branch(build) == branch_name):
            builds.append(build)
    return builds


def get_status(build):
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
