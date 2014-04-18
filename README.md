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

## Added SSH Options

You can share ssh-keys to provide ssh login without needing a password. The steps are as follows but cldstk-deploy will ask for a password either way.

### Steps:
    $ ssh-keygen -t rsa -b 2048
    Generating public/private rsa key pair.
    Enter file in which to save the key (/home/username/.ssh/id_rsa): **Enter**
    Enter passphrase (empty for no passphrase): **Enter**
    Enter same passphrase again: **Enter**
    Your identification has been saved in /home/username/.ssh/id_rsa.
    Your public key has been saved in /home/username/.ssh/id_rsa.pub.

Now lets copy your keys to the target server:

    $ ssh-copy-id user@server
    user@server password: 

Check that it works.

    $ ssh user@server


