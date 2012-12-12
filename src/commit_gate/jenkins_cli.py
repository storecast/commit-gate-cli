#!/usr/bin/env python
import os
from time import sleep
from urllib2 import HTTPError
import cli.app
import notify2
from commit_gate.jenkins_api_util import has_build_started
from jenkins_api_util import get_new_status, get_resultset, get_owned_builds, get_job
from ConfigParser import ConfigParser
from os.path import expanduser, exists
import logging

default_master_name = 'dev'
BUILD_CHECK_DELAY = 300
BUILD_PRE_DELAY = 10

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
    parser = ConfigParser({'master_name': default_master_name})
    parser.read(properties_file)
    jenkins_url = parser.get('main', 'jenkins_url')
    job_name = parser.get('main', 'job_name')
    target = target_with_version(parser.get('main', 'target_base_name'), app.params.version,
        parser.get('main', 'master_name'))
    source = source_with_version(parser.get('main', 'source_base_name'), app.params.version)
    job = get_job(jenkins_url, job_name)

    if app.params.action == "build":
        try:
            action_trigger_build(job, source, target)
        except KeyboardInterrupt:
            exit("interrupted")
    elif app.params.action == "status":
        action_print_last_build_status(job, source)
    else:
        exit_with_error("Please specify a correct action [build|status].")

jenkins_cli.add_param("action", help="[build|status]", default=False, type=str)
jenkins_cli.add_param("-v", "--version", help="Specify the version", required=False)

def action_trigger_build(job, source, target):
    original_build_no = job.get_last_buildnumber()

    params_block = False # done manually
    print "Triggering a new build for " + source + "."
    print

    try:
        job.invoke(block=params_block,
            params={'SourceBranch': source,
                    'TargetBranch': target, 'dryrun': 'false',
                    'delay': '0sec'})
    except HTTPError as e:
        exit_with_error(
            "HTTPError while triggering the build. Please verify your parameters (job: %s, source: %s, target: %s). Cause :%s" % (
                job, source, target, e.msg))

    block_until_build_started(job, source, original_build_no)

    build = job.get_last_build()
    print "Build #%s started." % str(build.id())
    count = 0
    while build.is_running():
        total_wait = BUILD_CHECK_DELAY * count
        print "Waited %is for build #%s to complete. Status: %s" % (total_wait, build.id(), get_new_status(build))
        sleep(BUILD_CHECK_DELAY)
        count += 1

    print_build_status(build)
    notify2.Notification("Build #" + str(build.id()), str(get_new_status(build)),
        os.path.join(os.path.dirname(__file__), 'jenkins.png')).show()


def action_print_last_build_status(job, source):
    global builds
    try:
        builds = get_owned_builds(job, source)
    except HTTPError as e:
        exit_with_error(
            "HTTPError while requesting the build. Please verify your parameters (job: %s, source: %s). Cause : %s" % (
                job, source, e.msg))

    print "Last status for %s: " % source
    if len(builds) == 0:
        print "No build found."
        return
    print_build_status(builds[0])


def block_until_build_started(job, source, original_build_no):
    sleep(BUILD_PRE_DELAY)
    total_wait = 0
    while has_build_started(job, original_build_no, source):
        print "Job is already queued. Waited %is for %s to begin..." % (total_wait, job.id())
        sleep(BUILD_PRE_DELAY)
        total_wait += BUILD_PRE_DELAY
        job.poll()


def print_build_status(build):
    print("status: " + get_new_status(build))
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


def target_with_version(source_base_name, version, master_name):
    if version is None:
        return master_name
    else:
        return source_base_name + "-" + version


def exit_with_error(message):
    print "Oops! " + message
    exit(1)


def run():
    jenkins_cli.run()


if __name__ == "__main__":
    run()