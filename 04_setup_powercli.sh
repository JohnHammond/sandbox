#!/bin/bash


# Run this AFTER both PowerShell and PowerCLI have been installed.

powershell -Command "Get-Module -ListAvailable PowerCLI* | Import-Module; Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:\$false"
