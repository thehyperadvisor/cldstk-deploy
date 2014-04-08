#! /usr/bin/env python
from subprocess import call,Popen, PIPE
import sys, os

cloud_repl_password = 'password'
mysql_root_password = 'PaSSw0rd1234'

def packagedownload(repo):
        # Download rpm packages from remote repository
        call(["wget","--no-parent", "-r", "--reject", "index.html*", "http://cloudstack.apt-get.eu/rhel/4.3/"], shell=False)

def startnode():
        # Check if webserver is already running. If so, kill and restart new process
        chkprog = Popen(['node_modules/forever/bin/forever', 'list'], stdout=PIPE)
        stdout, stderr = chkprog.communicate()
        a = stdout.split('\n')
        if len(a) > 2:
                for l in a: 
                        try:
                                id = l.split(' ')[4][1:-1]
                                Popen(['node_modules/forever/bin/forever', 'stop', '%s' % id], stderr=PIPE)
                        except: pass
        print('Starting webserver........')
        print ""
        prog = Popen(['node_modules/forever/bin/forever', 'start', 'app.js'], stderr=PIPE)
        errdata = prog.communicate()[1]
        if len(errdata) != 0:
                print errdata.strip("\n")
        if len(errdata) == 0: 
                pass
        
def stopnode():
        # Check if webserver is already running. If so, kill and restart new process
        chkprog = Popen(['node_modules/forever/bin/forever', 'list'], stdout=PIPE)
        stdout, stderr = chkprog.communicate()
        a = stdout.split('\n')
        if len(a) > 2:
                for l in a: 
                        try:
                                id = l.split(' ')[4][1:-1]
                                Popen(['node_modules/forever/bin/forever', 'stop', '%s' % id], stderr=PIPE)
                        except: pass
                print('Stopped webserver........')
        else:
                print('No webservers found........')
        print('')



def startall():
        # ansible-playbook -i ./ansible/hosts ./ansible/run-all.yml -k
        start_now = Popen(['ansible-playbook', '-i', './ansible/hosts', './ansible/run-all.yml', '-k'], stderr=PIPE)
        errdata = start_now.communicate()[1]
        if len(errdata) != 0:
                print errdata.strip("\n")

def main():
        print ""
        print "Cloudstack Deployment: Answer the questions below...."
        print ""
        installmysql = raw_input('Install MySQL?[Y/n]: ')

        if installmysql.lower() == 'y':
                db_master = raw_input('Db Server[dns/ip]: ')
        else:
                db_master = ''

        if installmysql.lower() == 'n':
                mgmt_master = raw_input('Whats the current DB Server?[dns/ip]: ')
        else:
                mgmt_master = ''

        installmysqlreplica = raw_input('Install MySQL Replica?[Y/n]: ')

        if installmysqlreplica.lower() == 'y':
                db_slave = raw_input('Db Replica Server[dns/ip]: ')
        else:
                db_slave = ''

        installwebsrv = raw_input('Install Management Servers?[Y/n]: ')

        if installwebsrv.lower() == 'y':
                cldstk_web = raw_input('Comma separated list: ')
        else:
                cldstk_web = ''

        installkvmhost = raw_input('Install KVM Hosts?[Y/n]: ')

        if installkvmhost.lower() == 'y':
                cldstk_kvmhost = raw_input('Comma separated list: ')
        else:
                cldstk_kvmhost = ''

        preseedtemplates = raw_input('Install System Templates?[Y/n]: ')

        if preseedtemplates.lower() == 'y':
                nfs_server = raw_input('NFS Server[dns/ip]: ')
        else:
                nfs_server = ''

        if preseedtemplates.lower() == 'y':
                nfs_path = raw_input('NFS Path[/nfsdirpath]: ')
        else:
                nfs_path = ''


        # Write the /etc/ansible/hosts file
        if len(db_master) != 0:
                hostsfile = open('./ansible/hosts','w')
                hostsfile.write('[localhost]\n127.0.0.1\n\n')
                hostsfile.write('[db_master]\n%s\n' % db_master)

                if len(db_slave) != 0:
                        hostsfile.write('\n[db_slave]\n%s\n' % db_slave)

                hostsfile.write('\n[mysql_servers]\n%s\n' % db_master)
                if len(db_slave) != 0:
                        hostsfile.write('%s\n' % db_slave)

                if len(cldstk_web) != 0:
                        hostsfile.write('\n[cldstk_web]\n')
                        cldstk_web = cldstk_web.split(',')
                        for w in cldstk_web:
                                hostsfile.write('%s\n' % w.strip())

                if len(cldstk_kvmhost) != 0:
                        hostsfile.write('\n[cldstk_kvm]\n')
                        cldstk_kvmhost = cldstk_kvmhost.split(',')
                        for k in cldstk_kvmhost:
                                hostsfile.write('%s\n' % k.strip())

                hostsfile.close()
                print('ansible hosts file successfully writing to disk.....')

                # Write the vars_file.yml file
                if len(db_master) != 0:
                        vars_file = open('./ansible/vars_file.yml','w')
                        vars_file.write('master: %s\n' % db_master)
                        vars_file.write('slave: %s\n' % db_slave)
                        vars_file.write('cloud_repl_password: %s\n' % cloud_repl_password)
                        vars_file.write('mysql_root_password: %s\n' % mysql_root_password)
                        vars_file.write('nfs_server: %s\n' % nfs_server)
                        vars_file.write('nfs_path: %s\n' % nfs_path)
                        vars_file.close()
                else:
                        vars_file = open('./ansible/vars_file.yml','w')
                        vars_file.write('master: %s\n' % mgmt_master)
                        vars_file.write('slave: %s\n' % db_slave)
                        vars_file.write('cloud_repl_password: %s\n' % cloud_repl_password)
                        vars_file.write('mysql_root_password: %s\n' % mysql_root_password)
                        vars_file.write('nfs_server: %s\n' % nfs_server)
                        vars_file.write('nfs_path: %s\n' % nfs_path)
                        vars_file.close()

                print('vars_file successfully writing to disk.....')
                
                startinstallation = raw_input('Start installation now?[Y/n]: ')

                if startinstallation.lower() == 'y':
                        startall()
                else:
                        print('Exiting program......')
                        sys.exit()

        else:
                print('You must provide the Master Database Server...')
                main()




if __name__ == '__main__':
        if len(sys.argv) == 2 and sys.argv[1] == '-s':
                startnode()
                print('')
                print('Started webserver........')
                print('Browse to: http://localhost:3000')
                print('')
                sys.exit()
        elif len(sys.argv) == 2 and sys.argv[1] == '-S':
                stopnode()
                sys.exit()
        elif len(sys.argv) == 2 and sys.argv[1] == '-i':
                startnode()
                print('')
                print('Started webserver........')
                print('Browse to: http://localhost:3000')
                print('')
                startall()
                sys.exit()
        else:
                main()
