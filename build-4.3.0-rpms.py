#!/usr/bin/python

from subprocess import call,Popen, PIPE
import sys, os, commands

homedir = os.getcwd()

eth = 'eth0'
eth_ip = commands.getoutput("ip address show dev " + eth).split()
eth_ip = eth_ip[eth_ip.index('inet') + 1].split('/')[0]

with open("/etc/hosts", "a") as myfile:
    myfile.write(eth_ip + ' ' + os.environ['HOSTNAME'] + '\n')

buildcommand = """yum groupinstall "Development Tools" -y \n
yum install git ant ant-devel java-1.6.0-openjdk java-1.6.0-openjdk-devel mysql mysql-server tomcat6 mkisofs gcc python MySQL-python openssh-clients wget rpm-build ws-commons-util net-snmp genisoimage createrepo -y \n
wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz \n
cd /usr/local/ \n
tar -zxvf %s/apache-maven-3.0.5-bin.tar.gz \n
cd %s \n
mkdir -p public/cloudstack.apt-get.eu/rhel/4.3 \n
echo export M2_HOME=/usr/local/apache-maven-3.0.5 >> ~/.bashrc \n
echo export PATH=/usr/local/apache-maven-3.0.5/bin:${PATH} >> ~/.bashrc \n
wget http://apache.osuosl.org/cloudstack/releases/4.3.0/apache-cloudstack-4.3.0-src.tar.bz2 \n
tar -jxvf apache-cloudstack-4.3.0-src.tar.bz2 \n
source ~/.bashrc \n
cd apache-cloudstack-4.3.0-src/deps \n
./install-non-oss.sh
cd apache-cloudstack-4.3.0-src/packaging/centos63 \n
./package.sh# -p noredist
cd %s/apache-cloudstack-4.3.0-src/dist/rpmbuild/RPMS/x86_64
createrepo .
cp -rf * %s/public/cloudstack.apt-get.eu/rhel/4.3
cd %s
rm -rf apache-*
\n""" % (homedir, homedir, homedir, homedir, homedir)

open('buildrpms.sh', 'w').write(buildcommand)

call(["chmod","a+x", "buildrpms.sh"], shell=False)

call(["./buildrpms.sh"], shell=True)


