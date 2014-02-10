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


=====================
Further Documentation
=====================

See the project `wiki`_ for detailed documentation on the configuration file and the commands to use. 


=======
License
=======
This software is released under the `MIT license`_.

.. _Linux Virtual Server: http://www.linuxvirtualserver.org/
.. _iptables: http://www.netfilter.org/projects/iptables
.. _MIT license: https://github.com/khosrow/lvsm/blob/master/LICENSE.rst
.. _wiki: https://github.com/khosrow/lvsm/wiki
