=============================================
Commit-gate command-line interface
=============================================

**IMPORTANT** works only with python 2.x atm

about
*****
Provide a way to trigger a build and to see the latest result from the command-line interface. Example :

::

  $ commit-gate -v 1.32 build
    Triggering a new build for pierrehenri.toussaint-1.32 ->
    Build #2903 (http://ci:8080/jenkins/job/REAKTOR_commit-gate/2903/) is RUNNING. Test failures : 0. Started 0s ago.
    Build #2903 (http://ci:8080/jenkins/job/REAKTOR_commit-gate/2903/) is RUNNING. Test failures : 0. Started 60s ago.
    Build #2903 (http://ci:8080/jenkins/job/REAKTOR_commit-gate/2903/) is RUNNING. Test failures : 0. Started 120s ago.

::

  $ commit-gate -version 1.32 status
  Status: FAILURE
  Url: http://ci:8080/jenkins/job/REAKTOR_commit-gate/2806/
  Test count:  2912
  Test failures:  121
  Failure: com.bookpac.server.test.catalog.ConvertRetailPriceIT
  Failure: com.bookpac.server.test.catalog.ConvertRetailPriceIT
  Failure: com.bookpac.server.test.content.generic.ContentStatisticIT
  ...

installation
*****
*on most UNIX-like systems, you'll probably need to run the following 
`install` commands as root or by using sudo*

::

  sudo pip install git+http://github.com/txtr/commit-gate-cli

Write the following configuration in ~/.commit-gate-cli.properties :
::

    [main]
    jenkins_url = http://ci:8080/jenkins
    job_name = REAKTOR_commit-gate
    source_base_name = YOUR_USER_NAME
    target_base_name = reaktor
    master_name = dev

If pip is not present on your system : 

::

  sudo apt-get install python-pip

usage
*****
::

  commit-gate -h
