Param($VMName)

If ( (Get-VM $VMName).Guest.OSFullName -Match "Windows" ){
	echo "This machine is running Windows. Don't want to bother with conpot!"
}Else{

$script_text = @"
sudo apt-get -y install libsmi2ldbl snmp-mibs-downloader python-dev libevent-dev libxslt1-dev libxml2-dev libmysqlclient-dev python-pip
sudo pip install conpot
sudo pip uninstall -y bacpypes
pip install -Iv https://github.com/JoelBender/bacpypes/archive/v0.13.8.tar.gz
"@

(Invoke-VMScript -VM $VMName -GuestUser sandbox -GuestPassword S@ndb0x -ScriptType Bash -ScriptText $script_text).ScriptOutput

}