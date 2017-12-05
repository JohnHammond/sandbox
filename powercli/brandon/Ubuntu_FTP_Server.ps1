#param($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$VMName = "Ubuntu FTP Server"
$VMMemory = 2
$VMCPU = 2
$VMAddress = '10.1.214.160'
#$VMAddress = 'any'
$OVFLocation = "C:\temp\Ubuntu (VMTools and Admin)\Ubuntu (VMTools and Admin).ovf"

.($PSScriptRoot + '\Default_Load_Vapp.ps1')($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$Command = @"
sudo apt-get install vsftpd
sudo mkdir ~/Documents/ftp
sudo touch ~/Documents/ftp/helloworld.txt
sudo sh -c `"echo local_root=/home/sandbox/Documents/ftp >> /etc/vsftpd.conf`"
sudo sh -c `"echo write_enable=YES >> /etc/vsftpd.conf`"
sudo systemctl restart vsftpd
"@

Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $Command