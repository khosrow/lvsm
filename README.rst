************
LVSM
************

*lvsm* provides a command shell to manage a `Linux Virtual Server`_ (LVS) 
as a unified system and aims to simplify the management of such systems.
The program assumes a Linux server running IPVS with `iptables`_
rules as firewall.

The program can be run as a shell by simply running ``lvsm`` or invoked as a command by passing all the arguments
in the command line like ``lvsm configure show director``

**Table of Contents**

.. contents::
    :local:
    :depth: 1
    :backlinks: none

=====================
Software Requirements
=====================

One or more of the following software is required for correct functionality of *lvsm*:

* iptables
* ipvsadm
* svn
* dsh
* vi

=============
Configuration
=============

The configuration file can be specified on the command line

.. code-block:: bash

    $ lvsm --config=configfile
    
Otherwise the program will look in the current directory for **lvsm.conf**

Valid configuration directives are as follows:

* **director_config**: location of the director configuration file.
* **firewall_config**: location of the iptables configuration file.
* **dsh_group**: the name of the dsh group to use 

All other directives are invalid and cause an error message. Further, lines beginning with ``#`` are considered
comments and will not be parsed.

-------
Example
-------

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
Common Commands
---------------

Commands below will work at all levels.

**help**: print a relevant help messge depending on the level

**end**: return to the previous

**exit, quit**: exit the lvsm shell

---------------
configure level
---------------

Enter configuration mode. In this mode, the configuration files can be viewed and synced if under version
control and/or cluster mode. Configure mode provides access to the director configuration as well as firewall rules. 

Available commands are

* **show <module>**: will display the configuration for the specified module. 

Usage: 

::

    show <module>
    
    
Where ``<module>`` is one of **director** or **firewall**

example:

.. code-block::

    lvsm(configure)# show director
  
                                                                                                    
* **sync**: sync all configuration files across the cluster by first commiting to a `revision control system`_. Currently only `subversion`_ is supported.

example:

.. code-block::

    lvsm(configure)# sync

* **edit <module>**: open the configuration file for the module using an editor. *note:* the editor is currently set to **vi**.

example:

.. code-block::

    lvsm(configure)# edit director

------------
status level
------------

Enter status mode. In this level the status of the live setup can be viewed.

* **show <module>**: show the running status of the given module. 

Usage:

::

    show <module>

Where ``<module>`` is one of **director**, **firewall**, **virtual**.

The ``virtual`` module takes additional options: **protocol**, **vip name or address** and **port number**
and will only show that VIP instead of the entire IPVS table.

Usage:

::

    show virtual fwm|tcp|udp <vip> <port>

examples:

::

    lvsm(status)# show firewall

::

    lvsm(status)# show virtual mysite port 80


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

