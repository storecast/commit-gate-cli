=============================================
Commit-gate command-line interface
=============================================

**IMPORTANT** works only with python 2.x atm

about
*****
Provide a way to trigger a build and to see the latest result from the command-line interface. Example :

::

  $ commit-gate -version 1.32 build
  Triggering a new build for pierrehenri.toussaint-1.32 !
::

  $ commit-gate -version 1.32 status
  status: FAILURE
  url: http://ci:8080/jenkins/job/REAKTOR_commit-gate/2806/
  totalCount:  2912
  failCount:  121
  failure: com.bookpac.server.test.catalog.ConvertRetailPriceIT
  failure: com.bookpac.server.test.catalog.ConvertRetailPriceIT
  failure: com.bookpac.server.test.content.generic.ContentStatisticIT
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

If pip is not present on your system : 

::

  sudo apt-get install python-pip

usage
*****
::

  commit-gate -h
