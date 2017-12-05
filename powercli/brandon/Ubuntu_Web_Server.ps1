#param($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$VMName = "Ubuntu Web Server"
$VMMemory = 2
$VMCPU = 2
$VMAddress = '10.1.214.162'
#$VMAddress = 'any'
$OVFLocation = "C:\temp\Ubuntu (VMTools and Admin)\Ubuntu (VMTools and Admin).ovf"

.($PSScriptRoot + '\Default_Load_Vapp.ps1') $VMName $VMMemory $VMCPU $VMAddress $OVFLocation

Copy-VMGuestFile -Source ("$PSScriptRoot\Resources\index.html") -Destination /home/sandbox/Documents/ -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force
Copy-VMGuestFile -Source ("$PSScriptRoot\Resources\contact.html") -Destination /home/sandbox/Documents/ -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force
Copy-VMGuestFile -Source ("$PSScriptRoot\Resources\sponsor.html") -Destination /home/sandbox/Documents/ -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force
Copy-VMGuestFile -Source ("$PSScriptRoot\Resources\banner.png") -Destination /home/sandbox/Documents/ -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force

$apachescript = @"
sudo apt-get install -y apache2
sudo cp -a /home/sandbox/Documents/. /var/www/html/
sudo service apache2 restart
"@
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $apachescript

Start-Sleep -Seconds 5
$IE=new-object -com internetexplorer.application
$IE.navigate2("10.1.214.162")
$IE.visible=$true