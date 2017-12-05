#param($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation, $ArecordIP, $ArecordIP2, $ArecordName)

$VMName = "Ubuntu DNS"
$VMMemory = 2
$VMCPU = 2
$VMAddress = '10.1.214.203'
#$VMAddress = 'any'
$OVFLocation = "C:\temp\Ubuntu (VMTools and Admin)\Ubuntu (VMTools and Admin).ovf"

#Set A-Record Values
$ArecordIP = "10.1.214.133"
$ArecordIP2 = "10.1.214.134"
$ArecordName = "sandboxroolz.org"

#Create The VM
.($PSScriptRoot + '\Default_Load_Vapp.ps1')($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

$workPath = ($PSScriptRoot + '\Resources\')

Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo apt-get install -y bind9 dnsutils"
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo mkdir /etc/bind/zones"
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo mkdir /etc/bind/zones/master"

$workPath = "C:\Users\Capstone\"

#Build A-Record Config File
$confPath = $workPath + "named.conf.local.sbx"
$confPathFinal = $workPath + "named.conf.local"
$content1 = [IO.File]::ReadAllText($confPath)
$NewContent1 = $content1 -replace "sandboxroolz.org", $ArecordName
New-Item -Path $confPathFinal -Value $NewContent1

#Build A-Record File
$aRecPath = $workPath + "db.sandboxroolz.org.sbx"
$aRecPathFinal = $workPath + "db." + $ArecordName
$content2 = [IO.File]::ReadAllText($aRecPath)
$NewContent2 = $content2 -replace "sandboxroolz.org", $ArecordName -replace "99.99.99.99", $ArecordIP -replace "99.99.99.98", $ArecordIP2
New-Item -Path $aRecPathFinal -Value $NewContent2

#Send A-Record Config File
Wait-Tools -VM $VMName
Copy-VMGuestFile -Source ($PSScriptRoot + 'named.conf.local') -Destination /home/sandbox/Documents -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo mv /home/sandbox/Documents/named.conf.local /etc/bind/named.conf.local"

#Send A-Record File
Wait-Tools -VM $VMName
Copy-VMGuestFile -Source $aRecPathFinal -Destination /home/sandbox/Documents -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force
$command1 = "sudo mv /home/sandbox/Documents/db." + $ArecordName + " /etc/bind/zones/master/db." + $ArecordName
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $command1

#Restart Bind
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText "sudo /etc/init.d/bind9 restart"

#Delete Evidence
Remove-Item -Path ($PSScriptRoot + 'named.conf.local')
Remove-Item -Path $aRecPathFinal