#!/usr/bin/python

from subprocess import call,Popen, PIPE
import sys, os, commands

homedir = os.getcwd()

buildcommand = """yum groupinstall "Development Tools" -y \n
yum install git ant ant-devel java-1.7.0-openjdk java-1.7.0-openjdk-devel mysql mysql-server tomcat6 mkisofs gcc python MySQL-python openssh-clients wget rpm-build ws-commons-util net-snmp net-snmp-devel genisoimage createrepo -y \n
mkdir -p public/cloudstack.apt-get.eu/rhel/4.5 \n
wget http://www.us.apache.org/dist/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz \n
cd /usr/local/ \n
tar -zxvf %s/apache-maven-3.0.5-bin.tar.gz \n
cd %s \n
echo export M2_HOME=/usr/local/apache-maven-3.0.5 >> ~/.bashrc \n
echo export JAVA_HOME=/usr/lib/jvm/java-1.7.0 >> ~/.bashrc \n
echo export PATH=/usr/local/apache-maven-3.0.5/bin:${PATH} >> ~/.bashrc \n
source ~/.bashrc \n
wget http://apache.osuosl.org/cloudstack/releases/4.5.1/apache-cloudstack-4.5.1-src.tar.bz2 \n
tar -jxvf apache-cloudstack-4.5.1-src.tar.bz2 \n
#cd apache-cloudstack-4.5.1-src \n
#rm -f ./server/test/org/apache/cloudstack/network/lb/CertServiceTest.java \n
#rm -f ./dist/rpmbuild/BUILD/cloudstack-4.5.1-SNAPSHOT/server/test/org/apache/cloudstack/network/lb/CertServiceTest.java \n
#rm -f ./dist/rpmbuild/SOURCES/cloudstack-4.5.1-SNAPSHOT/server/test/org/apache/cloudstack/network/lb/CertServiceTest.java \n
cd apache-cloudstack-4.5.1-src/deps \n
#wget http://www.thehyperadvisor.com/cloudstack/build-dep/cloud-iControl.jar \n
#wget http://www.thehyperadvisor.com/cloudstack/build-dep/manageontap.jar \n
#wget http://www.thehyperadvisor.com/cloudstack/build-dep/vim.jar \n
#wget http://www.thehyperadvisor.com/cloudstack/build-dep/vim25_51.jar \n
#wget http://www.thehyperadvisor.com/cloudstack/build-dep/apputils.jar \n
./install-non-oss.sh \n
cd ../packaging/centos63 \n
./package.sh
cd %s/apache-cloudstack-4.5.1-src/dist/rpmbuild/RPMS/x86_64/ \n
createrepo . \n
cp -rf * %s/public/cloudstack.apt-get.eu/rhel/4.5 \n
cd %s \n
#rm -rf apache-* \n
\n""" % (homedir, homedir, homedir, homedir, homedir)

open('buildrpms.sh', 'w').write(buildcommand)

call(["chmod","a+x", "buildrpms.sh"], shell=False)

call(["./buildrpms.sh"], shell=True)




