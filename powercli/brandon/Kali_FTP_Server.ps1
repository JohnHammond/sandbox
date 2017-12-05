# We need PowerCLI to do really anything.
Import-Module C:\Users\Capstone\Documents\WindowsPowerShell\Modules\VMware.PowerCLI\6.5.2.6268016\VMware.PowerCLI.psd1

# Currently connecting to cluster
Connect-VIServer -Server "10.1.214.223" -user administrator@vsphere.local -password S@ndbox2

$datastore_name = (Get-Datastore | Sort | Select -First 1).Name
$local_ovf_file = "C:\temp\Kali Linux\Kali Linux.ovf"
$vmname = "Kali FTP"

$vmhost = (Get-VMHost | Sort | Select -First 1)
$vmhost | Import-vApp -Source $local_ovf_file -Datastore $datastore_name -Name $vmname

Start-VM -VM $vmname

# Creates vsftpd server at 10.1.214.xxx

Wait-Tools -VM $vmname
Wait-Tools -VM $vmname
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo rm -f /var/lib/apt/lists/lock"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo rm /var/cache/apt/archives/lock"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo rm -f /var/lib/dpkg/lock"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo dpkg --configure -a"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText  "sudo ifconfig eth0 10.1.214.161"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText  "sudo ifconfig eth0 netmask 255.255.255.0"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText  "sudo route add default gw 10.1.214.1"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo apt-get install vsftpd"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo mkdir -p /root/Documents/ftp"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo touch /root/Documents/ftp/helloworld.txt"
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo sh -c `"echo local_enable=NO >> /etc/vsftpd.conf`""
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo sh -c `"echo anonymous_enable=YES >> /etc/vsftpd.conf`""
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo sh -c `"echo write_enable=YES >> /etc/vsftpd.conf`""
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo sh -c `"echo anon_root=/root/Documents/ftp >> /etc/vsftpd.conf`""
Wait-Tools -VM $vmname
Invoke-VMScript -VM $vmname -GuestUser root -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo systemctl restart vsftpd"

