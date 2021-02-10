# BESAgentCustomInstaller

This tool builds BESAgent packages with "division" and "automatic group" files. The provisioning in BigFix utilizes these divisions and automatic group files to determine the site and group membership.
Your environment may not utlize these files, in which case you should leave them empty.

Instructions: 

1. Add stock BESAgent installer to root folder.
1. If you want to include clientsettings.cfg in the custom pacakge, add it to the ModifiedFiles folder and use the -s flag.
1. Run ./customBESAgentPkg.py

* The tool will attempt to connect to your BES Root Server to get the latest actionsite. If that fails, add an actionsite.afxm to ModifiedFiles folder
* Adding a brand can be done by editing the "name" variable in the customBESAgentPkg.py script and using the -b flag.

~~~~
usage: customBESAgentPkg.py [-h] [--brand CUSTOM_BRAND] [--settings]
                            [--package CUSTOM_PKG]

Build Custom BESAgent Installers.

optional arguments:
  -h, --help            show this help message and exit
  --brand CUSTOM_BRAND, -b CUSTOM_BRAND
                        add branding text to the BESAgent pacakge
  --settings, -s        add custom settings cfg to the BESAgent pacakge
  --package CUSTOM_PKG, -p CUSTOM_PKG
                        specify the BESAgent pacakge to use
  --custom, -c          --custom <URN> <GUID>
                        create a installer for a custom division -c
  --distribute, -d      distribute packages to share unit folders
  
  --removeoldpackages, -r
                        remove old packages from share unit folders
  --autogroup, -a       create a installer for a custom division (-c) with an automatic group
  
  --jamfpkg, j          Create a package for Jamf (no site ID file)
~~~~ 
