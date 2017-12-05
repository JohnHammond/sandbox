#param($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$VMName = "Ubuntu Email Server"
$VMMemory = 2
$VMCPU = 2
$VMAddress = '10.1.214.211'
#$VMAddress = 'any'
$OVFLocation = "C:\temp\Ubuntu (VMTools and Admin)\Ubuntu (VMTools and Admin).ovf"


.($PSScriptRoot + '\Default_Load_Vapp.ps1')($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$script = @"
sudo debconf-set-selections <<< "postfix postfix/mailname string sandbox.local"
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
sudo apt-get install -y postfix
sudo mv /home/sandbox/Documents/hosts /etc/hosts
"@
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $script
Open-VMConsoleWindow $VMName
Restart-VM -VM $VMName -Confirm:$false

#sudo gedit /var/log/mail.log
#echo "hello!" | sudo sendmail sandbox@sandbox.local
#sudo gedit /etc/postfix/main.cf
#sudo hostnamectl set-hostname mail.sandbox.local