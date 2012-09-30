Introduction
====

*lvsm* provides a command shell to manage a [Linux Virtual Server](http://www.linuxvirtualserver.org/) (LVS) 
as a unified system and aims to simplify the management of such systems.
The program assumes a Linux server running IPVS with [iptables](http://www.netfilter.org/projects/iptables) 
rules as firewall.

The program can be run as a shell by simply running ```lvsm``` or invoked as a command by passing all the arguments
in the command line like ```lvsm configure show director```

Software Requirements
====
One or more of the following software is required for correct functionality of *lvsm*:
* iptables
* ipvsadm
* svn
* dsh

Configuration
====

The configuration file can be specified on the command line

    $ lvsm --config=configfile
    
Otherwise the program will look in the current directory for **lvsm.conf**

Valid configuration directives are as follows:
* **director_config**: location of the director configuration file.
* **firewall_config**: location of the iptables configuration file.
* **dsh_group**: the name of the dsh group to use 
All other directives are invalid and cause an error message. Further, lines beginning with # are considered
comments and will not be parsed.

Example
-------
```aconf
# this line is a comment
director_config = /etc/ha.d/ldirectord.cf
firewall_config = /etc/iptables.rules
dsh_group = lb
```


Commands
====

Commands are broken down into different levels, similar to shells like 
[crmsh](http://savannah.nongnu.org/projects/crmsh/), and each new level will present different commands.


Common Commands
-----

Commands below will work at all levels.

**help**: print a relevant help messge depending on the level

**end**: return to the previous

**exit, quit**: exit the lvsm shell

configure level
-----

Enter configuration mode. In this mode, the configuration files can be viewed and synced if under version
control and/or cluster mode.

Configure mode provides access to the director configuration as well as firewall rules. Available commands are
* **show <module>**: will display the configuration for the specified module. Available options are *director* or *fw*

example:

```
lvsm(configure)# show director
```
  
                                                                                                    
* **sync**: sync all configuration files across the cluster by first commiting to a 
[revision control system](http://en.wikipedia.org/wiki/Revision_control). Currently only 
[subversion](http://subversion.tigris.org) is supported.

example:

```
lvsm(configure)# sync
```
* **edit <module>**: *not implemented*

status level
-----
Enter status mode. In this level the status of the live setup can be viewed.

* **show <module>**: show the running status of the given module. Available options are *director*, *firewall*, *virtual*.
The *virtual* module takes additional options *VIP name or address* and *port number*. And will only show that VIP
instead of the entire IPVS table.

examples:

```
lvsm(status)# show firewall
```

```
lvsm(status)# show virtual mysite port 80
```

License
=====
This software is released under the MIT license.
