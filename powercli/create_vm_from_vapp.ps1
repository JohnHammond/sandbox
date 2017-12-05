Param($VMName, $VMMemory, $VMCPU, $VMAddress, $OVFLocation)

#Currently connecting to cluster
# Connect-VIServer -Server "10.1.214.223" -user administrator@vsphere.local -password S@ndbox2

<# # for debugging...
echo $VMName
echo "$VMMemory GB RAM Requested"
echo "$VMCPU CPUs Requested"
echo "I.P. Address $VMAddress Requested"
echo "VAPP Location: $OVFLocation"
#>

#Smart Select Host
#$VMHost = . ($PSScriptRoot + '\smart_select_vmhost.ps1')
$VMHost = Get-VMHost '10.1.214.222'
$OVFLocation = (Get-ChildItem $OVFLocation).ToString()

$VMLocation = Get-Cluster | Select -First 1

$VMHost | Import-vApp -Source $OVFLocation -Location $VMLocation -Name $VMName -Confirm:$false -WarningAction SilentlyContinue | Out-Null 

New-AdvancedSetting isolation.tools.copy.disable $false -Entity $VMName -Confirm:$false -WarningAction SilentlyContinue | Out-Null
New-AdvancedSetting isolation.tools.paste.disable $false -Entity $VMName -Confirm:$false -WarningAction SilentlyContinue | Out-Null

echo "VM creation complete."
#Set-VM -Name $VMName -NumCpu $VMCPU -MemoryGB $VMMemory

#Start-VM $VMName