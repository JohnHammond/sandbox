#!/bin/bash

# This script should be run AFTER PowerShell Core has been installed.

POWERCLI_DIRECTORY="powercli_core"
POWERCLI_ZIP="PowerCLI_Core.zip"

# Create a directory to work in...
mkdir -p $POWERCLI_DIRECTORY

# Save your current spot, and move to the new folder.
pushd
cd $POWERCLI_DIRECTORY

curl "https://download3.vmware.com/software/vmw-tools/powerclicore/PowerCLI_Core.zip" > $POWERCLI_ZIP

unzip -o $POWERCLI_ZIP

# Ensure we have the most recent OpenSSL installation
brew install openssl
brew install curl --with-openssl

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
# rm -r $POWERCLI_DIRECTORY
