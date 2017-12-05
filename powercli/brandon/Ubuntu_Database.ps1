#param($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$VMName = "Ubuntu Database"
$VMMemory = 2
$VMCPU = 2
$VMAddress = '10.1.214.112'
#$VMAddress = 'any'
$OVFLocation = "C:\temp\Ubuntu (VMTools and Admin)\Ubuntu (VMTools and Admin).ovf"

.($PSScriptRoot + '\Default_Load_Vapp.ps1')($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$script = @"
sudo echo "America/Chicago" > /etc/timezone
sudo dpkg-reconfigure -f noninteractive tzdata
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 3306
sudo apt-get -y install zsh htop
sudo echo "mysql-server-5.7 mysql-server/root_password password root" | sudo debconf-set-selections
sudo echo "mysql-server-5.7 mysql-server/root_password_again password root" | sudo debconf-set-selections
sudo apt-get -y update
sudo apt-get -y install mysql-server-5.7
sudo mysql_secure_installation -D --password=root
sudo sed -i 's/127\.0\.0\.1/0\.0\.0\.0/g' /etc/mysql/my.cnf
sudo mysql --password=root -uroot -e 'USE mysql; UPDATE `user` SET `Host`="%" WHERE `User`="root" AND `Host`="localhost"; DELETE FROM `user` WHERE `Host` != "%" AND `User`="root"; FLUSH PRIVILEGES;'
sudo service mysql restart
"@
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $script