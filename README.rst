=============================================
Jenkins command-line interface
=============================================

**IMPORTANT** works only with python 2.x atm

about
*****
Provide a way to trigger a build and to see the latest restult from the command-line interface. Example :

::

  $ commit-gate -source pierrehenri.toussaint-1.32 -target reaktor-1.32 build 
  Triggering a new build
  status: RUNNING
  url: http://ci:8080/jenkins/job/REAKTOR_commit-gate/2792/


::
  $ commit-gate -source pierrehenri.toussaint-1.32 -target reaktor-1.32 status
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

If pip is not present on your system : 

::

  sudo apt-get install python-pip

usage
*****
::

  jenkins -h
