#!/bin/bash

# Add support for colors...
export RED=`tput setaf 1`
export GREEN=`tput setaf 2`
export YELLOW=`tput setaf 3`
export BLUE=`tput setaf 4`
export MAGENTA=`tput setaf 5`
export CYAN=`tput setaf 6`
export BOLD=`tput bold`
export UNDERLINE=`tput smul`
export RESET=`tput sgr0`

# ----------------------------------------------------------

# Determine the OS, so we can handle any kind of machine in one single
# install script.

if [ `uname -s` == "Darwin" ]; then
	OS="mac"
elif [ `uname -s` == "Linux" ]; then
	OS="linux"
fi

function install_homebrew(){
	echo "${CYAN}Installing Homebrew... ${RESET}"
	echo "" | /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
}

function install_powershell(){

	echo "${CYAN}Installing PowerShell... ${RESET}"

	# Instructions found here:
	# https://github.com/PowerShell/PowerShell/blob/master/docs/installation/linux.md#macos-1012

	# DO NOT USE THE BETA VERSION. I HAVE HAD THE MOST SUCCESS WITH ALPHA.17

	if [ $OS == "mac" ]; then
		# Grab a command-line downloader (curl would not grab the right thing)
		brew install wget

		# Download the installer
		POWERSHELL_PACKAGE="powershell-6.0.0-alpha.17.pkg"
		if [ ! -e $POWERSHELL_PACKAGE ]
		then
			wget "https://github.com/PowerShell/PowerShell/releases/download/v6.0.0-alpha.17/powershell-6.0.0-alpha.17.pkg"
		fi
		# Install the package.
		sudo installer -pkg $POWERSHELL_PACKAGE -target /
		# Clean up.
		rm $POWERSHELL_PACKAGE
	elif [ $OS == "linux" ]; then


		POWERSHELL_PACKAGE="powershell_6.0.0-alpha.17-1ubuntu1.16.04.1_amd64.deb"
		if [ ! -e $POWERSHELL_PACKAGE ]
		then
			wget "https://github.com/PowerShell/PowerShell/releases/download/v6.0.0-alpha.17/powershell_6.0.0-alpha.17-1ubuntu1.16.04.1_amd64.deb"
		fi

		# Install the package.
		sudo dpkg -i $POWERSHELL_PACKAGE
		#sudo apt -y install -f

		# Clean up.
		rm $POWERSHELL_PACKAGE
		# Run powershell as `pwsh` for Linux.
	fi
}


function install_powercli(){

	# This  should be run AFTER PowerShell Core has been installed.
	echo "${CYAN}Installing VMware PowerCLI...${RESET}"

	POWERCLI_DIRECTORY="powercli_core"
	POWERCLI_ZIP="PowerCLI_Core.zip"

	# Create a directory to work in...
	mkdir -p $POWERCLI_DIRECTORY

	# Save your current spot, and move to the new folder.
	pushd
	cd $POWERCLI_DIRECTORY

	
	curl "https://download3.vmware.com/software/vmw-tools/powerclicore/PowerCLI_Core.zip" > $POWERCLI_ZIP

	unzip -o $POWERCLI_ZIP

	# Create the modules for our PowerShell installation...
	mkdir -p ~/.local/share/powershell/Modules

	# Place all the necessary files in the Modules path.
	unzip -o PowerCLI_Core.zip -d ~/.local/share/powershell/Modules
	unzip -o PowerCLI.ViCore.zip -d ~/.local/share/powershell/Modules
	unzip -o PowerCLI.Cis.zip -d ~/.local/share/powershell/Modules
	unzip -o PowerCLI.Vds.zip -d ~/.local/share/powershell/Modules

	# All done! Move back to where you are.
	popd

	# When you are done testing, uncomment this line to clean up the directory.
	rm -r $POWERCLI_DIRECTORY

	if [ $OS == 'mac' ]; then
		# Ensure we have the most recent OpenSSL installation
		brew install openssl
		brew install curl --with-openssl
	fi

}

function setup_powercli(){

	echo "${CYAN}Setting up VMware PowerCLI...${RESET}"
	powershell -Command "Get-Module -ListAvailable PowerCLI* | Import-Module; Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:\$false"
}

function install_gtk(){

	echo "${CYAN}Installing GTK and Glade (if you are on Ubuntu, this may take 10+ minutes)...${RESET}"
	if [ $OS == 'mac' ]; then

		brew install pygtk
		mkdir -p ~/Library/Python/2.7/lib/python/site-packages
		echo 'import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")' >> ~/Library/Python/2.7/lib/python/site-packages/homebrew.pth
		brew install gtk+3
		brew install glade
		brew install pygobject3

	elif [ $OS == 'linux' ]; then
		### Ubuntu 16.04 comes with GTK 3.18, but the GTK and Glade on Mac
		### is installed to 3.21... so we should upgrade like so:
		# https://askubuntu.com/questions/933010/how-to-upgrade-gtk-3-18-to-3-20-on-ubuntu-16-04/955980
		# echo "" | sudo add-apt-repository ppa:gnome3-team/gnome3-staging
		# echo "" | sudo add-apt-repository ppa:gnome3-team/gnome3
		# sudo apt update
		# sudo apt dist-upgrade

		# ## We will need to be able to import gi in Python, and the latest glade
		# ## (an updated intltool & libxml2 is needed to build glade)
		# sudo apt -y install python-gi-dev intltool libxml2-dev itstool libxml2-utils xsltproc

		# # Now get the latest glade...
		# wget "http://ftp.gnome.org/pub/GNOME/sources/glade/3.20/glade-3.20.0.tar.xz"
		# unxz glade-3.20.0.tar.xz
		# tar xvf glade-3.20.0.tar
		# cd glade-3.20.0
		# # Ensure you do not build the manpages, because one online does not
		# # exist and then it breaks everything
		# ./configure --enable-man-pages=no
		# sudo make
		# sudo make install
		# cd ..

		sudo apt -y install python-gi-dev glade
	fi

}

function main(){

	if [ $OS  == "mac" ]; then
		install_homebrew
	elif [ $OS == 'linux' ] ; then
		# Just for general success across the scripts..
		sudo apt -y install curl
	fi

	install_powershell
	install_powercli
	setup_powercli
	install_gtk

}

main 