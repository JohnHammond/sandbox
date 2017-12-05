Param($VMName, $IPAddress)


$script_text = @" 
netsh interface ipv4 set address name="Ethernet0" static $IPAddress 255.255.255.0 10.1.214.1
netsh interface ipv4 set dns name="Ethernet0" static 8.8.8.8
"@

(Invoke-VMScript -VM $VMName -GuestUser Administrator -GuestPassword S@ndb0x -ScriptType Powershell -ScriptText $script_text).ScriptOutput