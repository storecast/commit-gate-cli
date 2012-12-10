#!/usr/bin/env python
import cli.app
from jenkins_api_util import get_status, get_resultset, get_owned_builds, get_job

@cli.app.CommandLineApp(name="commit-gate")
def jenkins_cli(app):
    jenkinsurl = "http://ci:8080/jenkins"
    jobname = "REAKTOR_commit-gate"
    if(app.params.action == "build"):
        print("Triggering a new build")
        get_job(jenkinsurl, jobname).invoke(
            params={'SourceBranch': app.params.source, 'TargetBranch': app.params.target, 'dryrun': 'false',
                    'delay': '0sec'})
        print_status(jenkinsurl, jobname, app.params.source)
        return
    if(app.params.action == "status"):
        print_status(jenkinsurl, jobname, app.params.source)
        return
    print("Please specify a correct action [build|status].")
    exit()

jenkins_cli.add_param("action", help="[build|status]", default=False, type=str)
jenkins_cli.add_param("-source", help="specify the source branch", required=True)
jenkins_cli.add_param("-target", help="specify the target branch", required=False)

def run():
    jenkins_cli.run()


def print_build_status(build):
    print("status: " + get_status(build))
    print("url: " + build._data['url'])
    if(build.has_resultset()):
        resultset = get_resultset(build)
        print("totalCount:  %s" % resultset._data['totalCount'])
        print("failCount:  %s" % resultset._data['failCount'])
        for result_module in resultset._data['childReports']:
            for suites in result_module['result']['suites']:
                for cases in suites['cases']:
                    if(cases['status'] == "REGRESSION"):
                        print("failure: %s" % cases['className'])


def print_status(jenkins_url, job_name, branch_name):
    builds = get_owned_builds(jenkins_url, job_name, branch_name)
    build = builds[0]
    print_build_status(build)

if __name__ == "__main__":
    run()
