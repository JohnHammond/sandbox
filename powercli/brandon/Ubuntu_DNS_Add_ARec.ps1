param($ArecordIP, $ArecordName, $VMName)

# We need PowerCLI to do really anything.
Import-Module C:\Users\Capstone\Documents\WindowsPowerShell\Modules\VMware.PowerCLI\6.5.2.6268016\VMware.PowerCLI.psd1

# Currently connecting to cluster
Connect-VIServer -Server "10.1.214.223" -user administrator@vsphere.local -password S@ndbox2

$ArecordIP = '10.1.214.211';
$ArecordName = 'sandbox.local'
$VMName = 'Ubuntu DNS'

$datastore_name = (Get-Datastore | Sort | Select -First 1).Name
$OVFLocation = "C:\temp\Ubuntu (VMTools and Admin)\Ubuntu (VMTools and Admin).ovf"
$workPath = "C:\Users\Capstone\"

$VMHost = (Get-VMHost | Sort | Select -First 1)

$workPath = ($PSScriptRoot + '\Resources\')

#Retrieve Conf File
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo mv /etc/bind/named.conf.local /home/sandbox/Documents/named.conf.local"
Copy-VMGuestFile -Destination $workPath -Source /home/sandbox/Documents/named.conf.local -VM $VMName -GuestToLocal -GuestUser sandbox -GuestPassword sandbox -Force

#Edit Conf File
$NewARec = @"
zone "name.name" {

    type master;

    file "/etc/bind/zones/master/db.name.name";

};
"@

$NewerARec = $NewARec -replace "name.name", $ArecordName
Add-Content -Path ($workPath + "named.conf.local") -Value $NewerARec

#Send New Conf File
Wait-Tools -VM $VMName
Copy-VMGuestFile -Source ($workPath + "named.conf.local") -Destination /home/sandbox/Documents -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo mv /home/sandbox/Documents/named.conf.local /etc/bind/named.conf.local"

#Delete Evidence
Remove-Item -Path ($workPath + "named.conf.local")

#Build New A-Rec File
$aRecPath = $workPath + "db.sandboxroolz.org.sbx"
$aRecPathFinal = $workPath + "db." + $ArecordName
$content2 = [IO.File]::ReadAllText($aRecPath)
$NewContent2 = $content2 -replace "sandboxroolz.org", $ArecordName -replace "99.99.99.99", $ArecordIP
New-Item -Path $aRecPathFinal -Value $NewContent2

#Send New A-Record File
Wait-Tools -VM $VMName
Copy-VMGuestFile -Source $aRecPathFinal -Destination /home/sandbox/Documents -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force

$command1 = "sudo mv /home/sandbox/Documents/db." + $ArecordName + " /etc/bind/zones/master/db." + $ArecordName
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $command1

Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo /etc/init.d/bind9 restart"

#Delete Evidence
Remove-Item -Path $aRecPathFinal

#Resolve-DnsName -Name "www.sandboxroolz.org" -Server 10.1.214.201