from distutils.core import setup
import os
from setuptools import  find_packages

description = 'A simple command-line for Jenkins'
cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README.rst')).read()
except:
    long_description = description

setup(
    name='commit-gate-cli',
    version='0.0.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/txtr/commit-gate-cli',
    license='',
    author='pache',
    author_email='pierrehenri.toussaint@txtr.com',
    description=description,
    long_description=long_description,
    entry_points="""
    [console_scripts]
    commit-gate = commit_gate.jenkins_cli:run
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Bug Tracking',
    ],
    install_requires=['jenkinsapi', 'pyCLI']
)
