#!/usr/bin/python
import platform
import hashlib
import hmac
import base64
from subprocess import call, Popen, PIPE
import sys
import os
import commands
import urllib
import json
import getpass
import time
import httplib
from urlparse import urlparse
import random
import datetime
from optparse import OptionParser


# Supported versions on apache cloudstack
__versionsupport__ = ['4.3', '4.4', '4.5']
__version__ = "1.2.0"
__description__ = "CloudStack Deploy is a utility for making Apache CloudStack " \
                  "and KVM installations quick, easy and painless."
__maintainer__ = "Antone Heyward"
__maintaineremail__ = "thehyperadvisor@gmail.com"
__project__ = "cldstk-deploy"
__projecturl__ = "https://github.com/thehyperadvisor/cldstk-deploy"
__repolocalpath__ = '/public/rpms/rhel/'
__systmpllocalpath__ = '/public/templates/'

configs = {
    'local': {
        '4.5': {'download': 'https://dl.dropboxusercontent.com/u/3904598/cloudstack-4.5.1-rpms.tar.gz', 'rpms': '',
                'systmplfile': 'systemvm64template-4.5-kvm.qcow2.bz2'},
        '4.4': {'download': 'https://dl.dropboxusercontent.com/u/3904598/cloudstack-4.4.2-rpms.tar.gz', 'rpms': '',
                'systmplfile': 'systemvm64template-4.4.0-6-kvm.qcow2.bz2'},
        '4.3': {'download': 'https://www.dropbox.com/sh/7fa1j6ymap1wrgu/BXfoDzUNWy/cloudstack-4.3.0-rpms.tar.gz',
                'rpms': '', 'systmplfile': 'systemvm64template-2014-01-14-master-kvm.qcow2.bz2'}
    },
    'internet': {
        '4.5': {'download': '', 'rpms': '',
                'systmplurl': 'http://packages.shapeblue.com/systemvmtemplate/4.5/systemvm64template-4.5-kvm.qcow2.bz2'},
        '4.4': {'download': '', 'rpms': '',
                'systmplurl': 'http://cloudstack.apt-get.eu/systemvm/4.4/systemvm64template-4.4.0-6-kvm.qcow2.bz2'},
        '4.3': {'download': '', 'rpms': '',
                'systmplurl': 'http://download.cloud.com/templates/4.3/systemvm64template-2014-01-14-master-kvm.qcow2.bz2'}
    }
}
# Set user passwords for mysql users
cloud_repl_password = 'password'
mysql_root_password = 'PaSSw0rd1234'

# Set variables for current working directory
savedHome = os.getcwd()
userHome = os.path.expanduser('~')


class SignedAPICall(object):
    def __init__(self, api_url, apiKey, secret):
        self.api_url = api_url
        self.apiKey = apiKey
        self.secret = secret

    def request(self, args):
        args['apiKey'] = self.apiKey

        self.params = []
        self._sort_request(args)
        self._create_signature()
        self._build_post_request()

    def _sort_request(self, args):
        keys = sorted(args.keys())

        for key in keys:
            self.params.append(key + '=' + urllib.quote_plus(args[key]))

    def _create_signature(self):
        self.query = '&'.join(self.params)
        digest = hmac.new(
            self.secret,
            msg=self.query.lower(),
            digestmod=hashlib.sha1).digest()

        self.signature = base64.b64encode(digest)

    def _build_post_request(self):
        self.query += '&signature=' + urllib.quote_plus(self.signature)
        self.value = self.api_url + '?' + self.query


class CloudStack(SignedAPICall):
    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            if kwargs:
                return self._make_request(name, kwargs)
            return self._make_request(name, args[0])

        return handlerFunction

    def _http_get(self, url):
        response = urllib.urlopen(url)
        return response.read()

    def _make_request(self, command, args):
        args['response'] = 'json'
        args['command'] = command
        self.request(args)
        data = self._http_get(self.value)
        # The response is of the format {commandresponse: actual-data}
        key = command.lower() + "response"
        return json.loads(data)[key]


class CldStkDeploy(object):
    def __init__(self):
        if not os.path.exists(savedHome + '/public/templates'):
            os.makedirs(savedHome + '/public/templates')
        if not os.path.exists(savedHome + '/public/templates/other'):
            os.makedirs(savedHome + '/public/templates/other')
        if not os.path.exists(savedHome + '/public/templates/iso'):
            os.makedirs(savedHome + '/public/templates/iso')
        if not os.path.exists(savedHome + '/public/rpms'):
            os.makedirs(savedHome + '/public/rpms')
        if not os.path.exists(savedHome + '/public/rpms/rhel'):
            os.makedirs(savedHome + '/public/rpms/rhel')
        if not os.path.exists(userHome + '/.ssh'):
            os.makedirs(userHome + '/.ssh')
        try:
            if not os.path.exists(userHome + '/.ssh/known_hosts'):
                open(userHome + '/.ssh/known_hosts', 'w').close()
        except:
            pass

    def getpasswd(self):
        self.passwd = getpass.getpass("Enter Password Here: ")

    # Runs ansible playbooks
    def go_playbook(self, playfile, jobid):
        try:
            # Set ansible api variables
            from ansible.playbook import PlayBook
            from ansible import callbacks
            from ansible import utils
            self.playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
            self.stats = callbacks.AggregateStats()
            self.runner_cb = callbacks.PlaybookRunnerCallbacks(self.stats, verbose=utils.VERBOSITY)
        except Exception, e:
            print(str(e))
            print('You need to run [python cldstkdeploy.py --setup all].')
            sys.exit()
            pass

        vfile = open('ansible/jobs/{0}/vars_file.yml'.format(jobid))
        hfile = 'ansible/jobs/{0}/hosts'.format(jobid)
        # extravars = [v.strip() for v in vfile]
        # extravars = str(extravars).strip('[]').replace("'", "").replace(",", "").replace('= ', '=None ')
        #
        # start_now = Popen(['ansible-playbook', playfile, '-i', hfile,
        #                    '-e', ext, '-k'], stderr=PIPE)
        #
        # errdata = start_now.communicate()[1]
        # if len(errdata) != 0:
        #     print errdata.strip("\n")
        ext = {}
        for v in vfile:
            if v.split('=')[1].strip() == '':
                ext[v.split('=')[0]]='None'
            else:
                ext[v.split('=')[0]]=v.split('=')[1].strip()

        playbook = PlayBook(remote_user='root',
                            remote_pass=self.passwd,
                            playbook=playfile,
                            callbacks=self.playbook_cb,
                            runner_callbacks=self.runner_cb,
                            stats=self.stats,
                            extra_vars=ext,
                            host_list=hfile
                            )

        playoutput = playbook.run()
        for l in playoutput:
            print l, playoutput[l]

    def createZone(self, api_srv, jobdir):
        readconfig = open(userHome + '/.cloudmonkey/config').readlines()
        api_url = ''
        secret = ''
        apiKey = ''

        for k in readconfig:
            a = k.find('apikey')
            if a == 0:
                apiKey = k.split('=')[1].strip()
        for k in readconfig:
            a = k.find('secretkey')
            if a == 0:
                secret = k.split('=')[1].strip()
        for k in readconfig:
            a = k.find('url')
            if a == 0:
                api_url = k.split('=')[1].strip()
                print('appurl: ' + api_url)

        api = CloudStack(api_url, apiKey, secret)

        zone_file = open(jobdir + '/zone_conf').readlines()
        for k in zone_file:
            a = k.find('zname')
            if a == 0:
                zname = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('podname')
            if a == 0:
                podname = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('clus_name')
            if a == 0:
                clus_name = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('dns_ext')
            if a == 0:
                dns_ext = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('dns_int')
            if a == 0:
                dns_int = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('gw')
            if a == 0:
                gw = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('nmask')
            if a == 0:
                nmask = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('hpvr')
            if a == 0:
                hpvr = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('pod_start')
            if a == 0:
                pod_start = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('pod_end')
            if a == 0:
                pod_end = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('vlan_start')
            if a == 0:
                vlan_start = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('vlan_end')
            if a == 0:
                vlan_end = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('host_ips')
            if a == 0:
                host_ips = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('host_user')
            if a == 0:
                host_user = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('host_passwd')
            if a == 0:
                host_passwd = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('sec_storage')
            if a == 0:
                sec_storage = k.split('=')[1].strip()
        for k in zone_file:
            a = k.find('prm_storage')
            if a == 0:
                prm_storage = k.split('=')[1].strip()
        try:
            zonetask = {'dns1': dns_ext, 'internaldns1': dns_int, 'name': zname, 'networktype': 'Basic'}
            result = api.createZone(zonetask)
            # print "id", result
            zone_id = result['zone']['id']
            print('Created Zone ' + zname + ' with id: ' + zone_id)

            phynettask = {'name': 'phy-network', 'zoneid': zone_id}
            result = api.createPhysicalNetwork(phynettask)
            # print result
            phynet_id = result['id']
            print('Created physical network.')

            addtraffictypetask = {'physicalnetworkid': phynet_id, 'traffictype': 'Guest'}
            result = api.addTrafficType(addtraffictypetask)
            # print result

            addtraffictypetask = {'physicalnetworkid': phynet_id, 'traffictype': 'Management'}
            result = api.addTrafficType(addtraffictypetask)
            # print result

            updatephynettask = {'id': phynet_id, 'state': 'Enabled'}
            result = api.updatePhysicalNetwork(updatephynettask)
            # print result

            listnsptask = {'physicalnetworkid': phynet_id, 'name': 'VirtualRouter'}
            result = api.listNetworkServiceProviders(listnsptask)
            # print result
            nsp_id = result['networkserviceprovider'][0]['id']

            listvrtask = {'nspid': nsp_id}
            result = api.listVirtualRouterElements(listvrtask)
            # print result
            vre_id = result['virtualrouterelement'][0]['id']

            configvrtask = {'id': vre_id, 'enabled': 'true'}
            result = api.configureVirtualRouterElement(configvrtask)
            # print result

            updatensptask = {'id': nsp_id, 'state': 'Enabled'}
            result = api.updateNetworkServiceProvider(updatensptask)
            # print result

            listnsptask = {'physicalnetworkid': phynet_id, 'name': 'SecurityGroupProvider'}
            result = api.listNetworkServiceProviders(listnsptask)
            # print result
            nsp_sg_id = result['networkserviceprovider'][0]['id']

            updatensptask = {'id': nsp_sg_id, 'state': 'Enabled'}
            result = api.updateNetworkServiceProvider(updatensptask)
            # print result

            listnetofftask = {'name': 'DefaultSharedNetworkOfferingWithSGService'}
            result = api.listNetworkOfferings(listnetofftask)
            # print result
            netoff_id = result['networkoffering'][0]['id']

            nettask = {'name': 'guestNetworkForBasicZone', 'zoneid': zone_id, 'displaytext': 'guestNetworkForBasicZone',
                       'networkofferingid': netoff_id}
            result = api.createNetwork(nettask)
            # print result
            net_id = result['network']['id']

            podtask = {'name': podname, 'zoneid': zone_id, 'gateway': gw, 'netmask': nmask, 'startip': pod_start,
                       'endip': pod_end}
            result = api.createPod(podtask)
            # print result
            pod_id = result['pod']['id']
            print('Created Pod ' + podname + ' with id: ' + pod_id)

            vlantask = {'podid': pod_id, 'networkid': net_id, 'gateway': gw, 'netmask': nmask, 'startip': vlan_start,
                        'endip': vlan_end, 'forvirtualnetwork': 'false'}
            result = api.createVlanIpRange(vlantask)
            # print result

            clustertask = {'zoneid': zone_id, 'hypervisor': hpvr, 'clustertype': 'CloudManaged', 'podid': pod_id,
                           'clustername': clus_name}
            result = api.addCluster(clustertask)
            # print result
            cluster_id = result['cluster'][0]['id']
            print('Created Cluster ' + clus_name + ' with id: ' + cluster_id)

            for host_ip in host_ips.split(','):
                hosttask = {'zoneid': zone_id, 'podid': pod_id, 'clusterid': cluster_id, 'hypervisor': hpvr,
                            'username': host_user, 'password': host_passwd, 'url': 'http://' + host_ip}
                api.addHost(hosttask)
                # print result
                print('Added host (' + host_ip + ') to cluster.')

            primarytask = {'zoneid': zone_id, 'podid': pod_id, 'clusterid': cluster_id, 'name': 'MyNFSPrimary',
                           'url': prm_storage}
            api.createStoragePool(primarytask)
            # print result

            secondarytask = {'zoneid': zone_id, 'url': sec_storage}
            api.addSecondaryStorage(secondarytask)
            # print result
            print('Secondary storage added to zone.')

            enablezonetask = {'id': zone_id, 'allocationstate': 'Enabled'}
            api.updateZone(enablezonetask)
            # print result
            print('Primary storage added to zone.')
        except Exception, e:
            print('Error creating new zone.')
            print(str(e))

    # Configures cloudmonkey environment to access currently deployed CloudStack Management API
    def cloudmonkeyConfig(self, api_srv, jobid):
        print(api_srv)
        self.go_playbook('./ansible/play-books/cldstk-api-enable.yml', jobid)
        print("Waiting for cloudstack-management server to come online before finishing......")
        time.sleep(80)
        url = "http://{0}:8096/client/api?command=registerUserKeys&id=2&response=json".format(api_srv)
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        apikey = data['registeruserkeysresponse']['userkeys']['apikey']
        secretkey = data['registeruserkeysresponse']['userkeys']['secretkey']
        call(["cloudmonkey", "set", "url", "http://{0}:8096/client/api".format(api_srv)], shell=False)
        call(["cloudmonkey", "set", "username", "admin"], shell=False)
        call(["cloudmonkey", "set", "apikey", apikey], shell=False)
        call(["cloudmonkey", "set", "secretkey", secretkey], shell=False)
        call(["cloudmonkey", "sync"], shell=False)
        self.go_playbook('./ansible/play-books/cldstk-api-disable.yml', jobid)
        call(["cloudmonkey", "set", "url", "http://{0}:8080/client/api".format(api_srv)], shell=False)

    # Sets up the environment and installs dependancies needed for "cldstk-deploy" to run.
    def setupenv(self):
        if platform.system() == 'Darwin':
            #call(["make"], shell=False)
            prog = Popen(['make'], stderr=PIPE)
            errdata = prog.communicate()[1]
            if len(errdata) != 0:
                if 'no developer tools' in errdata:
                    raw_input('Hit [enter] after you have install the command line deveoper tools.: ')
            call(["sudo", "curl", "https://bootstrap.pypa.io/ez_setup.py", "-o", "-", "|", "sudo", "python"], shell=False)
            call(["sudo", "easy_install", "pip"], shell=False)
            call(["sudo", "pip", "install", "ansible"], shell=False)
            call(["sudo", "pip", "install", "wget"], shell=False)
            call(["sudo", "pip", "install", "netifaces"], shell=False)
            call(["sudo", "pip", "install", "cloudmonkey"], shell=False)
            #call(["ssh-keyscan -H '127.0.0.1' >> ~/.ssh/known_hosts"], shell=True)

        elif platform.system() == 'Linux' and platform.dist()[0] == 'centos':
            call(["rpm", "-Uvh", "http://mirror.pnl.gov/epel/6/x86_64/epel-release-6-8.noarch.rpm"], shell=False)
            call(["yum", "install", "wget", "-y"], shell=False)
            call(["yum", "install", "sshpass", "-y"], shell=False)
            call(["yum", "install", "python-setuptools", "-y"], shell=False)
            call(["yum", "install", "python-pip", "-y"], shell=False)
            call(["pip", "install", "wget"], shell=False)
            call(["yum", "install", "ansible", "-y"], shell=False)
            call(["easy_install", "cloudmonkey"], shell=False)
            call(["service", "iptables", "stop"], shell=False)
            call(["chkconfig", "iptables", "off"], shell=False)

            if os.path.isfile(userHome + "/.ssh/known_hosts") is False:
                call(["mkdir ~/.ssh"], shell=True)
                call(["touch ~/.ssh/known_hosts"], shell=True)
            else:
                pass
            call(["ssh-keyscan -H '127.0.0.1' >> ~/.ssh/known_hosts"], shell=True)
        else:
            print('Operating System Not Supported!!!')

    # Downloads the rpms for CloudStack to be used for a "local" install
    def get_rpms(self, repo):
        import wget
        # Download rpm packages from remote repository
        wgetUrl = configs['local'][repo]['download']
        wgetFile = configs['local'][repo]['download'].split('/')[-1]

        os.chdir(savedHome + __repolocalpath__)
        call(["rm", "-rf", repo], shell=False)
        print('Downloading CloudStack RPMS.......')
        wget.download(wgetUrl)
        print('Complete!')
        #call(["wget", wgetUrl], shell=False)
        call(["tar", "-zxvf", wgetFile], shell=False)
        call(["rm", "-f", wgetFile], shell=False)

        os.chdir(savedHome)

    # Downloads the systemtemplates for CloudStack to be used to preseed secondary storage
    def getsystemtemplate(self, repo):
        import wget
        # Download rpm packages from remote repository
        wgetUrl = configs['internet'][repo]['systmplurl']
        if not os.path.exists(savedHome + __systmpllocalpath__ + repo):
            os.makedirs(savedHome + __systmpllocalpath__ + repo)
        os.chdir(savedHome + __systmpllocalpath__ + repo)
        print('Downloading CloudStack KVM System Template.......')
        wget.download(wgetUrl)
        print('Complete!')
        #call(["wget", wgetUrl], shell=False)
        os.chdir(savedHome)

    # Starts the nodejs webserver and kills currently running webserver if required
    def startnode(self):
        print('Starting webserver........')
        print ""
        try:
            if urllib.urlopen("http://0.0.0.0:8080").getcode() == 200:
                print('Server already started on port 8080.')
            else:
                #os.chdir('./public')
                os.system('python SimpleAsyncHTTPServer.py -p 8080 -r public/ &')
                #os.chdir('..')
        except IOError:
            #os.chdir('./public')
            os.system('python SimpleAsyncHTTPServer.py -p 8080 -r public/ &')
            #os.chdir('..')

        time.sleep(3)

    # Stops nodejs webserver if running
    def stopnode(self):
        # Check if webserver is already running. If so, kill and restart new process
        chkprog = Popen(['node_modules/forever/bin/forever', 'list'], stdout=PIPE)
        stdout, stderr = chkprog.communicate()
        a = stdout.split('\n')
        if len(a) > 2:
            for l in a:
                if '[' in l and ']' in l:
                    try:
                        stopnodeid = l.split(' ')[4][1:-1]
                        print 'id = ' + stopnodeid
                        killprog = Popen(['node_modules/forever/bin/forever', 'stop', '{0}'.format(stopnodeid)],
                                         stderr=PIPE)
                        errdata = killprog.communicate()[1]
                        if len(errdata) != 0:
                            print errdata.strip("\n")
                    except:
                        pass
                else:
                    pass
            print('Stopped webserver........')
        else:
            print('No webservers found........')
        print('')

    # Runs ansible/play-books/run-all.yml, includes ALL playbooks
    def startall(self, jobid):
        playbook = './ansible/play-books/run-all.yml'
        self.go_playbook(playbook, jobid)

    # Runs ansible/play-books/all-in-one.yml, includes ALL playbooks except for replication
    def startall_in_one(self, jobid):
        playbook = './ansible/play-books/all-in-one.yml'
        self.go_playbook(playbook, jobid)

    # Updates host files and config files
    def runfileupdates(self, jobid):
        playbook = './ansible/play-books/cldstk-files-update.yml'
        self.go_playbook(playbook, jobid)

    # Installs and configures Cloudstack Agents (KVM Host)
    def kvm_agent_install(self, jobid):
        playbook = './ansible/play-books/cldstk-agent_deploy.yml'
        self.go_playbook(playbook, jobid)

    # Installs and configures CloudStack Management server (Web Front-End Only)
    def management_install(self, jobid):
        playbook = './ansible/play-books/cldstk-mgmt_deploy.yml'
        self.go_playbook(playbook, jobid)

    # Installs and configures MySQL Primary database server
    def db_install(self, jobid):
        playbook = './ansible/play-books/mysql-server-install.yml'
        self.go_playbook(playbook, jobid)

    # Installs and configures MySQL replication and replica database server
    def db_replication_install(self, jobid):
        playbook = './ansible/play-books/mysql-replication-setup.yml'
        self.go_playbook(playbook, jobid)

    # Preseed the CloudStack system template
    def systemtemplate_install(self, jobid):
        playbook = './ansible/play-books/cldstk-preseed-kvm-systmpl.yml'
        self.go_playbook(playbook, jobid)

    def list_jobs(self):
        dirs = os.listdir('ansible/jobs/')
        for d in dirs:
            print(d)

    def delete_job(self, jobid):
        try:
            delete_now = Popen(['rm', '-frv', 'ansible/jobs/{0}'.format(jobid)], stderr=PIPE)
            errdata = delete_now.communicate()[1]
            if len(errdata) != 0:
                print errdata.strip("\n")

        except:
            print('Could not find and delete job..')

    def delete_jobs(self):
        try:
            dirs = os.listdir('ansible/jobs/')
            for d in dirs:
                delete_now = Popen(['rm', '-frv', 'ansible/jobs/{0}'.format(d)], stderr=PIPE)
                errdata = delete_now.communicate()[1]
                if len(errdata) != 0:
                    print errdata.strip("\n")
        except:
            print('Could not find and delete job..')

    def createZoneFile(self, jobdir, nfs_server='None'):
        zname = ''
        podname = ''
        clus_name = ''
        dns_ext = ''
        dns_int = ''
        gw = ''
        nmask = ''
        pod_start = ''
        pod_end = ''
        vlan_start = ''
        vlan_end = ''
        host_ips = ''
        host_user = ''
        host_passwd = ''
        sec_storage = ''
        prm_storage = ''

        while zname.lower() == '':
            zname = raw_input('Basic Zone Name: ')
        while dns_ext.lower() == '':
            dns_ext = raw_input('External DNS: ')
        while dns_int.lower() == '':
            dns_int = raw_input('Internal DNS: ')
        while gw.lower() == '':
            gw = raw_input('Gateway: ')
        while nmask.lower() == '':
            nmask = raw_input('NetMask: ')

        print('Hypervisor type only support KVM at this time.')

        while podname.lower() == '':
            podname = raw_input('Pod Name: ')
        while pod_start.lower() == '':
            pod_start = raw_input('Pod Start IP: ')
        while pod_end.lower() == '':
            pod_end = raw_input('Pod End IP: ')
        while vlan_start.lower() == '':
            vlan_start = raw_input('Guest Start IP: ')
        while vlan_end.lower() == '':
            vlan_end = raw_input('Guest End IP: ')
        while clus_name.lower() == '':
            clus_name = raw_input('Cluster Name: ')
        while host_ips.lower() == '':
            host_ips = raw_input('Host DNS/IP (separated by comma): ')
        while host_user.lower() == '':
            host_user = raw_input('Host User: ')
        while host_passwd.lower() == '':
            host_passwd = getpass.getpass('Host Password: ')

        if nfs_server != 'None':
            print('Using default: nfs://{0}/opt/nfs/secondary'.format(nfs_server))
            print('Using default: nfs://{0}/opt/nfs/primary'.format(nfs_server))
            sec_storage = 'nfs://{0}/opt/nfs/secondary'.format(nfs_server)
            prm_storage = 'nfs://{0}/opt/nfs/primary'.format(nfs_server)
        else:
            print("Enter the secondary and primary storage mount points.")
            print("Example: nfs://192.168.78.148/mnt/volume1/secondary")
            while sec_storage.lower() == '':
                sec_storage = raw_input('Secondary Storage: ')
            while prm_storage.lower() == '':
                prm_storage = raw_input('Primary Storage: ')

        var_file = open(jobdir + '/vars_file.yml').readlines()
        print(jobdir)
        for k in var_file:
            a = k.find('mgmt_primary')
            if a == 0:
                cldstk_mgmt = k.split('=')[1].strip()

        zonecfg = [
            "mgmt_primary = %s" % cldstk_mgmt,
            "zname = %s" % zname,
            "podname = %s" % podname,
            "clus_name = %s" % clus_name,
            "dns_ext = %s" % dns_ext,
            "dns_int = %s" % dns_int,
            "gw = %s" % gw,
            "nmask = %s" % nmask,
            "hpvr = KVM",
            "pod_start = %s" % pod_start,
            "pod_end = %s" % pod_end,
            "vlan_start = %s" % vlan_start,
            "vlan_end = %s" % vlan_end,
            "host_ips = %s" % host_ips,
            "host_user = %s" % host_user,
            "host_passwd = %s" % host_passwd,
            "sec_storage = %s" % sec_storage,
            "prm_storage = %s" % prm_storage]

        zone_file = open(jobdir + '/zone_conf', 'w')
        for l in zonecfg:
            zone_file.writelines(l + '\n')
        zone_file.close()

        print('Zone.cfg file has been created.')

    def checkurl(self, url):
        p = urlparse(url)
        conn = httplib.HTTPConnection(p.netloc)
        conn.request('HEAD', p.path)
        resp = conn.getresponse()
        return resp.status

    def runallwithzone(self, jobid):
        jobdir = 'ansible/jobs/' + jobid

        zone_file = open(jobdir + '/zone_conf').readlines()
        # print zone_file
        for k in zone_file:
            a = k.find('mgmt_primary')
            if a == 0:
                cldstk_mgmt = k.split('=')[1].strip()

        print('Management Server: http://{0}:8080/client'.format(cldstk_mgmt))
        siteup = False
        tries = 0
        while siteup != 302:
            if tries == 20:
                print('Waiting for management server timed out.')
                sys.exit()
            else:
                try:
                    siteup = self.checkurl('http://{0}:8080/client'.format(cldstk_mgmt))
                    tries += 1
                except:
                    tries += 1
                    print('Waiting for management server...')
                    time.sleep(10)
        print('Management server is running...')
        self.cloudmonkeyConfig(cldstk_mgmt, jobid)
        print('Waiting for management server to restart.')
        time.sleep(20)
        siteup = False
        tries = 0
        while siteup != 302:
            if tries == 10:
                print('Waiting for management server timed out.')
                sys.exit()
            else:
                try:
                    siteup = self.checkurl('http://{0}:8080/client'.format(cldstk_mgmt))
                    tries += 1
                except:
                    tries += 1
                    print('Waiting for management server...')
                    time.sleep(10)

        self.createZone(cldstk_mgmt, jobdir)

    def createjobdir(self):
        if 'jobs' not in os.listdir('ansible/'):
            os.mkdir('ansible/jobs', 0755)
        randnum = random.randrange(10000000, 99999999)
        today = datetime.date.today()
        hour, minute = datetime.datetime.now().hour, datetime.datetime.now().minute
        jobdir = 'ansible/jobs/{0}-{1}-{2}-{3}'.format(today, hour, minute, randnum)
        os.mkdir(jobdir, 0755)
        return jobdir

    def createhostfile(self, jobdir, db_master, db_slave, cldstk_mgmt, cldstk_kvmhost, cldstk_web, db_primary,
                       mgmtrestart, nfs_server):
        # Write the /etc/ansible/hosts file
        systemlist = []
        hostsfile = open(jobdir + '/hosts', 'w')
        if platform.system() == 'Darwin':
            hostsfile.write('[localhosts]\n\n')
        else:
            hostsfile.write('[localhosts]\n127.0.0.1\n\n')

        hostsfile.write('[db_master]\n')
        if len(db_master) != 0:
            hostsfile.write('%s\n' % db_master)
            systemlist.append('%s' % db_master)
        else:
            hostsfile.write('%s\n' % db_primary)
            systemlist.append('%s' % db_primary)

        hostsfile.write('\n[db_slave]\n')
        if len(db_slave) != 0:
            hostsfile.write('%s\n' % db_slave)
            systemlist.append('%s' % db_slave)

        hostsfile.write('\n[mysql_servers]\n')
        if len(db_master) != 0:
            hostsfile.write('%s\n' % db_master)
            systemlist.append('%s' % db_master)
        if len(db_slave) != 0:
            hostsfile.write('%s\n' % db_slave)
            systemlist.append('%s' % db_slave)

        hostsfile.write('\n[cldstk_mgmt]\n')
        if len(cldstk_mgmt) != 0:
            cldstk_mgmt = cldstk_mgmt.split(',')[0]
            hostsfile.write('%s\n' % cldstk_mgmt)
            systemlist.append('%s' % cldstk_mgmt)

        hostsfile.write('\n[cldstk_web]\n')
        if len(cldstk_web) != 0:
            cldstk_web = cldstk_web.split(',')
            for w in cldstk_web:
                hostsfile.write('%s\n' % w.strip())
                systemlist.append('%s' % w.strip())

        hostsfile.write('\n[cldstk_kvm]\n')
        if len(cldstk_kvmhost) != 0:
            cldstk_kvmhost = cldstk_kvmhost.split(',')
            for k in cldstk_kvmhost:
                hostsfile.write('%s\n' % k.strip())
                systemlist.append('%s' % k.strip())

        hostsfile.write('\n[mgmt_restart]\n')
        if len(mgmtrestart) != 0:
            mgmt_restart = mgmtrestart.split(',')
            for w in mgmt_restart:
                hostsfile.write('%s\n' % w.strip())
                systemlist.append('%s' % w.strip())
        hostsfile.write('\n[nfs_servers]\n')
        if len(nfs_server) != 0:
            nfs_servers = nfs_server.split(',')
            for w in nfs_servers:
                hostsfile.write('%s\n' % w.strip())
                systemlist.append('%s' % w.strip())

        hostsfile.close()
        print('ansible hosts file successfully writing to disk.....')
        return systemlist

    def createrepo_file(self, jobdir, repo_type, repo_version):
        # Get the ip for eth0. This is only work if there is an eth0 device.
        if platform.system() == 'Darwin':
            import netifaces as ni
            ni.ifaddresses('en0')
            eth_ip = ni.ifaddresses('en0')[2][0]['addr']
        else:
            eth = 'eth0'
            eth_ip = commands.getoutput("ip address show dev " + eth).split()
            eth_ip = eth_ip[eth_ip.index('inet') + 1].split('/')[0]

        __localurl__ = 'http://{0}:8080'.format(eth_ip)

        w_file = open(jobdir + '/cloudstack.repo', 'w')
        w_file.write('[cloudstack]\n')
        w_file.write('name=cloudstack\n')
        if repo_type == 'Local':
            w_file.write('baseurl={0}/rpms/rhel/{1}/\n'.format(__localurl__, repo_version))

        else:
            w_file.write('baseurl=http://cloudstack.apt-get.eu/rhel/{0}/\n'.format(repo_version))
        w_file.write('enabled=1\n')
        w_file.write('gpgcheck=0\n')
        w_file.close()

    def createvarsfile(self, jobdir, cldstk_mgmt, db_master, db_slave, cloud_repl_password, mysql_root_password,
                       nfs_server,
                       nfs_path, repo_type, repo_version, db_primary, jobid):
        # Get the ip for eth0. This is only work if there is an eth0 device.
        if platform.system() == 'Darwin':
            import netifaces as ni
            ni.ifaddresses('en0')
            eth_ip = ni.ifaddresses('en0')[2][0]['addr']
        else:
            eth = 'eth0'
            eth_ip = commands.getoutput("ip address show dev " + eth).split()
            eth_ip = eth_ip[eth_ip.index('inet') + 1].split('/')[0]

        __localurl__ = 'http://{0}:8080'.format(eth_ip)

        system_template = ''
        if repo_type == 'Local':
            system_template = '{0}/templates/{1}/{2}'.format(__localurl__, repo_version,
                                                             configs['local'][repo_version]['systmplfile'])

        if repo_type == 'Internet':
            system_template = '{0}'.format(configs['internet'][repo_version]['systmplurl'])

        # Write the vars_file.yml file
        vars_file = open(jobdir + '/vars_file.yml', 'w')
        vars_file.write('job_id=%s\n' % jobid)
        if len(db_master) != 0:
            vars_file.write('master=%s\n' % db_master)
        else:
            vars_file.write('master=%s\n' % db_primary)

        vars_file.write('mgmt_primary=%s\n' % cldstk_mgmt)
        vars_file.write('master=%s\n' % db_master)
        vars_file.write('slave=%s\n' % db_slave)
        vars_file.write('cloud_repl_password=%s\n' % cloud_repl_password)
        vars_file.write('mysql_root_password=%s\n' % mysql_root_password)
        vars_file.write('nfs_server=%s\n' % nfs_server)
        vars_file.write('nfs_path=%s\n' % nfs_path)
        vars_file.write('repotype=%s\n' % repo_type)
        vars_file.write('repoversion=%s\n' % repo_version)
        vars_file.write('systemtemplate=%s\n' % system_template)
        vars_file.close()

        print('vars_file successfully writing to disk.....')

    def getsshkey(self, systemlist):
        # Add systems ssh rsa keys to ~/.ssh/known_hosts file
        uniquesys = []
        for system in systemlist:
            if system not in uniquesys:
                uniquesys.append(system)
                call(["ssh-keyscan -H '%s' >> ~/.ssh/known_hosts" % system], shell=True)
            else:
                pass

    def go_question(self):
        self.startnode()
        print ""
        print "Cloudstack Deployment: Answer the questions below...."
        print ""
        installallinone = ''
        while installallinone.lower() != 'y' and installallinone.lower() != 'n':
            installallinone = raw_input('Install all-in-one?[Y/n]: ')

        if installallinone.lower() == 'y':
            db_master = raw_input('All-in-one Server[dns/ip]: ')
            cldstk_mgmt = db_master
            cldstk_kvmhost = db_master
            cldstk_web = ''
            db_slave = ''
            db_primary = ''
            mgmtrestart = ''

        else:
            installmysql = ''
            while installmysql.lower() != 'y' and installmysql.lower() != 'n':
                installmysql = raw_input('Install Primary Database Server?[Y/n]: ')

            if installmysql.lower() == 'y':
                db_master = raw_input('Db Server[dns/ip]: ')
            else:
                db_master = ''

            installmysqlreplica = ''
            while installmysqlreplica.lower() != 'y' and installmysqlreplica.lower() != 'n':
                installmysqlreplica = raw_input('Configure Database Replica?[Y/n]: ')

            if installmysqlreplica.lower() == 'y':
                db_slave = raw_input('DB Replica Server[dns/ip]: ')
            else:
                db_slave = ''

            installmgmtsrv = ''
            while installmgmtsrv.lower() != 'y' and installmgmtsrv.lower() != 'n':
                installmgmtsrv = raw_input('Install Primary Management Server?[Y/n]: ')

            if installmgmtsrv.lower() == 'y':
                cldstk_mgmt = raw_input('Server[dns/ip]: ')
            else:
                cldstk_mgmt = ''

            installwebsrv = ''
            while installwebsrv.lower() != 'y' and installwebsrv.lower() != 'n':
                installwebsrv = raw_input('Install additional Management servers?[Y/n]: ')

            if installwebsrv.lower() == 'y':
                cldstk_web = raw_input('Comma separated list: ')
            else:
                cldstk_web = ''

            if installmysql.lower() == 'n' and installmgmtsrv == 'y' \
                    or installwebsrv == 'y' and installmysql.lower() == 'n' \
                    or installmysqlreplica.lower() == 'y' and installmysql.lower() == 'n':
                db_primary = raw_input('Whats the current DB Server?[dns/ip]: ')
            else:
                db_primary = ''

            installkvmhost = ''
            while installkvmhost.lower() != 'y' and installkvmhost.lower() != 'n':
                installkvmhost = raw_input('Install KVM Hosts?[Y/n]: ')

            if installkvmhost.lower() == 'y':
                cldstk_kvmhost = raw_input('Comma separated list: ')
            else:
                cldstk_kvmhost = ''

            mgmtrestart = ''
            if installmysqlreplica.lower() == 'y' and installmgmtsrv.lower() == 'n' and installwebsrv.lower() == 'n':
                while mgmtrestart.lower() == '':
                    print('Need to restart services on management servers. List them below.')
                    mgmtrestart = raw_input('Comma separated list: ')
            else:
                pass

        preseedtemplates = ''
        while preseedtemplates.lower() != 'y' and preseedtemplates.lower() != 'n':
            preseedtemplates = raw_input('Install System Templates?[Y/n]: ')

        if preseedtemplates.lower() == 'y' and installallinone.lower() == 'y':
            nfs_server = db_master
            nfs_path = '/opt/nfs/secondary'
        else:
            if preseedtemplates.lower() == 'y':
                nfs_server = raw_input('NFS Server[dns/ip]: ')
            else:
                nfs_server = ''

            if preseedtemplates.lower() == 'y':
                nfs_path = raw_input('NFS Secondary Storage Path[/nfsdirpath]: ')
            else:
                nfs_path = ''

        changerepotype = ''
        while changerepotype.lower() != 'y' and changerepotype.lower() != 'n':
            changerepotype = raw_input('Change install type to "Internet"?[Y/n]: ')
        if changerepotype.lower() == 'y':
            repo_type = 'Internet'
        else:
            repo_type = 'Local'

        changerepoversion = ''
        while changerepoversion.lower() not in __versionsupport__:
            changerepoversion = raw_input('Which version to install {0}?: '.format(__versionsupport__))
        repo_version = changerepoversion.lower()

        ssh_addrsakeys = ''

        while ssh_addrsakeys.lower() != 'y' and ssh_addrsakeys.lower() != 'n':
            ssh_addrsakeys = raw_input('Add ssh rsa keys to ~/.ssh/known_hosts?[Y/n]: ')
        if ssh_addrsakeys.lower() == 'y':
            addrsakeys = 'True'
        else:
            addrsakeys = 'False'

        # Create job file for ansible files
        jobdir = self.createjobdir()
        jobid = jobdir.split('/')[-1]
        print('jobid: ' + jobid)

        # Create host file for ansible
        systemlist = self.createhostfile(jobdir, db_master, db_slave, cldstk_mgmt, cldstk_kvmhost, cldstk_web,
                                         db_primary, mgmtrestart, nfs_server)
        # Create vars file
        self.createvarsfile(jobdir, cldstk_mgmt, db_master, db_slave, cloud_repl_password, mysql_root_password,
                            nfs_server,
                            nfs_path, repo_type, repo_version, db_primary, jobid)

        self.createrepo_file(jobdir, repo_type, repo_version)

        if addrsakeys == 'True':
            self.getsshkey(systemlist)

        create_zone = raw_input('Create Basic Zone?[Y/n]: ')

        if create_zone.lower() == 'y':
            if installallinone.lower() == 'y':
                self.createZoneFile(jobdir, nfs_server)
            else:
                self.createZoneFile(jobdir)
        else:
            print('No Basic Zone will be created')

        startinstallation = raw_input('Start installation now?[Y/n]: ')

        if startinstallation.lower() == 'y':
            self.startall(jobid)

            if create_zone.lower() == 'y':
                self.runallwithzone(jobid)

        else:
            print('Exiting program......')
            sys.exit()


def main():
    cldstkdeploy = CldStkDeploy()

    parser = OptionParser(usage="cldstk-deploy [options] [commands]",
                          description=__description__,
                          epilog="Try cldstk-deploy [-h|--help]")

    parser.add_option("-v", "--version", action="version",
                      help="show cldstk-deploy's version and exit")

    parser.add_option("--setup",
                      action="store",
                      metavar='<type>', choices=['all'],
                      help="The setup type that you'd like to perform. Choices are ['all']")

    parser.add_option("--config",
                      action="store", nargs=2, choices=['api', 'zone'],
                      metavar='<[api|zone]> <servername>',
                      help="The setup type that you'd like to perform. Choices are ['api','zone']")

    parser.add_option("--getall",
                      action="store", metavar='<version>',
                      choices=__versionsupport__,
                      help="Pre download the cloudstack rpms and system template for CentOS.")

    parser.add_option("--getrpm",
                      action="store", metavar='<version>',
                      choices=__versionsupport__,
                      help="Pre download the cloudstack rpms for CentOS.")

    parser.add_option("--getsystmpl",
                      action="store", metavar='<version>',
                      choices=__versionsupport__,
                      help="Pre download the cloudstack system template for kvm.")

    parser.add_option("-w", "--web",
                      action="store",
                      metavar='<start>', choices=['start'],
                      help="Used to start the web server.")

    parser.add_option("-l", "--list",
                      action="store",
                      metavar='<all>',
                      help="List deployment jobs that have been created.")

    parser.add_option("-d", "--delete",
                      action="store", nargs=1,
                      metavar='<[jobid|all]>',
                      help="Delete deployment jobs. Options are a single job by 'jobid' or 'all' jobs.")

    parser.add_option("-i", "--install",
                      action="store", nargs=2,
                      metavar='[all|db|kvm|mgmt|dbrepl|systmpl|allzone] <jobid>',
                      help="The installation type that you'd like to perform.")

    (options, args) = parser.parse_args()

    cldstkdeploy.getpasswd()

    if options.setup:
        cldstkdeploy.setupenv()
    else:

        if len(sys.argv) == 1:
            cldstkdeploy.go_question()

        if options.delete:
            if options.delete == 'all':
                cldstkdeploy.delete_jobs()
            else:
                cldstkdeploy.delete_job(options.delete)
            sys.exit()

        if options.list == 'all':
            cldstkdeploy.list_jobs()
            sys.exit()

        if options.web == 'start':
            cldstkdeploy.startnode()
            sys.exit()
        # if options.web == 'stop':
        # stopnode()
        # sys.exit()

        if options.getall:
            cldstkdeploy.get_rpms(options.getall)
            cldstkdeploy.getsystemtemplate(options.getall)
            sys.exit()

        if options.getrpm:
            cldstkdeploy.get_rpms(options.getrpm)
            sys.exit()

        if options.getsystmpl:
            cldstkdeploy.getsystemtemplate(options.getsystmpl)
            sys.exit()

        if options.config:
            if options.config[0] == 'api':
                cldstkdeploy.cloudmonkeyConfig(options.config[1])
            elif options.config[0] == 'zone':
                cldstkdeploy.createZoneFile()
                cldstkdeploy.createZone(options.config[1])
            else:
                print('Wrong Syntax.....')

        if options.install:
            cldstkdeploy.startnode()

            if options.install[0] == 'all':
                print(options.install[1])
                cldstkdeploy.startall(options.install[1])
            elif options.install[0] == 'allzone':
                cldstkdeploy.startall(options.install[1])
                cldstkdeploy.runallwithzone(options.install[1])
            elif options.install[0] == 'kvm':
                cldstkdeploy.runfileupdates(options.install[1])
                cldstkdeploy.kvm_agent_install(options.install[1])
            elif options.install[0] == 'mgmt':
                cldstkdeploy.runfileupdates(options.install[1])
                cldstkdeploy.management_install(options.install[1])
            elif options.install[0] == 'db':
                cldstkdeploy.runfileupdates(options.install[1])
                cldstkdeploy.db_install(options.install[1])
            elif options.install[0] == 'dbrepl':
                cldstkdeploy.runfileupdates(options.install[1])
                cldstkdeploy.db_replication_install(options.install[1])
            elif options.install[0] == 'systmpl':
                cldstkdeploy.systemtemplate_install(options.install[1])
            sys.exit()


if __name__ == '__main__':
    main()
