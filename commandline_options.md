# Getting Started

## Setting up the environment

1. Download **cldstk-deploy** from Github.
2. Setup **cldstk-deploy** using the "setup all" option.

    `python cldstk-deploy.py setup all`

3. Download the Apache Cloudstack RPMS and Systemtemplates using the "get rpmversion=" and "get systemtemplate=" options.

    `python cldstk-deploy.py get rpmversion=4.3`

    `python cldstk-deploy.py get systemtemplate=4.3`

Or you can manually copy the RPMS into the appropriate directory (cldstk-deploy/public/cloudstack.apt-get.eu/rhel/4.3) if you've built your own. 

## Deploying Apache Cloudstack using cldstk-deploy

### Commandline

1. Change into the "cldstk-deploy" directory.
2. From the "cldstk-deploy" directory run: 

    `python cldstk-deploy.py`

3. This will start a wizard with interactive prompts. Answer the questions based on your required installation needs.
4. You can start the installation process at the end.

### Web UI

1. Change into the "cldstk-deploy" directory.
2. From the "cldstk-deploy" directory run: 

    `python cldstk-deploy.py -s`

3. Open a browser to URL: http://cldstk-deploy-server:3000
4. Click the "Get-Started" link.
5. Fill in the information as needed and click "Submit"
6. This will created the needed files in the cldstk-deploy folder.
7. From the "cldstk-deploy" directory run: 

    `python cldstk-deploy.py install all`

8. The deployment process will run and complete all it's tasks.

# Help

## Setup

Used to install rpm dependancies (nodejs and ansible) 

- **all**  *(ex: python cldstk-deploy.py setup all)*

## Get

Used to download dependancies 

- **all** *(ex: python cldstk-deploy.py get all)*
- **rpmversion=** *(ex: python cldstk-deploy.py get rpmversion=4.3)*
- **systemtemplate=** *(ex: python cldstk-deploy.py get systemtemplate=4.3)*

## Install

Used to run ansible playbook 

- **all** *(ex: python cldstk-deploy.py install all)*
- **all-in-one** *(ex: python cldstk-deploy.py install all-in-one)*
- **kvm-agent** *(ex: python cldstk-deploy.py install agent)*
- **management** *(ex: python cldstk-deploy.py install management)*
- **db** *(ex: python cldstk-deploy.py install db)*
- **db-replication** *(ex: python cldstk-deploy.py install replication)*
- **systemtemplate** *(ex: python cldstk-deploy.py install systemtemplate)*

