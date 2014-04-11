cldstk-deploy
=============

CloudStack Deploy is a utility for making Apache CloudStack and KVM  installations quick, easy and painless.

## Requirements

- CentOS 6.4 or above
- Systems must have internet connectivity
- Host resolution must be working for the systems that runs this process

## Instructions

#### Command line:

    python start.py
    
This will start asking questions from the command prompt.

Next all you have to do is answer the preseeding questions. Example shown below.

    Install MySQL?[Y/n]: y
    Db Server[dns/ip]: cldstkdbsrv01
    Install MySQL Replica?[Y/n]: y
    Db Replica Server[dns/ip]: cldstkdbsrv02
    Install Management Servers?[Y/n]: y
    Comma separated list: cldstkwebsrv01,cldstkwebsrv02 
    Install KVM Hosts?[Y/n]: y
    Comma separated list: cldstkkvm01,cldstkkvm02
    SSH password:
    
After you enter your password it's off to the races. If everything goes as planned you'll have all your Apache CloudStack components up and running in no time.

#### Web UI:

From the root directory type:

    python start.py -s

This will start the web server so that you can use the web interface.


## Options

- You can choose whether or not to install MySQL. If you choose not to install MySQL, you must provide the current MySQL server name or ip address.
- You can choose whether or not to install MySQL replication partner.
- You can choose whether or not to install Apache CloudStack Management servers.
- You can choose whether or not to install KVM hsots with CloudStack Agent.

