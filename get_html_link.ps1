
## $VMName must be supplied 



$VM = Get-VM -Name $VMName
$VMMoref = $VM.ExtensionData.MoRef.Value


$VCInstanceUUID = $global:DefaultVIServer.InstanceUuid
$VCName = $global:DefaultVIServer.Name
$SessionMgr = Get-View $DefaultViserver.ExtensionData.Content.SessionManager
$Ticket = $SessionMgr.AcquireCloneTicket()
$URL = "https://$VCName`:9443/vsphere-client/webconsole.html?vmId=$VMMoref&vmName=$VMname&serverGuid=$VCInstanceUUID&locale=en_US&host=$VCName`:443&sessionTicket=$Ticket"

echo $URL
