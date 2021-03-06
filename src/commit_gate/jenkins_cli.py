#!/usr/bin/env python
import os
from time import sleep
from urllib2 import HTTPError
import cli.app
try:
    import notify2 # Not working on mac
    notify2_available = True
except ImportError:
    notify2_available = False
from commit_gate.jenkins_api_util import has_build_started, get_url, get_test_cases, get_total_count, get_fail_count
from jenkins_api_util import get_new_status, get_owned_builds, get_job
from ConfigParser import ConfigParser
from os.path import expanduser, exists
import logging

default_master_name = 'dev'
JENKINS_LAG_DELAY = 3
BUILD_CHECK_DELAY = 60
BUILD_PRE_DELAY = 30

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logging.getLogger().addHandler(ch)

@cli.app.CommandLineApp(name="commit-gate")
def jenkins_cli(app):
    home = expanduser("~")
    properties_file = home + '/.commit-gate-cli.properties'
    if(not exists(properties_file)):
        exit_with_error("Cannot find the config file in " + properties_file)
    parser = ConfigParser({'master_name': default_master_name})
    parser.read(properties_file)
    jenkins_url = parser.get('main', 'jenkins_url')
    job_name = parser.get('main', 'job_name')
    target = app.params.target if app.params.target is not None else target_with_version(parser.get('main', 'target_base_name'), app.params.version,
        parser.get('main', 'master_name'))
    source = app.params.source if app.params.source is not None else source_with_version(parser.get('main', 'source_base_name'), app.params.version)
    job = get_job(jenkins_url, job_name)

    if app.params.action == "build":
        try:
            action_trigger_build(job, source, target,app.params.dryrun)
        except KeyboardInterrupt:
            exit("interrupted")
    elif app.params.action == "status":
        action_print_last_build_status(job, source)
    else:
        exit_with_error("Please specify a correct action [build|status].")

jenkins_cli.add_param("action", help="[build|status]", default=False, type=str)
jenkins_cli.add_param("-v", "--version", help="Specify the version", required=False)
jenkins_cli.add_param("-d", "--dryrun", help="Dry run", default=False, action="store_true")
jenkins_cli.add_param("-s", "--source", help="Specify the source branch", required=False)
jenkins_cli.add_param("-t", "--target", help="Specify the target branch", required=False)

def action_trigger_build(job, source, target, dryrun):
    original_build_no = job.get_last_buildnumber()

    params_block = False # done manually
    print "Triggering a new build for " + source + " -> " + target + " :"
    try:
        job.invoke(block=params_block,
            build_params={'SourceBranch': source,
                    'TargetBranch': target, 
                    'dryrun': str(dryrun).lower(),
                    'delay': '0sec'})
    except HTTPError as e:
        exit_with_error(
            "HTTPError while triggering the build. Please verify your parameters (job: %s, source: %s, target: %s). Cause :%s" % (
                job, source, target, e.msg))

    block_until_build_started(job, source, original_build_no)

    build = job.get_last_build()
    count = 0
    fail_notified = False
    while build.is_running():
        status = get_new_status(build)
        total_wait = BUILD_CHECK_DELAY * count
        fail_count = get_fail_count(build)
        if fail_count > 0 and not fail_notified:
            notify("Build #" + str(build.get_number()), str("Test failures : %s" % fail_count))
            fail_notified = True
        print "Build #%s (%s) is %s. Test failures : %s. Started %im ago." % (
            build.get_number(), get_url(build), status, fail_count, total_wait / 60)
        sleep(BUILD_CHECK_DELAY)
        count += 1
        pass

    sleep(JENKINS_LAG_DELAY)
    print_build_status(build)
    notify("Build #" + str(build.get_number()), str(get_new_status(build)))


def action_print_last_build_status(job, source):
    global builds
    try:
        builds = get_owned_builds(job, source)
    except HTTPError as e:
        exit_with_error(
            "HTTPError while requesting the build. Please verify your parameters (job: %s, source: %s). Cause : %s" % (
                job, source, e.msg))

    print "Last status for %s ->" % source
    if len(builds) == 0:
        print "No build found."
        return
    print_build_status(builds[0])


def block_until_build_started(job, source, original_build_no):
    total_wait = 0
    while has_build_started(job, original_build_no, source):
        print "Job is already queued. Waited %is for %s to begin..." % (total_wait, job.get_last_buildnumber())
        sleep(BUILD_PRE_DELAY)
        total_wait += BUILD_PRE_DELAY
        job.poll()


def print_build_status(build):
    print(" Status: %s" % get_new_status(build))
    print(" Url: %s " % get_url(build))
    if(build.has_resultset()):
        print(" Test count:  %s" % get_total_count(build))
        print(" Test failures:  %s" % get_fail_count(build))
        for case in get_test_cases(build):
            if(case['status'] == "REGRESSION"):
                print(" Failure: %s" % case['className'])


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


def notify(summary, message):
    if not notify2_available:
        return
    try:
        notify2.init('commit-gate-cli')
        notify2.Notification(summary, message, os.path.join(os.path.dirname(__file__), 'jenkins.png')).show()
    except BaseException as e:
        print "Could not display notification %s" % e.message


def exit_with_error(message):
    print "Oops! " + message
    exit(1)


def run():
    jenkins_cli.run()


if __name__ == "__main__":
    run()
