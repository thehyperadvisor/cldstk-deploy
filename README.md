cldstk-deploy
=============

cldstk-deploy is a utility for making Apache CloudStack and KVM  installations quick, easy and painless. Meant to be reusable so you can deploy Apache CloudStack more than once after you’ve downloaded the RPMS and system templates locally with cldstk-deploy.

## Features

- can install NFS server ****New****
- cldstk-deploy now creates jobs for each deploy ****New****
- cldstk-deploy now has help using -h
- can pre download Apache CloudStack RPMS (version 4.3, 4.4 & 4.5)
- can pre download KVM system template
- runs web server to be used as ISO, RPM and system template repository
- can install and setup cloudstack-management servers (One or many)
- can install and setup mysql database servers (Primary and Repica)
- can install and setup cloudstack-agent KVM hosts
- can preseed KVM system template
- can mix options
- All-In-One Installation
- Basic Zone Configuration setup after deployment
- configures NTP
- Installs CloudMonkey

## Requirements

- CentOS 6.4 or above (**not compatible with CentOS 7**)
- Mac OS X support ****New**** (tested on 10.10.3 and higher)
- Systems must have internet connectivity (this just make sense)
- Host resolution must be working for the systems that runs this process

# Getting Started

## Setting up the environment

1. Download **cldstk-deploy** from Github. 

    **On CentOS**:
    
    `yum install git -y`

    `git clone https://github.com/thehyperadvisor/cldstk-deploy.git`

    **On Mac OSX**:
    
    Download cldstk-deploy from [here](https://github.com/thehyperadvisor/cldstk-deploy/archive/master.zip)
    
    Double click the download to unpack.
    
2. Setup **cldstk-deploy** using the “setup all” option. This prepares the environment and installs all the required packages for **cldstk-deploy** (python and ansible).

    `cd cldstk-deploy`

    `python cldstkdeploy.py —-setup all`

3. Download the Apache Cloudstack RPMS and Systemtemplates all at once. (OPTIONAL) - if you use “Internet” installation type. 

    `python cldstkdeploy.py —-getall 4.5`

4. (OPTIONAL) Build RPMS from source. ONLY 4.3, 4.4 & 4.5 for now. ONLY IF YOU DO NOT DOWNLOAD RPMS.

    `python build-4.5.x-rpms.py`

   Takes roughly 10 minutes to build and installs additional packages.

## Usage Instructions

RPM packages and system templates must be in downloaded first when NOT using the “Internet” installation type.

Browse the **cldstk-deploy** directory then run the command below. 

    python cldstkdeploy.py

This will start asking questions from the command prompt.

## All-In-One deployment

Next all you have to do is answer the questions. Example shown below.
    
    [root@centos cldstk-deploy]# python cldstkdeploy.py
    
    Cloudstack Deployment: Answer the questions below….
    
    Install all-in-one?[Y/n]: y
    All-in-one Server[dns/ip]: 192.168.0.29
    Install System Templates?[Y/n]: y
    Change install type to “Internet”?[Y/n]: n
    Which version to install [‘4.3’, ‘4.4’, ‘4.5’]?: 4.5
    Add ssh rsa keys to ~/.ssh/known_hosts?[Y/n]: y
    jobid: 2015-07-06-22-17-45165765
    ansible hosts file successfully writing to disk…..
    vars_file successfully writing to disk…..
    # 192.168.0.29 SSH-2.0-OpenSSH_5.3
    Create Basic Zone?[Y/n]: n
    No Basic Zone will be created
    Start installation now?[Y/n]: y

## Customized deployment  

Next all you have to do is answer the questions. Example shown below.
    
    [root@centos cldstk-deploy]# python cldstkdeploy.py
    
    Cloudstack Deployment: Answer the questions below….
    
    Install all-in-one?[Y/n]: n
    Install Primary Database Server?[Y/n]: y
    Db Server[dns/ip]: 192.168.0.20
    Configure Database Replica?[Y/n]: n
    Install Primary Management Server?[Y/n]: y
    Server[dns/ip]: 192.168.0.30
    Install additional Management servers?[Y/n]: n
    Install KVM Hosts?[Y/n]: y
    Comma separated list: 192.168.0.40,192.168.0.41
    Install System Templates?[Y/n]: y
    NFS Server[dns/ip]: 192.168.0.50
    NFS Secondary Storage Path[/nfsdirpath]: /secondary
    Change install type to “Internet”?[Y/n]: n
    Which version to install [‘4.3’, ‘4.4’, ‘4.5’]?: 4.5
    Add ssh rsa keys to ~/.ssh/known_hosts?[Y/n]: y
    jobid: 2015-07-06-22-28-34672160
    ansible hosts file successfully writing to disk…..
    vars_file successfully writing to disk…..
    # 192.168.0.20 SSH-2.0-OpenSSH_5.3
    # 192.168.0.30 SSH-2.0-OpenSSH_5.3
    # 192.168.0.40 SSH-2.0-OpenSSH_5.3
    # 192.168.0.41 SSH-2.0-OpenSSH_5.3
    # 192.168.0.50 SSH-2.0-OpenSSH_5.3
    Create Basic Zone?[Y/n]: n
    No Basic Zone will be created
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
    
After you enter ‘y’ to start the installation it’s off to the races. If everything goes as planned you’ll have all your Apache CloudStack components up and running in no time.
