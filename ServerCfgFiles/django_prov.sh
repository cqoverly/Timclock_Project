#!/usr/bin/env bash

PGSQL_VERSION=9.1
PROJECT='Timeclock'
PROJECT_ENV='TimeclockEnv'

apt-get update && apt-get upgrade

#python tools
apt-get install -y build-essential python python2.7-dev python-setuptools python-pip

pip install virtualenv


#apach2
apt-get install -y apache2 libapache2-mod-wsgi
rm -rf /var/www
ln -fs /vagrant /var/www
cp /vagrant/ServerCfgFiles/default /etc/apache2/sites-available/default
service apache2 restart

# change locale setting so postgres encodes UTF-8
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale-gen en_US.UTF-8
dpkg-reconfigure locales

# postgres
apt-get install -y postgresql-$PGSQL_VERSION postgresql-contrib-$PSQL_VERSION libpq-dev

#set up virtualenv for django project
cd /home/vagrant
virtualenv $PROJECT_ENV

#turn on virtualenv and install dependencies.
source /home/vagrant/$PROJECT_ENV/bin/activate
pip install -r /vagrant/requirements.txt



