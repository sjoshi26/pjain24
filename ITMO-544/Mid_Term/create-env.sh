sudo apt-get -y update
sudo apt-get -y install apache2

sudo systemctl enable apache2
sudo systemctl start apache2

sudo apt-get -y install php 
# make sure libapache2-mod-php7.2 is there
sudo apt-get -y install php php-gd mysql-server php-mysql php-mysql mysql-server simplexml php7.2.xml
#library for image processing 


sudo apt-get -y install simplexml php7.2.xml