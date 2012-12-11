#!/usr/bin/env python
import cli.app
from jenkinsapi.api import get_latest_build
from jenkins_api_util import get_status, get_resultset, get_owned_builds, get_job
from ConfigParser import ConfigParser
from os.path import expanduser, exists

import logging

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logging.getLogger().addHandler(ch)

@cli.app.CommandLineApp(name="commit-gate")
def jenkins_cli(app):
    home = expanduser("~")
    properties_file = home + '/.commit-gate-cli.properties'
    if(not exists(properties_file)):
        exit_with_error("Cannot find the config file in " + properties_file)

    parser = ConfigParser()
    parser.read(properties_file)
    jenkins_url = parser.get('main', 'jenkins_url')
    job_name = parser.get('main', 'job_name')
    target = with_version(parser.get('main', 'target_base_name'), app.params.version)
    source = with_version(parser.get('main', 'source_base_name'), app.params.version)
    if app.params.action == "build":
        print "Triggering a new build for " + source + " !"
        get_job(jenkins_url, job_name).invoke(
            params={'SourceBranch': source,
                    'TargetBranch': target, 'dryrun': 'false',
                    'delay': '0sec'})
        return
    elif app.params.action == "status":
        print "Last status for " + source + ":"
        builds = get_owned_builds(jenkins_url, job_name, source)
        if len(builds) == 0:
            print "No build found."
            return
        build = builds[0]
        print_build_status(build)
    else:
        exit_with_error("Please specify a correct action [build|status].")

jenkins_cli.add_param("action", help="[build|status]", default=False, type=str)
jenkins_cli.add_param("-version", help="Specify the version", required=False)

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


def with_version(source_base_name, version):
    if version is None:
        return source_base_name
    else:
        return source_base_name + "-" + version


def exit_with_error(message):
    print "Oops! " + message
    exit(1)


def run():
    jenkins_cli.run()


if __name__ == "__main__":
    run()
















