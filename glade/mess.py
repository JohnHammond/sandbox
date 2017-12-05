#!/usr/bin/env python

import os
import glob

print os.getcwd()
print [  os.path.basename(x) for x in glob.glob('../powercli/provision/*.ps1') ] 
