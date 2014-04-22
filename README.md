cldstk-deploy
=============

CloudStack Deploy is a utility for making Apache CloudStack and KVM  installations quick, easy and painless. Meant to be reusable so you can deploy Apache CloudStack more than once after you've downloaded the RPMS and systemtemplates locally with cldstk-deploy.

## Features

- can pre download Apache CloudStack RPMS (version 4.2 & 4.3)
- can pre download KVM system template
- runs web server to be used as local RPM and systemtemplate repository
- can install and setup cloudstack-management servers (One or many)
- can install and setup mysql database servers (Primary and Repica)
- can install and setup cloudstack-agent KVM hosts
- can preseed KVM system template
- can mix options

## Requirements

- CentOS 6.4 or above
- Systems must have internet connectivity
- Host resolution must be working for the systems that runs this process

# Getting Started

## Setting up the environment

1. Download **cldstk-deploy** from Github. 

    `yum install git -y`

    `git clone https://github.com/thehyperadvisor/cldstk-deploy.git`

2. Setup **cldstk-deploy** using the "setup all" option. This prepares the environment and installs all the required packages for **cldstk-deploy** (nodejs and ansible).

    `python cldstk-deploy.py setup all`

3. You can use the "INTERNET" installation type which will use the Apache CloudStack repository. **Note: The Internet install could be really slow and it's recommended to pre download the RPMS and System Templates before doing a full deployment with many systems.**

4. (OPTIONAL) Download the Apache Cloudstack RPMS and Systemtemplates using the "get rpmversion=" and "get systemtemplate=" options. 

    `python cldstk-deploy.py get rpmversion=4.3`

5. (OPTIONAL BUT RECOMMENDED) Build RPMS from source. ONLY 4.3 for now.

    `python build-4.3.0-rpms.py`

Takes roughly 10 minutes to build and installs additional packages.

6. Download KVM system template. Version 4.2 or 4.3 works.

   `python cldstk-deploy.py get systemtemplate=4.3`

RPM packages and system templates must be in downloaded first when NOT using the "Internet" installation type.

## Usage Instructions

Browse the **cldstk-deploy** directory then run the command below. **Note: At this time you must have already sshed into the systems you plan on using this tool with at least once.**

    python start.py

This will start asking questions from the command prompt.

Next all you have to do is answer the questions. Example shown below.
    
    [root@ansible cldstk-deploy]# python cldstk-deploy.py
    
    Cloudstack Deployment: Answer the questions below....
    
    Install Primary Database Server?[Y/n]: y
    Db Server[dns/ip]: cldstkdbsrv01
    Configure Database Replica?[Y/n]: y
    DB Replica Server[dns/ip]: cldstkdbsrv02
    Install Primary Management Server?[Y/n]: y
    Server[dns/ip]: cldstkwebsrv01
    Install additional Management servers?[Y/n]: y             
    Comma separated list: cldstkwebsrv02,cldstkwebsrv03
    Install KVM Hosts?[Y/n]: y
    Comma separated list: cldstkkvm01,cldstkkvm02
    Install System Templates?[Y/n]: y
    NFS Server[dns/ip]: labnas01
    NFS Path[/nfsdirpath]: /nfs/secondary
    Change install type to "Internet"?[Y/n]: n
    Change install version to "4.2"?[Y/n]: n
    ansible hosts file successfully writing to disk.....
    vars_file successfully writing to disk.....
    Start installation now?[Y/n]: y
    SSH password: 
    
After you enter your password it's off to the races. If everything goes as planned you'll have all your Apache CloudStack components up and running in no time.

For "All-In-One" installation, you can use the same system name for "Primary Management Server", "Primary DB Server" and "KVM Host".






