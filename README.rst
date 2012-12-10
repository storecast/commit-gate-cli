=============================================
Jenkins command-line interface
=============================================

**IMPORTANT** works only with python 2.x atm

about
*****
Provide a way to trigger a build and to see the latest restult from the command-line interface. Example :

::

  $ jenkins -source pierrehenri.toussaint-1.32 -target reaktor-1.32 build 
  Triggering a new build
  status: RUNNING
  url: http://ci:8080/jenkins/job/REAKTOR_commit-gate/2792/


::

  $ jenkins -source pierrehenri.toussaint-1.32 status                     
  status: ABORTED
  url: http://ci:8080/jenkins/job/REAKTOR_commit-gate/2791/
  totalCount:  583
  failCount:  0

installation
*****
*on most UNIX-like systems, you'll probably need to run the following 
`install` commands as root or by using sudo*

::

  sudo pip install git+http://github.com/txtr/jenkins-cli

usage
*****
::

  jenkins -h
