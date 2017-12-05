# ---------------------------------------------------------------------------
# Author:  John Hammond
# Date:    29AUG17
# Purpose: This script is to act as POC code to deploy a new virtual machine
#          on the ESXi server with a given ISO file and using PowerCLI.
#
# ---------------------------------------------------------------------------



# We get the datastore name because we need it to specify the ISO we want later
$datastore_name = (Get-Datastore | Select -First 1).Name


# THIS IS BAD AND NEEDS TO BE FIXED
# But this is the proof of concept, so we'll deal
# We need the path of the local ISO file. I'll use Windows 7 as an example.
#$local_iso_path = "C:\Users\Capstone\isos\ubuntu-16.04.2-desktop-amd64.iso"
#$local_iso_path = "C:\Users\Capstone\isos\en_windows_7_enterprise_x64_dvd_x15-70749.iso"
#$local_iso_path = "C:\Users\Capstone\isos\windows_server_2016_EVALUATION.ISO"
#$local_iso_path = "C:\Users\Capstone\isos\Windows 7 Ultimate SP1  32 Bit.iso"
#$local_iso_path = "C:\Users\Capstone\isos\Windows10x64_1607.iso"
#$local_iso_path = "C:\Users\Capstone\isos\CentOS-7-x86_64-Everything-1611.iso"
#$local_iso_path = "C:\Users\Capstone\isos\Windows_XP_Professional_SP3_Nov_2013_Incl_SATA_Drivers.iso"
#$local_iso_path = "C:\Users\Capstone\isos\windows_server_2012_EVALUATION.ISO"
$local_iso_path = "C:\Users\Capstone\isos\kali-linux-2017.2-i386.iso"
$local_iso_path = "C:\Users\Capstone\isos\ubuntu-16.04.3-server-amd64.iso"
$local_iso_file = ls $local_iso_path
$local_iso_filename = $local_iso_file.PSChildName


# This is the default path on all ESXi installations.
# The 'vmstore' is a PowerShell Drive that PowerCLi created for us.
$destination_folder = "vmstore:\ha-datacenter\datastore1\isos\"
mkdir -Force $destination_folder

$destination_path = "$destination_folder\$local_iso_filename"

if ( Test-Path $destination_path ){
    
    # This means that the file has already been uploaded... 
    # so we don't have to do it again!
    Write-Host -Foreground Cyan "This .ISO has already been uploaded!"

}else{
    # Actually upload the iso...
    Copy-DatastoreItem -Item $local_iso_file -Destination $destination_path -PassThru
}

$esxi_iso_path="[$datastore_name]\isos\$local_iso_filename"

# Now that we have an ISO uploaded, we can create a new VM.
# -DiskGB is harddrive space in GB
# -MemoryGB is RAM

$vm_name="Ubuntu Server"
New-VM -Name $vm_name -DiskGB 50 -MemoryGB 1 | Out-Null
New-ScsiController -HardDisk (Get-HardDisk $vm_name) -Type VirtualLsiLogicSAS
New-CDDrive -VM $vm_name

Start-VM $vm_name | Out-Null

Get-CDDrive -VM $vm_name | Set-CDDrive -IsoPath $esxi_iso_path `
                           -StartConnected $true -Connected $true -Confirm:$false

Restart-VM $vm_name -Confirm:$false
Open-VMConsoleWindow $vm_name

Disconnect-VIServer -Confirm:$false

#>