************
LVS Manger - a shell to manage LVS and iptables
************
.. image:: https://secure.travis-ci.org/khosrow/lvsm.png
   :target: https://travis-ci.org/#!/khosrow/lvsm

*lvsm* provides a command shell to manage a `Linux Virtual Server`_ (LVS) 
as a unified system and aims to simplify the management of such systems.
The program assumes a Linux server running IPVS with `iptables`_
rules as firewall.

The program can be run as a shell by simply running ``lvsm`` or invoked as a command by passing all the arguments
in the command line like ``lvsm configure show director``

**Table of Contents**

.. contents::
    :local:
    :depth: 2
    :backlinks: none

=====================
Software Requirements
=====================

One or more of the following software is required for correct functionality of *lvsm*:

* `iptables`_
* `ipvsadm`_
* `svn`_
* `dsh`_
* `vi`_

=============
Configuration
=============

The configuration file can be specified on the command line

.. code-block::

    $ lvsm --config=configfile
    
Otherwise the program will look in the current directory for **lvsm.conf**

Valid configuration directives are as follows:

* **director_config**: location of the director configuration file
* **director_cmd**: command to restart the director
* **firewall_config**: location of the iptables configuration file
* **firewall_cmd**: command restart the iptables firewall
* **dsh_group**: the name of the dsh group to use 
* **director**: the type of director used for *ipvs*. Only ``ldirectord`` is supported at the moment
* **maintenance_dir**: directory used by *ldirectord* for disabling servers
* **ipvsadm**: location of the *ipvsadm* binary. Defaults to ``ipvsadm``
* **iptables**: location of the *iptables* binary. Defaults to ``iptables``


All other directives are invalid and cause an error message. Further, lines beginning with ``#`` are considered
comments and will not be parsed.

example:

.. code-block:: conf

    # this line is a comment
    director_config = /etc/ha.d/ldirectord.cf
    firewall_config = /etc/iptables.rules
    dsh_group = lb

========
Commands
========

Commands are broken down into different levels, similar to shells like 
`crmsh`_, and each new level will present different commands.

---------------
common commands
---------------

Commands below will work at all levels.

**set**: change or show display settings inside lvsm. 

**help**: print a relevant help messge depending on the level

**end**: return to the previous

**exit, quit**: exit the lvsm shell

---------------
main level
---------------

Available commands are

* **restart**: restart a given module. For this command to work the configuration items ``director_cmd`` and/or ``firewall_cmd`` need to be set up in the ``lvsm.conf`` file.

Usage:

::

    restart <module>

Where ``<module>`` is one of:

+------------------------------------+-------------------------------------+
| Option                             | Result                              |
+====================================+=====================================+
|``director``                        | restart the lvs director            |
+------------------------------------+-------------------------------------+
|``firewall``                        | restart the iptables firewall       |
+------------------------------------+-------------------------------------+


---------------
configure level
---------------

Enter configuration mode. In this mode, the configuration files can be viewed and synced if under version
control and/or cluster mode. Configure mode provides access to the director configuration as well as firewall rules. 

Available commands are

* **show**: will display the configuration for the specified module. 

Usage: 

::

    show <module>
    
    
Where ``<module>`` is one of:

+------------------------------------+-------------------------------------+
| Option                             | Result                              |
+====================================+=====================================+
|``director``                        | show the director configuration     |
+------------------------------------+-------------------------------------+
|``firewall``                        | show the iptables configuration     |
+------------------------------------+-------------------------------------+

example:

.. code-block::

    lvsm(configure)# show director


* **edit**: open the configuration file for the module using an editor. *note:* the editor is currently set to **vi**.

Usage:

::
    
    show <module>

Where ``<module>`` is one of:

+------------------------------------+-------------------------------------+
| Option                             | Result                              |
+====================================+=====================================+
|``director``                        | edit the director configuration     |
+------------------------------------+-------------------------------------+
|``firewall``                        | edit the iptables configuration     |
+------------------------------------+-------------------------------------+


example:

.. code-block::

    lvsm(configure)# edit director
                                                                                                    
* **sync**: sync all configuration files across the cluster by first commiting to a `revision control system`_. Currently only `subversion`_ is supported.

example:

.. code-block::

    lvsm(configure)# sync


------------
status level
------------

Enter status mode. In this level the status of the live setup can be viewed.

* **show**: show the running status of the given module. 

Usage:

::

    show <module>
    
``<module>`` can be one of the following

+------------------------------------+-------------------------------------+
| Option                             | Result                              |
+====================================+=====================================+
|``director``                        | show the running ipvs status        |
+------------------------------------+-------------------------------------+
|``firewall``                        | show the iptables status            |
+------------------------------------+-------------------------------------+
|``nat``                             | show the iptables NAT tables        |
+------------------------------------+-------------------------------------+
|``real <server> <port>``            | show the status of a real server    |
+------------------------------------+-------------------------------------+
|``virtual tcp|udp|fwm <vip> <port>``| show the status of virtual server   |
+------------------------------------+-------------------------------------+

examples:

::

    lvsm(status)# show firewall

::

    lvsm(status)# show virtual mysite http

::
    
    lvs(status)# show real fe-01 http

* **enable**: enable a real server. 
This option is dependent on the director type. Currently only **ldirectord** is supported.

Usage:

::

    enable real <server> <port>

* **disable**: disable a real server in *ipvs*. 
This option is dependent on the director type. Currently only **ldirectord** is supported.

Usage:

::

    disable real <server> <port>

=======
License
=======
This software is released under the `MIT license`_.

.. _Linux Virtual Server: http://www.linuxvirtualserver.org/
.. _iptables: http://www.netfilter.org/projects/iptables
.. _crmsh: http://savannah.nongnu.org/projects/crmsh/
.. _revision control system: http://en.wikipedia.org/wiki/Revision_control
.. _subversion: http://subversion.tigris.org
.. _MIT license: https://github.com/khosrow/lvsm/blob/master/LICENSE.rst
.. _ipvsadm: http://www.linuxvirtualserver.org/software/ipvs.html
.. _svn: http://subversion.tigris.org/
.. _dsh: http://www.netfort.gr.jp/~dancer/software/dsh.html.en
.. _vi: http://en.wikipedia.org/wiki/Vi

