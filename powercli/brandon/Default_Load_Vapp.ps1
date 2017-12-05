param($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

#We need PowerCLI to do really anything.
Import-Module C:\Users\Capstone\Documents\WindowsPowerShell\Modules\VMware.PowerCLI\6.5.2.6268016\VMware.PowerCLI.psd1

#Currently connecting to cluster
Connect-VIServer -Server "10.1.214.223" -user administrator@vsphere.local -password S@ndbox2

echo $VMName
echo "$VMMemory GB RAM Requested"
echo "$VMCPU CPUs Requested"
echo "I.P. Address $VMAddress Requested"
echo "VAPP Location: $OVFLocation"

#Smart Select Host
$VMHost = . ($PSScriptRoot + '\smart_select_vmhost.ps1')

$VMLocation = Get-Cluster | Select -First 1

$VMHost | Import-vApp -Source $OVFLocation -Location $VMLocation -Name $VMName -Confirm:$false

New-AdvancedSetting isolation.tools.copy.disable $false -Entity $VMName -Confirm:$false
New-AdvancedSetting isolation.tools.paste.disable $false -Entity $VMName -Confirm:$false

#Set-VM -Name $VMName -NumCpu $VMCPU -MemoryGB $VMMemory

Start-VM $VMName

Start-Sleep -Seconds 30
Wait-Tools -VM $VMName
Wait-Tools -VM $VMName

$script = @"
sudo rm -f /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock
sudo rm -f /var/lib/dpkg/lock
sudo dpkg --configure -a
"@
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $script


If ($VMAddress -ne 'any')
{
$content = [IO.File]::ReadAllText($PSScriptRoot + '\Resources\interfaces.sbx')
$content = $content.Replace("x.x.x.x", $VMAddress)
New-Item ($PSScriptRoot + '\Resources\interfaces') -ItemType file -Value $content
Copy-VMGuestFile -Source  ($PSScriptRoot + '\Resources\interfaces') -Destination /home/sandbox/Documents/ -VM $VMName -LocalToGuest -GuestUser sandbox -GuestPassword sandbox -Force
Remove-Item -Path ($PSScriptRoot + '\Resources\interfaces')

$networkScript = @"
sudo ifdown --force ens32
sudo mv /home/sandbox/Documents/interfaces /etc/network/interfaces
sudo ifup ens32
sudo service networking restart
sudo ifdown --force ens32
sudo ifup ens32
"@
Wait-Tools -VM $VMName
Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword sandbox -ScriptType Bash -ScriptText $networkScript

Restart-VM $VMName -Confirm:$false
Start-Sleep -Seconds 20
}