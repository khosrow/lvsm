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
Software Requirements
=====================

One or more of the following software is required for correct functionality of *lvsm*:

* `iptables`_
* `ipvsadm`_
* `svn`_
* `git`_
* `dsh`_
* `vi`_
* `pyparsing`_
* `snimpy`_

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
.. _crmsh: http://savannah.nongnu.org/projects/crmsh/
.. _revision control system: http://en.wikipedia.org/wiki/Revision_control
.. _subversion: http://subversion.tigris.org
.. _MIT license: https://github.com/khosrow/lvsm/blob/master/LICENSE.rst
.. _ipvsadm: http://www.linuxvirtualserver.org/software/ipvs.html
.. _svn: http://subversion.tigris.org/
.. _dsh: http://www.netfort.gr.jp/~dancer/software/dsh.html.en
.. _vi: http://en.wikipedia.org/wiki/Vi
.. _git: http://git-scm.com
.. _pyparsing: http://pyparsing.wikispaces.com/
.. _snimpy: https://pypi.python.org/pypi/snimpy/
.. _wiki: https://github.com/khosrow/lvsm/wiki
