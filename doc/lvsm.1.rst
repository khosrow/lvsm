====
lvsm
====

----------------------------
Linux Virtual Server Manager
----------------------------

:Author: Khosrow E.
:Manual section: 1
:Date: February 10, 2014
:Version: 0.5.0

Synopsis
========

**lvsm** [-h] [-c <conffile>][commands]

Description
===========

Lvsm provides a command shell to manage a Linux Virtual Server (LVS) as a unified system and aims to simplify the management of such systems. The program assumes a Linux server running IPVS with iptables rules as firewall.

This program can be run as a shell by simply running lvsm or invoked as a command by passing all the arguments in the command line like: 'lvsm configure show director'

Use 'lvsm help <command>' for information on a specific command.

Options
=======

  -h, --help            Show this help message and exit.
  -d, --debug           Enable debug messages during runtime
  -c conffile, --config=conffile
                        Specify which configuration file to use. The default is **/etc/lvsm.conf**
  -m, --monochrome      Disable color display
  -n, --numeric         Enable numeric host names, and avoid using DNS
  -v, --version         Display lvsm version

License
=======

This software is released under the MIT license.
