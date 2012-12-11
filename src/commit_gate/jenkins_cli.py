#!/usr/bin/env python
import os
from time import sleep
import cli.app
import notify2
from jenkins_api_util import get_status, get_resultset, get_owned_builds, get_job
from ConfigParser import ConfigParser
from os.path import expanduser, exists
#from gi.repository import Notify

import logging

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logging.getLogger().addHandler(ch)


@cli.app.CommandLineApp(name="commit-gate")
def jenkins_cli(app):
    home = expanduser("~")
    properties_file = home + '/.commit-gate-cli.properties'
    notify2.init('commit-gate-cli')
    if(not exists(properties_file)):
        exit_with_error("Cannot find the config file in " + properties_file)
    parser = ConfigParser()
    parser.read(properties_file)
    jenkins_url = parser.get('main', 'jenkins_url')
    job_name = parser.get('main', 'job_name')
    target = target_with_version(parser.get('main', 'target_base_name'), app.params.version)
    source = source_with_version(parser.get('main', 'source_base_name'), app.params.version)
    if app.params.action == "build":
        try:
            trigger_build(app, jenkins_url, job_name, source, target)
        except KeyboardInterrupt:
            exit("interrupted")
    elif app.params.action == "status":
        print_last_build_status(jenkins_url, job_name, source)
    else:
        exit_with_error("Please specify a correct action [build|status].")

jenkins_cli.add_param("action", help="[build|status]", default=False, type=str)
jenkins_cli.add_param("-v", "--version", help="Specify the version", required=False)

def trigger_build(app, jenkins_url, job_name, source, target):
    job = get_job(jenkins_url, job_name)
    total_wait = 0
    while job.is_queued():
        print "Job is already queued. Waited %is for %s to begin..." % ( total_wait, job.id() )
        sleep(15)
        total_wait += 15
        notify2.Notification("Build starting !", "(job was queued)",
            os.path.join(os.path.dirname(__file__), 'jenkins.png')).show()
        print "Build starting (job as queued) !"

    print "Triggering a new build for " + source + " !"
    params_block = True
    job.invoke(block=params_block,
        params={'SourceBranch': source,
                'TargetBranch': target, 'dryrun': 'false',
                'delay': '0sec'})
    builds = get_owned_builds(jenkins_url, job_name, source)
    #    sleep(3) consider sleep when not blocking
    assert len(builds) != 0, "Build not started"
    print_build_status(builds[0])
    notify2.Notification("Build #" + str(builds[0].id()), get_status(builds[0]),
        os.path.join(os.path.dirname(__file__), 'jenkins.png')).show()


def print_last_build_status(jenkins_url, job_name, source):
    print "Last status for " + source + ":"
    builds = get_owned_builds(jenkins_url, job_name, source)
    if len(builds) == 0:
        print "No build found."
        return
    print_build_status(builds[0])


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


def source_with_version(source_base_name, version):
    if version is None:
        return source_base_name
    else:
        return source_base_name + "-" + version


def target_with_version(source_base_name, version):
    if version is None:
        return "dev"
    else:
        return source_base_name + "-" + version


def exit_with_error(message):
    print "Oops! " + message
    exit(1)


def run():
    jenkins_cli.run()


if __name__ == "__main__":
    run()
















