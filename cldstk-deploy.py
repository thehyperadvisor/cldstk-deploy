#!/usr/bin/python
#new
import hashlib, hmac, string, base64
from subprocess import call,Popen, PIPE
import sys, os, commands, urllib, json
import getpass, time
import httplib
from urlparse import urlparse

try:
    # Set ansible api variables
    from ansible.playbook import PlayBook
    from ansible import callbacks
    from ansible import utils
    playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
    stats = callbacks.AggregateStats()
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
except:
    pass


# Set user passwords for mysql users
cloud_repl_password = 'password'
mysql_root_password = 'PaSSw0rd1234'

# Set variables for current working directory
savedHome = os.getcwd()
userHome = os.path.expanduser('~')

# Get the ip for eth0. This is only work if there is an eth0 device.
eth = 'eth0'
eth_ip = commands.getoutput("ip address show dev " + eth).split()
eth_ip = eth_ip[eth_ip.index('inet') + 1].split('/')[0]


def runPlaybook(play):
    playbook = PlayBook(remote_user='root',
                        remote_pass=passwd,
                        playbook=play,
                        callbacks=playbook_cb,
                        runner_callbacks=runner_cb,
                        stats=stats,
                        host_list='ansible/hosts'
                        )

    playoutput = playbook.run()
    for l in playoutput:print l,playoutput[l]

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

def createZone(api_srv):
    readconfig = open(userHome + '/.cloudmonkey/config').readlines()
    for k in readconfig:
        a = k.find('apikey')
        if a == 0:
            apiKey = k.split('=')[1].strip()
    for k in readconfig:
        a = k.find('secretkey')
        if a == 0:
            secret = k.split('=')[1].strip()
    for k in readconfig:
        a = k.find('host')
        if a == 0 and api_srv == k.split('=')[1].strip():
            api_url = 'http://' + k.split('=')[1].strip() + ':8080/client/api'
            print api_url

    api = CloudStack(api_url, apiKey, secret)

    zone_file = open(savedHome + '/zone_conf').readlines()
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
        zonetask = {'dns1': dns_ext,'internaldns1':dns_int,'name':zname,'networktype':'Basic'}
        result = api.createZone(zonetask)
        #print "id", result
        zone_id = result['zone']['id']
        print('Created Zone ' + zname + ' with id: ' + zone_id)

        phynettask = {'name': 'phy-network','zoneid': zone_id}
        result = api.createPhysicalNetwork(phynettask)
        #print result
        phynet_id = result['id']
        print('Created physical network.')

        addtraffictypetask = {'physicalnetworkid': phynet_id,'traffictype': 'Guest'}
        result = api.addTrafficType(addtraffictypetask)
        #print result

        addtraffictypetask = {'physicalnetworkid': phynet_id,'traffictype': 'Management'}
        result = api.addTrafficType(addtraffictypetask)
        #print result

        updatephynettask = {'id': phynet_id,'state': 'Enabled'}
        result = api.updatePhysicalNetwork(updatephynettask)
        #print result

        listnsptask = {'physicalnetworkid': phynet_id,'name': 'VirtualRouter'}
        result = api.listNetworkServiceProviders(listnsptask)
        #print result
        nsp_id = result['networkserviceprovider'][0]['id']

        listvrtask = {'nspid': nsp_id}
        result = api.listVirtualRouterElements(listvrtask)
        #print result
        vre_id = result['virtualrouterelement'][0]['id']

        configvrtask = {'id': vre_id, 'enabled':'true'}
        result = api.configureVirtualRouterElement(configvrtask)
        #print result

        updatensptask = {'id': nsp_id, 'state':'Enabled'}
        result = api.updateNetworkServiceProvider(updatensptask)
        #print result

        listnsptask = {'physicalnetworkid': phynet_id,'name': 'SecurityGroupProvider'}
        result = api.listNetworkServiceProviders(listnsptask)
        #print result
        nsp_sg_id = result['networkserviceprovider'][0]['id']

        updatensptask = {'id': nsp_sg_id, 'state':'Enabled'}
        result = api.updateNetworkServiceProvider(updatensptask)
        #print result

        listnetofftask = {'name': 'DefaultSharedNetworkOfferingWithSGService'}
        result = api.listNetworkOfferings(listnetofftask)
        #print result
        netoff_id = result['networkoffering'][0]['id']

        nettask = {'name': 'guestNetworkForBasicZone','zoneid': zone_id, 'displaytext':'guestNetworkForBasicZone','networkofferingid': netoff_id}
        result = api.createNetwork(nettask)
        #print result
        net_id = result['network']['id']

        podtask = {'name': podname, 'zoneid': zone_id, 'gateway': gw, 'netmask': nmask, 'startip': pod_start, 'endip': pod_end}
        result = api.createPod(podtask)
        #print result
        pod_id = result['pod']['id']
        print('Created Pod ' + podname + ' with id: ' + pod_id)

        vlantask = {'podid': pod_id, 'networkid': net_id, 'gateway': gw, 'netmask': nmask, 'startip': vlan_start, 'endip': vlan_end, 'forvirtualnetwork':'false'}
        result = api.createVlanIpRange(vlantask)
        #print result

        clustertask = {'zoneid': zone_id, 'hypervisor': hpvr, 'clustertype': 'CloudManaged', 'podid': pod_id, 'clustername':clus_name}
        result = api.addCluster(clustertask)
        #print result
        cluster_id = result['cluster'][0]['id']
        print('Created Cluster ' + clus_name + ' with id: ' + cluster_id)

        for host_ip in host_ips.split(','):
            hosttask = {'zoneid':zone_id, 'podid':pod_id, 'clusterid':cluster_id, 'hypervisor':hpvr, 'username':host_user, 'password':host_passwd, 'url':'http://'+host_ip}
            result = api.addHost(hosttask)
            #print result
            print('Added host (' + host_ip + ') to cluster.')

        primarytask = {'zoneid': zone_id,'podid':pod_id, 'clusterid':cluster_id, 'name':'MyNFSPrimary', 'url':prm_storage}
        result = api.createStoragePool(primarytask)
        #print result

        secondarytask = {'zoneid': zone_id,'url': sec_storage}
        result = api.addSecondaryStorage(secondarytask)
        #print result
        print('Secondary storage added to zone.')

        enablezonetask = {'id': zone_id,'allocationstate':'Enabled'}
        result = api.updateZone(enablezonetask)
        #print result
        print('Primary storage added to zone.')
    except:
        print('Error creating new zone.')


# Configures cloudmonkey environment to access currently deployed CloudStack Management API
def cloudmonkeyConfig(api_srv):
    print(api_srv)
    runPlaybook('./ansible/play-books/cldstk-api-enable.yml')
    print("Waiting for cloudstack-management server to come online before finishing......")
    time.sleep(80)
    url = "http://%s:8096/client/api?command=registerUserKeys&id=2&response=json" % api_srv
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    apikey = data['registeruserkeysresponse']['userkeys']['apikey']
    secretkey = data['registeruserkeysresponse']['userkeys']['secretkey']
    call(["cloudmonkey","set", "host", api_srv], shell=False)
    call(["cloudmonkey","set", "port", "8096"], shell=False)
    call(["cloudmonkey","set", "username", "admin"], shell=False)
    call(["cloudmonkey","set", "apikey", apikey], shell=False)
    call(["cloudmonkey","set", "secretkey", secretkey], shell=False)
    call(["cloudmonkey","sync"], shell=False)
    runPlaybook('./ansible/play-books/cldstk-api-disable.yml')
    call(["cloudmonkey","set", "port", "8080"], shell=False)

# Sets up the environment and installs dependancies needed for "cldstk-deploy" to run.
def setUp():
        call(["rpm","-Uvh", "http://mirror.pnl.gov/epel/6/x86_64/epel-release-6-8.noarch.rpm"], shell=False)
        call(["yum","install", "wget", "-y"], shell=False)
        call(["yum","install", "sshpass", "-y"], shell=False)
        call(["yum","install", "python-setuptools", "-y"], shell=False)
        call(["yum","install", "ansible", "-y"], shell=False)
        call(["yum","install", "nodejs", "-y"], shell=False)
        call(["yum","install", "npm", "-y"], shell=False)
        call(["easy_install","cloudmonkey"], shell=False)
        call(["npm","update"], shell=False)
        call(["npm","install", "forever", "-g"], shell=False)
        call(["service","iptables", "stop"], shell=False)
        call(["chkconfig","iptables", "off"], shell=False)
        if os.path.isfile(userHome + "/.ssh/known_hosts") == False:
                call(["mkdir ~/.ssh"], shell=True)
                call(["touch ~/.ssh/known_hosts"], shell=True)
        else: pass
        call(["ssh-keyscan -H '127.0.0.1' >> ~/.ssh/known_hosts"], shell=True)
        zonecfg = [
        "mgmt_primary = ",
        "zname = ",
        "podname = ",
        "clus_name = ",
        "dns_ext = ",
        "dns_int = ",
        "gw = ",
        "nmask = ",
        "hpvr = ",
        "pod_start = ",
        "pod_end = ",
        "vlan_start = ",
        "vlan_end = ",
        "host_ips = ",
        "host_user = ",
        "host_passwd = ",
        "sec_storage = ",
        "prm_storage = "]

        zone_file = open('./zone_conf','w')
        for l in zonecfg:zone_file.writelines(l + '\n')
        zone_file.close()

        if not os.path.exists(savedHome + '/public/templates/other'):
            os.makedirs(savedHome + '/public/templates/other')
        if not os.path.exists(savedHome + '/public/templates/iso'):
            os.makedirs(savedHome + '/public/templates/iso')

# Downloads the rpms for CloudStack to be used for a "local" install
def getRPMS(repo):
        # Download rpm packages from remote repository
        if repo == '4.4':
                os.chdir(savedHome + '/public/cloudstack.apt-get.eu/rhel/')
                call(["rm","-rf", "4.4"], shell=False)
                call(["wget","https://dl.dropboxusercontent.com/u/3904598/cloudstack-4.4.2-rpms.tar.gz"], shell=False)
                #call(["wget","https://www.dropbox.com/sh/7fa1j6ymap1wrgu/AADUA9LjHSnXLJmwQ7rf3WjKa/cloudstack-4.4.0-rpms.tar.gz"], shell=False)
                call(["tar","-zxvf", "cloudstack-4.4.2-rpms.tar.gz"], shell=False)
                call(["rm -f cloudstack-4.4.2-rpms.tar.*"], shell=True)
        if repo == '4.3':
                os.chdir(savedHome + '/public/cloudstack.apt-get.eu/rhel/')
                call(["rm","-rf", "4.3"], shell=False)
                call(["wget","https://www.dropbox.com/sh/7fa1j6ymap1wrgu/BXfoDzUNWy/cloudstack-4.3.0-rpms.tar.gz"], shell=False)
                call(["tar","-zxvf", "cloudstack-4.3.0-rpms.tar.gz"], shell=False)
                call(["rm -f cloudstack-4.3.0-rpms.tar.*"], shell=True)
        if repo == '4.2':
                os.chdir(savedHome + '/public/cloudstack.apt-get.eu/rhel/')
                call(["rm","-rf", "4.2"], shell=False)
                call(["wget","https://www.dropbox.com/sh/7fa1j6ymap1wrgu/KC6chASB5H/cloudstack-4.2.1-rpms.tar.gz"], shell=False)
                call(["tar","-zxvf", "cloudstack-4.2.1-rpms.tar.gz"], shell=False)
                call(["rm -f cloudstack-4.2.1-rpms.tar.*"], shell=True)
        os.chdir(savedHome)

# Downloads the systemtemplates for CloudStack to be used to preseed secondary storage
def getSystemtemplate(repo):
        # Download rpm packages from remote repository
        if repo == '4.4':
                if not os.path.exists(savedHome + '/public/templates/4.4/'): os.makedirs(savedHome + '/public/templates/4.4/')
                os.chdir(savedHome + '/public/templates/4.4/')
                call(["wget","http://cloudstack.apt-get.eu/systemvm/4.4/systemvm64template-4.4.0-6-kvm.qcow2.bz2"], shell=False)
                #call(["wget","http://download.cloud.com/templates/4.3/systemvm64template-2014-01-14-master-xen.vhd.bz2"], shell=False)
                #call(["wget","http://download.cloud.com/templates/4.3/systemvm64template-2014-01-14-master-vmware.ova"], shell=False)
                os.chdir(savedHome)
        if repo == '4.3':
                if not os.path.exists(savedHome + '/public/templates/4.3/'): os.makedirs(savedHome + '/public/templates/4.3/')
                os.chdir(savedHome + '/public/templates/4.3/')
                call(["wget","http://download.cloud.com/templates/4.3/systemvm64template-2014-01-14-master-kvm.qcow2.bz2"], shell=False)
                #call(["wget","http://download.cloud.com/templates/4.3/systemvm64template-2014-01-14-master-xen.vhd.bz2"], shell=False)
                #call(["wget","http://download.cloud.com/templates/4.3/systemvm64template-2014-01-14-master-vmware.ova"], shell=False)
                os.chdir(savedHome)
        if repo == '4.2':
                if not os.path.exists(savedHome + '/public/templates/4.2/'): os.makedirs(savedHome + '/public/templates/4.2/')
                os.chdir(savedHome + '/public/templates/4.2/')
                os.chdir('public/template/4.2/')
                call(["wget","http://download.cloud.com/templates/4.2/systemvmtemplate-2013-06-12-master-kvm.qcow2.bz2"], shell=False)
                os.chdir(savedHome)

# Starts the nodejs webserver and kills currently running webserver if required
def startnode():
        # Check if webserver is already running. If so, kill and restart new process
        chkprog = Popen(['node_modules/forever/bin/forever', 'list'], stdout=PIPE)
        stdout, stderr = chkprog.communicate()
        a = stdout.split('\n')
        if len(a) > 2:
                for l in a:
                        if '[' in l and ']' in l:  
                                try:
                                        stopnode()
                                except: pass
                        else:pass
        print('Starting webserver........')
        print ""
        prog = Popen(['node_modules/forever/bin/forever', 'start', 'app.js'], stderr=PIPE)
        errdata = prog.communicate()[1]
        if len(errdata) != 0:
                print errdata.strip("\n")
        if len(errdata) == 0: 
                pass
                print('')
                print('Started webserver........')
                print('Browse to: http://%s:8080' % eth_ip)
                print('')

# Stops nodejs webserver if running
def stopnode():
        # Check if webserver is already running. If so, kill and restart new process
        chkprog = Popen(['node_modules/forever/bin/forever', 'list'], stdout=PIPE)
        stdout, stderr = chkprog.communicate()
        a = stdout.split('\n')
        if len(a) > 2:
                for l in a:
                        if '[' in l and ']' in l: 
                                try:
                                        id = l.split(' ')[4][1:-1]
                                        print 'id = ' + id
                                        killprog = Popen(['node_modules/forever/bin/forever', 'stop', '%s' % id], stderr=PIPE)
                                        errdata = killprog.communicate()[1]
                                        if len(errdata) != 0:
                                                print errdata.strip("\n")
                                except: pass
                        else:pass
                print('Stopped webserver........')
        else:
                print('No webservers found........')
        print('')

# Runs ansible/play-books/run-all.yml, includes ALL playbooks
def startall():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/run-all.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]


# Runs ansible/play-books/all-in-one.yml, includes ALL playbooks except for replication
def startall_in_one():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/all-in-one.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]

# Updates host files and config files
def runfileupdates():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/cldstk-files-update.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]

# Installs and configures Cloudstack Agents (KVM Host)
def kvm_agent_Install():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/cldstk-agent_deploy.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]


# Installs and configures CloudStack Management server (Web Front-End Only)
def management_Install():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/cldstk-mgmt_deploy.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]


# Installs and configures MySQL Primary database server
def db_Install():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/mysql-server-install.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]


# Installs and configures MySQL replication and replica database server
def db_replication_Install():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/mysql-replication-setup.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]

# Preseed the CloudStack system template
def systemtemplate_Install():
        playbook = PlayBook(remote_user='root',
                            remote_pass=passwd,
                            playbook='./ansible/play-books/cldstk-preseed-kvm-systmpl.yml',
                            callbacks=playbook_cb,
                            runner_callbacks=runner_cb,
                            stats=stats,
                            host_list='ansible/hosts'
                            )

        playoutput = playbook.run()
        for l in playoutput:print l,playoutput[l]

def createZoneFile():
        zname = ''
        podname = ''
        clus_name = ''
        dns_ext=''
        dns_int=''
        gw=''
        nmask=''
        hpvr=''
        pod_start=''
        pod_end=''
        vlan_start=''
        vlan_end=''
        host_ips=''
        host_user=''
        host_passwd=''
        sec_storage=''
        prm_storage=''

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
        hpvr ='KVM'
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
        print("Enter the secondary and primary storage mount points.")
        print("Example: nfs://192.168.78.148/mnt/volume1/secondary")
        while sec_storage.lower() == '':
            sec_storage = raw_input('Secondary Storage: ')
        while prm_storage.lower() == '':
            prm_storage = raw_input('Primary Storage: ')
        
        var_file = open(savedHome + '/ansible/vars_file.yml').readlines()
        #print zone_file
        for k in var_file:
            a = k.find('mgmt_primary')
            if a == 0:
                cldstk_mgmt = k.split(':')[1].strip()
        
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

        zone_file = open('./zone_conf','w')
        for l in zonecfg:zone_file.writelines(l + '\n')
        zone_file.close()


def checkUrl(url):
    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status

def runAllwithZone():
    zone_file = open(savedHome + '/zone_conf').readlines()
    #print zone_file
    for k in zone_file:
        a = k.find('mgmt_primary')
        if a == 0:
            cldstk_mgmt = k.split('=')[1].strip()

    print('Management Server: ' + 'http://' + cldstk_mgmt + ':8080/client')
    siteup = False
    tries = 0
    while siteup != 302:
        if tries == 10: 
            print('Waiting for management server timed out.')
            sys.exit()
        else:
            try:
                siteup = checkUrl('http://' + cldstk_mgmt + ':8080/client')
                tries += 1
            except:
                tries += 1
                print('Waiting for management server...')
                time.sleep(10)
    print('Management server is running...')
    cloudmonkeyConfig(cldstk_mgmt)
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
                siteup = checkUrl('http://' + cldstk_mgmt + ':8080/client')
                tries += 1
            except:
                tries += 1
                print('Waiting for management server...')
                time.sleep(10)

    createZone(cldstk_mgmt)
# 
def main():
        print ""
        print "Cloudstack Deployment: Answer the questions below...."
        print ""
        installallinone = ''
        while installallinone.lower() != 'y' and installallinone.lower() != 'n':
                installallinone = raw_input('Install all-in-one?[Y/n]: ')

        if installallinone == 'y':
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

            if installmysql.lower() == 'n' and installmgmtsrv == 'y' or installwebsrv == 'y' and installmysql.lower() == 'n' or installmysqlreplica.lower() == 'y' and installmysql.lower() == 'n':
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
            else: pass



        preseedtemplates = ''
        while preseedtemplates.lower() != 'y' and preseedtemplates.lower() != 'n':
                preseedtemplates = raw_input('Install System Templates?[Y/n]: ')

        if preseedtemplates.lower() == 'y':
                nfs_server = raw_input('NFS Server[dns/ip]: ')
        else:
                nfs_server = ''

        if preseedtemplates.lower() == 'y':
                nfs_path = raw_input('NFS Path[/nfsdirpath]: ')
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
        while changerepoversion.lower() != '4.2' and changerepoversion.lower() != '4.3' and changerepoversion.lower() != '4.4':
                changerepoversion = raw_input('Which version to install[4.2, 4.3, 4.4]?: ')
        if changerepoversion.lower() == '4.2':
                repo_version = '4.2'
        elif changerepoversion.lower() == '4.3':
                repo_version = '4.3'
        else:
                repo_version = '4.4'

        ssh_addrsakeys = ''
        systemlist = []
        while ssh_addrsakeys.lower() != 'y' and ssh_addrsakeys.lower() != 'n':
                ssh_addrsakeys = raw_input('Add ssh rsa keys to ~/.ssh/known_hosts?[Y/n]: ')
        if ssh_addrsakeys.lower() == 'y':
                addrsakeys = 'True'
        else:
                addrsakeys = 'False'


        system_template = ''
        if repo_version == '4.4' and repo_type == 'Local':
                system_template = 'http://%s:8080/acs/templates/4.4/systemvm64template-4.4.0-6-kvm.qcow2.bz2' % eth_ip
        if repo_version == '4.3' and repo_type == 'Local':
                system_template = 'http://%s:8080/acs/templates/4.3/systemvm64template-2014-01-14-master-kvm.qcow2.bz2' % eth_ip
        if repo_version == '4.2' and repo_type == 'Local':
                system_template = 'http://%s:8080/acs/templates/4.2/systemvmtemplate-2013-06-12-master-kvm.qcow2.bz2' % eth_ip
        if repo_version == '4.4' and repo_type == 'Internet':
                system_template = 'http://cloudstack.apt-get.eu/systemvm/4.4/systemvm64template-4.4.0-6-kvm.qcow2.bz2'
        if repo_version == '4.3' and repo_type == 'Internet':
                system_template = 'http://download.cloud.com/templates/4.3/systemvm64template-2014-01-14-master-kvm.qcow2.bz2'
        if repo_version == '4.2' and repo_type == 'Internet':
                system_template = 'http://download.cloud.com/templates/4.2/systemvmtemplate-2013-06-12-master-kvm.qcow2.bz2'


        # Write the /etc/ansible/hosts file
        #if installmysql.lower() == 'n' and len(db_master) != 0 or installmysql.lower() == 'n' and len(db_primary) !=0:
        hostsfile = open('./ansible/hosts','w')
        hostsfile.write('[localhost]\n127.0.0.1\n\n')
        
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

        hostsfile.close()
        print('ansible hosts file successfully writing to disk.....')

        # Write the vars_file.yml file
        if len(db_master) != 0:
                vars_file = open('./ansible/vars_file.yml','w')
                vars_file.write('mgmt_primary: %s\n' % cldstk_mgmt)
                vars_file.write('master: %s\n' % db_master)
                vars_file.write('slave: %s\n' % db_slave)
                vars_file.write('cloud_repl_password: %s\n' % cloud_repl_password)
                vars_file.write('mysql_root_password: %s\n' % mysql_root_password)
                vars_file.write('nfs_server: %s\n' % nfs_server)
                vars_file.write('nfs_path: %s\n' % nfs_path)
                vars_file.write('repotype: %s\n' % repo_type)
                vars_file.write('repoversion: %s\n' % repo_version)
                vars_file.write('systemtemplate: %s\n' % system_template)
                vars_file.close()
        else:
                vars_file = open('./ansible/vars_file.yml','w')
                vars_file.write('mgmt_primary: %s\n' % cldstk_mgmt)
                vars_file.write('master: %s\n' % db_primary)
                vars_file.write('slave: %s\n' % db_slave)
                vars_file.write('cloud_repl_password: %s\n' % cloud_repl_password)
                vars_file.write('mysql_root_password: %s\n' % mysql_root_password)
                vars_file.write('nfs_server: %s\n' % nfs_server)
                vars_file.write('nfs_path: %s\n' % nfs_path)
                vars_file.write('repotype: %s\n' % repo_type)
                vars_file.write('repoversion: %s\n' % repo_version)
                vars_file.write('systemtemplate: %s\n' % system_template)
                vars_file.close()

        print('vars_file successfully writing to disk.....')


        # Add systems ssh rsa keys to ~/.ssh/known_hosts file
        if addrsakeys == 'True':
                uniquesys = []
                for system in systemlist:
                        if system not in uniquesys:
                                uniquesys.append(system)
                                call(["ssh-keyscan -H '%s' >> ~/.ssh/known_hosts" % system], shell=True)
                        else: pass
        else: pass

        create_zone = raw_input('Create Basic Zone?[Y/n]: ')

        if create_zone.lower() == 'y':
            createZoneFile()
        else:
                print('No Basic Zone will be created')

        startinstallation = raw_input('Start installation now?[Y/n]: ')

        if startinstallation.lower() == 'y':
                startall()

                if create_zone.lower() == 'y':
                    runAllwithZone()

        else:
                print('Exiting program......')
                sys.exit()

        #else:
        #        print('You must provide the Master Database Server...')
        #        main()

if __name__ == '__main__':
        if len(sys.argv) == 2 and sys.argv[1] == '-s':
                startnode()
                sys.exit()
        if len(sys.argv) == 2 and sys.argv[1] == '-S':
                stopnode()
                sys.exit()
        
        if len(sys.argv) == 3 and sys.argv[1] == 'get':
                if sys.argv[2].split('=')[0] == 'rpmversion' and len(sys.argv[2].split('=')[1]) != 0:
                        getRPMS('%s' % sys.argv[2].split('=')[1])
                elif sys.argv[2].split('=')[0] == 'systemtemplate' and len(sys.argv[2].split('=')[1]) != 0:
                        getSystemtemplate('%s' % sys.argv[2].split('=')[1])
                else:
                        print('Wrong Syntax.....')
                sys.exit()

        passwd = getpass.getpass("Enter Password Here: ")
        if len(sys.argv) == 3 and sys.argv[1] == 'setup':
                if sys.argv[2] == 'all':
                        setUp()
                else:
                    print('Wrong Syntax.....')
        if len(sys.argv) == 4 and sys.argv[1] == 'setup':
                if sys.argv[2] == 'api':
                    cloudmonkeyConfig(sys.argv[3])
                elif sys.argv[2] == 'zone':
                    createZoneFile()
                    createZone(sys.argv[3])
                else:
                    print('Wrong Syntax.....')

        if len(sys.argv) == 3 and sys.argv[1] == 'install':
                startnode()
                if sys.argv[2] == 'all':
                        startall()
                elif sys.argv[2] == 'allwithzone':
                        startall()
                        runAllwithZone()
                elif sys.argv[2] == 'all-in-one':
                        startall_in_one()
                elif sys.argv[2] == 'kvm-agent':
                        runfileupdates()
                        kvm_agent_Install()
                elif sys.argv[2] == 'management':
                        runfileupdates()
                        management_Install()
                elif sys.argv[2] == 'db':
                        runfileupdates()
                        db_Install()
                elif sys.argv[2] == 'db-replication':
                        runfileupdates()
                        db_replication_Install()
                elif sys.argv[2] == 'systemtemplate':
                        systemtemplate_Install()
                sys.exit()
        if len(sys.argv) == 1:
                startnode()
                main()
