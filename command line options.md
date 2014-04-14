# Verbs

**Install** - used to run ansible playbook 

**Get** - used to download dependancies 

**Setup** - used to install rpm dependancies (nodejs and ansible) 

# Setup
- **all**  *(ex: python cldstk-deploy.py setup all)*
- **nodejs** *(ex: python cldstk-deploy.py setup nodejs)*
- **ansible** *(ex: python cldstk-deploy.py setup ansible)*

# Get
- **all** *(ex: python cldstk-deploy.py get all)*
- **rpmversion=** *(ex: python cldstk-deploy.py get rpmversion=4.3)*
- **systemtemplate=** *(ex: python cldstk-deploy.py get systemtemplate=4.3)*

# Install
- **all** *(ex: python cldstk-deploy.py install all)*
- **kvm-agent** *(ex: python cldstk-deploy.py install agent)*
- **management** *(ex: python cldstk-deploy.py install management)*
- **db** *(ex: python cldstk-deploy.py install db)*
- **db-replication** *(ex: python cldstk-deploy.py install replication)*
- **systemtemplate** *(ex: python cldstk-deploy.py install systemtemplate)*

## Getting Started

### Setting up the environment

1. Download **cldstk-deploy** from Github.
2. Setup **cldstk-deploy** using the "setup all" option.
3. Download the Apache Cloudstack RPMS and Systemtemplates using the "get rpmversion=" and "get systemtemplate=" options.

### Deploying Apache Cloudstack using cldstk-deploy

1. Change into the "cldstk-deploy" directory.
2. From the "cldstk-deploy" directory run: 

    `python cldstk-deploy.py -s`

3. Open a browser to URL: http://cldstk-deploy-server:3000
4. Click the "Get-Started" link.
5. Fill in the information as needed and click "Submit"
6. This will created the needed files in the cldstk-deploy folder.
7. From the "cldstk-deploy" directory run: 

    `python cldstk-deploy.py -i`

8. Watch the deployment to it's completion.

