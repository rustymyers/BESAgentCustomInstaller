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
usage: bigfixCustomInstaller.py [-h] [--brand] [--settings]
                                [--custom URN GUID] [--package CUSTOM_PACKAGE]
                                [--distribute] [--removeoldpackages]
                                [--autogroup AUTO_GROUP] [--agentversion]
                                [--jamfpkg]

Build BESAgent Installers.

optional arguments:
  -h, --help            show this help message and exit
  --brand, -b           add branding text to the BESAgent pacakge -b, --brand
  --settings, -s        add custom settings cfg to the BESAgent pacakge -s,
                        --settings
  --custom URN GUID, -c URN GUID
                        create a installer for a custom division -c, --custom
                        <URN> <GUID>
  --package CUSTOM_PACKAGE, -p CUSTOM_PACKAGE
                        path to custom package to use -p, --package
                        [/path/to/package.pkg]
  --distribute, -d      distribute packages to share unit folders -d,
                        --distribute
  --removeoldpackages, -r
                        remove old packages from share unit folders -r,
                        --removeoldpackages
  --autogroup AUTO_GROUP, -a AUTO_GROUP
                        create a installer for a custom division (-c) with an
                        automatic group
  --agentversion, -v    Display version of agent being used -v, --agentversion
  --jamfpkg, -j         Create a package for Jamf (no site ID file) -j,
                        --jamfpkg
~~~~
