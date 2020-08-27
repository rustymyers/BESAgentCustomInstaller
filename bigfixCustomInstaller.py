#!/usr/bin/python
#--------------------------------------------------------------------------------------------------
#-- BigFix Custom Installer
#--------------------------------------------------------------------------------------------------
# Program    : BigFix Custom Installer
# To Complie : n/a
#
# Purpose    : 
#
# Called By  :
# Calls      :
#
# Author     : Rusty Myers <rustymyers@gmail.com>
# Based Upon :
#
# Note       : 
#
# Revisions  : 
#           2016-01-25 <rzm102>   Initial Version
#
# Version    : 1.0
#--------------------------------------------------------------------------------------------------


import sys, glob, os, re, shutil, argparse, subprocess
import urllib2 as url
import xml.etree.ElementTree as ET

# Get XML of different untis to build packages for
units_url = "https://api.example.com/"
# Set your signing certificate
signing_cert='Developer ID Installer: Example Company (ufwhuhef8h3))'
# Set your bigfix root server to get latest mastehead
bigfix_root_server = 'http://bigfix.server.com:52311/masthead/masthead.afxm'

# Function to download all  division IDs and Names. Stores in Dict
def loadUnits(url):
    subdivname = ""
    subdivisions = []
    # Clear out any existing values
    Divs.clear()
    # Store results in var
    # units = url.urlopen(url)
    # <Menu>
    # <Division URN="EX" Name="Example IT Group" GUID="8057E28C-1F4A-4128-BDB8-C0683D6E2C05"/>
    # <Division URN="EX/AMPLE" Name="Example SUB Group" GUID="3DE2B3B6-569F-453A-9D58-9896952F66B5"/>
    # </Menu>
    units = '''<?xml version="1.0"?><Menu>
<Division URN="EX" Name="Example IT Group" GUID="8057E28C-1F4A-4128-BDB8-C0683D6E2C05"/>
<Division URN="EX/AMPLE" Name="Example SUB Group" GUID="3DE2B3B6-569F-453A-9D58-9896952F66B5"/>
</Menu>'''
    # Grab tree and root of XML
    # tree = ET.parse(units)
    root = ET.fromstring(units)
    # root = tree.getroot()
    # Grab name and guid from root
    for child in root:
        subdivname = ""
        subdivisions = []
        # Store URN in name without /
        name = child.get('URN').replace('/','-')
        # Store GUID
        guid = child.get('GUID')
        # Try to get subdiv
        for subdiv in child:
            # Store sub division
            subdivname = subdiv.get('FileName')
            subdivisions.append(subdivname)
        # Add to dict
        Divs[name] = [guid, subdivisions]

# Function to remove 'relocate' tags
# This forces installer to place files in correct location on disk
def derelocatePacakge(distroPath):
    # Open Distribution file passed to function
    tree = ET.parse(distroPath)
    # Get the root of the tree
    root = tree.getroot()
    # Should we add replocate?
    relocate_pkg_ref = False
    # Check each child
    for child in root:
        # If it's a pkg-ref
        # print "child: {}".format(child)
        if child.tag == "relocate":
            # Remove the whole child
            root.remove(child)
    # Remove old Distribution file
    os.remove(distroPath)
    # Write new Distribution file
    tree.write(distroPath)

# Function to sign packages
def signPackage(pkg, cert):
    # rename unsigned package so that we can slot the signed package into place
    # print "signPackage received: "
    # print pkg
    
    pkg_dir = os.path.dirname( pkg )
    pkg_base_name = os.path.basename( pkg )
    ( pkg_name_no_extension, pkg_extension ) = os.path.splitext( pkg_base_name )
    # print "pkg_dir: " + pkg_dir
    # print "pkg_base_name: " + pkg_base_name
    unsigned_pkg_path = os.path.join( pkg_dir, pkg_name_no_extension + "-unsigned" + pkg_extension )
    # print os.path.abspath(pkg)
    # print os.path.abspath(unsigned_pkg_path)
    # print "unsigned path: " + unsigned_pkg_path
    os.rename( os.path.abspath(pkg), os.path.abspath(unsigned_pkg_path) )

    command_line_list = [ "/usr/bin/productsign", \
                          "--sign", \
                          cert, \
                          unsigned_pkg_path, \
                          pkg, ] # " > /dev/null 2>&1" 
    # print command_line_list
    # print command_line_list
    subprocess.call( command_line_list )
    os.remove(unsigned_pkg_path)
    
# Function to load the latest BESAgent Installer
def loadPackages():
    # searches for BESAgent installer packages, returns latest version if 
    # multiple are found
    # Store packages in local folder
    besPkgs = []
    # Look in local folder
    source = "./"
    # check each file
    for filename in sorted(os.listdir(source)):
        # join path and filename
        p=os.path.join(source, filename)
        # check if it's a file
        if os.path.isfile(p):
            print("Found: " + str(filename))
            # Check if it matches BESAgent regex
            pattern = re.compile(r'^BESAgent-(\d+.\d+.\d+.\d+)-*.*pkg')
            match = pattern.search(filename)
            # If it matches, add it to the array of all packages
            if match:
                besPkgs.append(p)
    # If we have more than one package found, notify
    if len(besPkgs) > 1:
        print "Found more than one package, choosing latest version."
    # Return the last package found, which should be latest verison
    return besPkgs[-1]

# Clean out the modified files
def clean_up(oldfilepath):
    # We're done with the default folder, so we can remove it
    if os.path.isdir(oldfilepath):
        shutil.rmtree(oldfilepath)

# Touch a file - written by mah60
def touch(path):
    basedir = os.path.dirname(path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    open(path, 'a').close()

def purgeAll(dir):
    pattern = re.compile(r'BESAgent-.*(\d+.\d+.\d+.\d+)-*.*pkg')
    for installer in os.listdir(dir):
        if re.search(pattern, installer):
            print "Removed {0}".format(os.path.join(dir, installer))
            os.remove(os.path.join(dir, installer))

def purgeOld(dir):
    pattern = re.compile(r'^BESAgent-(\d+.\d+.\d+.\d+)-*.*pkg')
    for installer in os.listdir(dir):
        if re.search(pattern, installer):
            print "Removed {0}".format(os.path.join(dir, installer))
            os.remove(os.path.join(dir, installer))

def buildPkg(name,guid,ag=""):
    # print "!!!!!making pacakge for {} {} {}".format(name, guid, ag)
    # Name of temp unit folder
    if ag != "":
        unit_folder = name + "-" + ag + "-" + default_folder
    else:
        unit_folder = name + "-" + default_folder
    # Name of unit package
    unit_package = unit_folder + ".pkg"

    # Copy modified package folder to temp unit folder
    sys_cmd = "cp -R " + modifiedDest + " " + unit_folder
    os.system(sys_cmd)

    # Touch GUID id file
    if guid != "":
        touch(os.path.join(unit_folder, "besagent.pkg/Scripts/", guid + ".id"))
    
    # Touch ag id file
    if ag:
        touch(os.path.join(unit_folder, "besagent.pkg/Scripts/", ag))
    
    # Echo Unit Name into Brand file if requested
    if args.custom_brand:
        sys_cmd = "echo \"" + name + "\" > " + os.path.join(unit_folder, "besagent.pkg/Scripts" ,"brand.txt")
        os.system(sys_cmd)
    
    # Flatten customized unit folder into final package
    sys_cmd = "pkgutil --flatten " + unit_folder + " " + finishedFolder + "/" + unit_package
    os.system(sys_cmd)
    # Clean out custom folder
    clean_up(unit_folder)
    
    # Sign package
    signPackage(finishedFolder + "/" + unit_package, signing_cert)
    # If the distribute argument is true
    # Copy installers to Share mounted locally
    if args.distribute_pkgs:
        unitInstallerFolder = distributePath()
        shutil.copy(os.path.join(finishedFolder, unit_package), os.path.join(unitInstallerFolder + "/" + unit_package))
        print "Copied pkg {} to Unit folder".format(unit_package)

def distributePath():
    defaultInstallerFolder = "/tmp/"
    if os.path.isdir(Share):
        # print "Found DLE Share"
        unitFolder = os.path.join(Share, name)
        print unitFolder
        if os.path.isdir(unitFolder):
            # print "Found Unit Folder in  Share"
            return unitFolder
        else:
            print "Failed to find unit folder"
            exit(1)
            return defaultInstallerFolder
    else:
        print "No DLE Share"
        exit(1)
        return defaultInstallerFolder

def copyInstallers(finishedFolder, unit_package, unitInstallerFolder):
    # Copy installers to  Share mounted locally
    if args.distribute_pkgs:
        # if /Volumes/ exists
        checkPath = distributePath()
        if os.path.isdir(checkPath):
            # Copy package to folder
            shutil.copy(os.path.join(finishedFolder, unit_package), os.path.join(unitInstallerFolder + "/" + unit_package))
            print "Copied pkg {} to Unit folder".format(unit_package)
            # else:
            #     print "Unit does not have a Division Installers folder"
        else:
            print "Unit does not have a folder"

# Add command line arguments
parser = argparse.ArgumentParser(description='Build BESAgent Installers.', conflict_handler='resolve')

# Add option for adding band
parser.add_argument('--brand','-b', dest='custom_brand', action="store_true",
                    help='add branding text to the BESAgent pacakge -b, --brand')

# Add option for adding custom settings
parser.add_argument('--settings','-s', dest='custom_settings', action="store_true", default=True,
                    help='add custom settings cfg to the BESAgent pacakge -s, --settings')

# Add option for custom division
parser.add_argument('--custom','-c', dest='custom_division', action="append", nargs=2, metavar=('URN', 'GUID'),
                    help='create a installer for a custom division -c, --custom <URN> <GUID>')

# Add option for specific package
parser.add_argument('--package','-p', dest='custom_package', action="append", type=str,
                    help='path to custom package to use -p, --package [/path/to/package.pkg]')

# Add option to copy packages to Share
parser.add_argument('--distribute','-d', dest='distribute_pkgs', action="store_true",
                    help='distribute packages to share unit folders -d, --distribute')

# Add option to copy packages to Share
parser.add_argument('--removeoldpackages','-r', dest='remove_pkgs', action="store_true",
                    help='remove old packages from share unit folders -r, --removeoldpackages')

# Add option for custom automatic group
parser.add_argument('--autogroup','-a', dest='auto_group', action="append", type=str,
                    help='create a installer for a custom division (-c) with an automatic group')

# Add option to display version of BES Package
parser.add_argument('--agentversion','-v', dest='agent_version', action="store_true",
                    help='Display version of agent being used -v, --agentversion')

# Add option to display version of BES Package
parser.add_argument('--jamfpkg','-j', dest='jamf_package', action="store_true",
                    help='Create a package for Jamf (no site ID file) -j, --jamfpkg')

# Parse the arguments
args = parser.parse_args()

# Dict to Store units:
Divs = {}
ag = ""

# Set share path
share=""

if args.jamf_package:
    jamf_package = True
else:
    jamf_package = False
    
# Set purge old installers to true if we get the arguement
if args.remove_pkgs:
    purgeOldInstallers = True
else:
    purgeOldInstallers = False

# Check that we're on OS X
if not sys.platform.startswith('darwin'):
     print "This script currently requires it be run on OS X"
     exit(2)

# run function to get packages
if args.custom_package:
    default_package = args.custom_package[0]
    print default_package[0:-4]
    default_folder = default_package[0:-4]
else:
    default_package = loadPackages()
    # remove .pkg from name
    default_folder = default_package[2:-4]

# Make sure our modified package folder exists
modifiedFolder = "ModifiedPackage"
if not os.path.isdir(modifiedFolder):
    # Make it if needed
    os.mkdir(modifiedFolder)

# Notify user of default package being used
print "Using Package: " + default_package

if args.agent_version == True:
    exit(0)

# Make the path for the modified package destination
modifiedDest = os.path.join(modifiedFolder, default_folder)

# Print path for modified folder
# print "Modified Dest: {0}".format(modifiedDest)
# Delete old files
clean_up(modifiedDest)

# Set path to distribution file
DistroFile = os.path.join(modifiedDest, "Distribution")

# If the default folder is missing
# Default folder is the BESAgent package expanded, 
# with the addition of our ModifiedFiles.
if not os.path.isdir(modifiedDest):
    # Expand default pacakge to create the default folder
    sys_cmd = "pkgutil --expand " + default_package + " " + modifiedDest
    os.system(sys_cmd)
    pkg_pkginfo = os.path.join(modifiedDest, "besagent.pkg", "PackageInfo")
    # Update PkgInfo to remove relocate
    derelocatePacakge(pkg_pkginfo)
    # Update Distribution file to remove relocate tags
    # derelocatePacakge(DistroFile) # - Not Needed
    # Set up paths to the Modified Files and their new destination in expanded package
    src = "./ModifiedFiles/"

    # Disabled downloading of latest masthead due to errors with update versions
    # Automatic update of masthead (actionstie)
    if not os.path.exists(os.path.join(src, "ActionSite.afxm")):
        # os.remove(os.path.join(src, "ActionSite.afxm"))
        response = url.urlopen(bigfix_root_server)
        actionsite = response.read()
        # Write actionsite afxm to modified files.
        # print(actionsite)
        file1 = open(os.path.join(src, "ActionSite.afxm"),"w")
          # \n is placed to indicate EOL (End of Line)
        file1.write(actionsite)
        # file1.writelines(L)
        file1.close() #to change file access modes
    
    dest = os.path.join(modifiedDest, "besagent.pkg/Scripts/")
    # Create array of all of the modified files 
    src_files = os.listdir(src)
    # For each file in the array of all modified files
    # print "Dest {0}".format(dest)
    for file_name in src_files:
        # create path with source path and file name
        full_file_name = os.path.join(src, file_name)
        # if it's a file, copy it to the default folder
        if (os.path.isfile(full_file_name)):
            if "clientsettings.cfg" in full_file_name:
                # Copy custom settings if requested
                if args.custom_settings:
                    shutil.copy(full_file_name, dest)
            elif file_name == "preinstall":
                # Copy the preinstall if we dont need a jamf package
                if not jamf_package:
                    print "Copying preinstall"
                    shutil.copy(full_file_name, dest)
            elif file_name == "jamf_preinstall":
                # If building jamf package, use custom preflight
                if jamf_package:
                    print "Copying jamf_preinstall"
                    postflight_dest = os.path.join(dest, "preinstall")
                    shutil.copy(full_file_name, postflight_dest)
            else:
                # Generic copy whatever file is left
                shutil.copy(full_file_name, dest)

# If we didn't get a custom division
if not args.custom_division:
    if jamf_package:
        name = "JAMFENROLL"
        guid = ""
        ag = ""
        Divs[name] = [guid, ag]
    else:
        # Load the  units
        loadUnits(units_url)
else:
# Otherwise use custom variables
    # Set Name from Args
    name = args.custom_division[0][0].replace('/','-')
    # Set GUID from Args
    guid = args.custom_division[0][1]
    # Set AutomaticGroup from Args
    ag = []
    if args.auto_group:
        ag.append(args.auto_group[0])
    if guid != "":
        # Add to Divs dict
        Divs[name] = [guid, ag]
    else:
        print "Empty GUID Provided"
        exit(1)

# Make dir for destination packages
finishedFolder = default_folder[0:-11] + "Finished"
if not os.path.isdir(finishedFolder):
    os.mkdir(finishedFolder)

# for name, guid in Divs.items():
#     print name, guid

# For each of the  units make a custom package
for name, guid in Divs.items():

    if args.distribute_pkgs and purgeOldInstallers:
        print "Removing old files"
        unitPath = distributePath()
        purgeAll(unitPath)
    
    # Print out the one we're doing
    if len(guid[1]) > 0:
        # print "-> {0:<40}       {1}: {2}".format(name,guid[0],guid[1])

        for autogroup in guid[1]:
            # print autogroup
            print "-> Making Pacakge For -> {0} : {2:<40}      {1}".format(name, guid[0], autogroup)
            buildPkg(name,guid[0],autogroup)
    else:
        # print "{0:<40}       {1}".format(name,guid[0])
        print "-> Making Pacakge For -> {0:<40}       {1}".format(name, guid[0])
        buildPkg(name,guid[0])
        
    # exit(0)
# Clean ourselves up
clean_up(modifiedDest)
