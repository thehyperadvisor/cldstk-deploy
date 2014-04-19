# Setup

Used to install rpm dependancies (nodejs and ansible) 

- **all**  *(ex: python cldstk-deploy.py setup all)*

# Get

Used to download dependancies 

- **all** *(ex: python cldstk-deploy.py get all)*
- **rpmversion=** *(ex: python cldstk-deploy.py get rpmversion=4.3)*
- **systemtemplate=** *(ex: python cldstk-deploy.py get systemtemplate=4.3)*

# Install

Used to run ansible playbook 

- **all** *(ex: python cldstk-deploy.py install all)*
- **all-in-one** *(ex: python cldstk-deploy.py install all-in-one)*
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

