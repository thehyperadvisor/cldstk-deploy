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
- All-In-One Installation
- Basic Zone Configuration
- Web Server on 8080 for template and iso library
- NTP is now completely synced and configured

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

3. Download the Apache Cloudstack RPMS and Systemtemplates using the "get rpmversion=" and "get systemtemplate=" options. (OPTIONAL) - if you use "Internet" installation type. 

    `python cldstk-deploy.py get rpmversion=4.3`

4. (OPTIONAL) Build RPMS from source. ONLY 4.3 for now. ONLY IF YOU DO NOT DOWNLOAD RPMS.

    `python build-4.3.0-rpms.py`

   Takes roughly 10 minutes to build and installs additional packages.

5. Download KVM system template. Version 4.2 or 4.3 works.

   `python cldstk-deploy.py get systemtemplate=4.3`


## Usage Instructions

RPM packages and system templates must be in downloaded first when NOT using the "Internet" installation type.

Browse the **cldstk-deploy** directory then run the command below. 

    python cldstk-deploy.py

This will start asking questions from the command prompt.

## All-In-One deployment

Next all you have to do is answer the questions. Example shown below.
    
    [root@ansible cldstk-deploy]# python cldstk-deploy.py
    
    Cloudstack Deployment: Answer the questions below....
    
    Install all-in-one?[Y/n]: y
    All-in-one Server[dns/ip]: cldstkkvm01
    Install System Templates?[Y/n]: y
    NFS Server[dns/ip]: 192.168.78.148
    NFS Path[/nfsdirpath]: /mnt/volume1/secondary
    Change install type to "Internet"?[Y/n]: n
    Change install version to "4.2"?[Y/n]: n
    Add ssh rsa keys to ~/.ssh/known_hosts?[Y/n]: y
    ansible hosts file successfully writing to disk.....
    vars_file successfully writing to disk.....
    # cldstkkvm01 SSH-2.0-OpenSSH_5.3

## Customized deployment  

Next all you have to do is answer the questions. Example shown below.
    
    [root@ansible cldstk-deploy]# python cldstk-deploy.py
    
    Cloudstack Deployment: Answer the questions below....
    
    Install all-in-one?[Y/n]: n
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
    Add ssh rsa keys to ~/.ssh/known_hosts?[Y/n]: y
    ansible hosts file successfully writing to disk.....
    vars_file successfully writing to disk.....
    Create Basic Zone?[Y/n]: n
    Start installation now?[Y/n]: y

## Basic Zone option

    Create Basic Zone?[Y/n]: y
    Basic Zone Name: MyZone
    External DNS: 192.168.78.2
    Internal DNS: 192.168.78.2
    Gateway: 192.168.78.2
    NetMask: 255.255.255.0
    Hypervisor type only support KVM at this time.
    Pod Name: MyPod
    Pod Start IP: 192.168.78.200
    Pod End IP: 192.168.78.210
    Guest Start IP: 192.168.78.211
    Guest End IP: 192.168.78.220
    Cluster Name: MyCluster
    Host DNS/IP (separated by comma): cldstkkvm01
    Host User: root
    Host Password: 
    Enter the secondary and primary storage mount points.
    Example: nfs://192.168.78.148/mnt/volume1/secondary
    Secondary Storage: nfs://192.168.78.148/mnt/volume1/secondary
    Primary Storage: nfs://192.168.78.148/mnt/volume1/primary  
    Start installation now?[Y/n]: y
    
After you enter 'y' to start the installation it's off to the races. If everything goes as planned you'll have all your Apache CloudStack components up and running in no time.






