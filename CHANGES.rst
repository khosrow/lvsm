Changes
========

0.3.3 (2013-02-05)
------------------

* Fixed pagination
* Added colour support to ipvsadm and iptables output
* enable/disable commands now ensure the RIP is enabled/disabled
* enable/disable now work across a cluster (if defined)
* General bug fixes

0.3.2 (2013-01-13)
------------------

* Fixed bug when quitting and no files are modified
* Added pagination support for long output
* Added new "status show nat" command
* refactored Director classes to use a factory pattern
* Added stub Keepalived class


0.3.1 (2013-01-09)
------------------

* Added color term support
* Added verification of modified configs
* refactored CommandPrompt and Director classes
* Fixed typos 


0.3.0 (2012-11-06)
------------------

* Added ability to restart firewall and director
* Added ``--version`` flag 
* Fixed bug with unhelpful ipvsadm error message
* Fixed bug in firewall module's ``show()``  


0.2.1 (2012-10-22)
------------------

* Bug fixes in Director class

0.2.0 (2012-10-21)
------------------

* Bug fixes
* Disabling real servers now prompts user for a comment
* ``show virtual`` now displays firewall info for VIP

0.1.1 (2012-10-17)
------------------

* Bug fixes

0.1.0 (2012-10-16)
------------------

* Initial relase 
