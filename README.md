[![Build Status](https://travis-ci.org/linuxdynasty/ld-ansible-modules.svg?branch=master)](https://travis-ci.org/linuxdynasty/ld-ansible-modules)
[![Coverage Status](https://coveralls.io/repos/github/linuxdynasty/ld-ansible-modules/badge.svg?branch=master)](https://coveralls.io/github/linuxdynasty/ld-ansible-modules?branch=master)

# Ansible Version

[![Join the chat at https://gitter.im/linuxdynasty/ld-ansible-modules](https://badges.gitter.im/linuxdynasty/ld-ansible-modules.svg)](https://gitter.im/linuxdynasty/ld-ansible-modules?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
* These modules are tested against the latest Ansible, unless otherwise specified.

# Guidelines
**Any modules that I write and submit to https://github.com/ansible/ansible-modules-extras will also be in this repository.**

## Pull Requests
**All modules must include a test with them in order to be accepted.**

The tests should include the following..

* Integration suite using the Ansible v2 API. The integration suite should cover every possible scenario in which the module you are submitting can be used in.
* Unit tests. Every Method, and function needs to be covered.

## Module Writing Guidelines
**Beyond what is already written here [Developing Modules](http://docs.ansible.com/ansible/developing_modules.html)**

* Do not write everything in main().
* Do not include module as a parameter to every function.
* Write complete documentation for each Function/Method/Class. Read this document for examples.. [Google python style guide](http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html)
