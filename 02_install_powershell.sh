#!/bin/bash

# Instructions found here:
# https://github.com/PowerShell/PowerShell/blob/master/docs/installation/linux.md#macos-1012

# DO NOT USE THE BETA VERSION. I HAVE HAD THE MOST SUCCESS WITH ALPHA.


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
