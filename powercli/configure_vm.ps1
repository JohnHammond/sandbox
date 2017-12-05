Param($VMName, $IPAddress, $VMCPU, $VMMemory)


Set-VM $VMName -NumCpu $VMCPU -MemoryGB $VMMemory -Confirm:$false -ErrorAction SilentlyContinue| Out-Null
Start-VM $VMName -ErrorAction SilentlyContinue | Out-Null
Wait-Tools -VM $VMName | Out-Null

If ( (Get-VM $VMName).Guest.OSFullName -Match "Windows" ){
	
	$script_text = @" 
netsh interface ipv4 set address name="Ethernet0" static $IPAddress 255.255.255.0 10.1.214.1
netsh interface ipv4 set dns name="Ethernet0" static 8.8.8.8
"@

	(Invoke-VMScript -VM $VMName -GuestUser Administrator -GuestPassword S@ndb0x -ScriptType Powershell -ScriptText $script_text).ScriptOutput

}else{
	If ( (Get-VM $VMName).Guest.OSFullName -Match "Linux" ){
	
		$interface_name=((Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword S@ndb0x -ScriptType Bash -ScriptText "sudo ifconfig | head -n1 | cut -d ' ' -f1").ScriptOutput).Replace("`n","")
		
		$script_text = @" 
sudo ifconfig $interface_name $IPAddress
sudo ifconfig $interface_name netmask 255.255.255.0
sudo route add default gw 10.1.214.1
sudo bash -c "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"
"@

	(Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword S@ndb0x -ScriptType Bash -ScriptText $script_text).ScriptOutput	

	}
}