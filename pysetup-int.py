#! /usr/bin/env python
## Copyright (C) 2015  Trevor Woerner <twoerner@gmail.com>

import os
import sys
import json
import getopt
import locale
from dialog import Dialog

def get_layer_name_from_id(id):
	for thisLayer in layerItems:
		thisLayerID = thisLayer["id"]
		if thisLayerID == id:
			return thisLayer["name"]
	return ""

def get_branch_name_from_id(id):
	for thisBranch in branches:
		thisBranchID = thisBranch["id"]
		if thisBranchID == id:
			return thisBranch["name"]
	return ""

locale.setlocale(locale.LC_ALL, '')

# figure out where we are
OEROOT = os.getcwd()

# process cmdline args
try:
	cmdlineopts, cmdlineargs = getopt.getopt(sys.argv[1:], "r", ["refresh"])
except Exception, e:
	print "Cmdline parsing error"
	sys.exit(1)
for opt, arg in cmdlineopts:
	if opt in ("-r", "--refresh"):
		os.system("rm -fr " + OEROOT + "/index/*json")
buildDir = OEROOT + "/build"
if len(cmdlineargs) > 0:
	buildDir = OEROOT + "/" + cmdlineargs[0]

# get, check, update index data
try:
	os.mkdir(OEROOT + "/index")
except Exception, e:
	pass
filename = OEROOT + "/index/machines.json"
if not os.path.isfile(filename):
	os.system("wget http://layers.openembedded.org/layerindex/api/machines/ -O " + filename)
filename = OEROOT + "/index/branches.json"
if not os.path.isfile(filename):
	os.system("wget http://layers.openembedded.org/layerindex/api/branches/ -O " + filename)
filename = OEROOT + "/index/layerBranches.json"
if not os.path.isfile(filename):
	os.system("wget http://layers.openembedded.org/layerindex/api/layerBranches/ -O " + filename)
filename = OEROOT + "/index/layerItems.json"
if not os.path.isfile(filename):
	os.system("wget http://layers.openembedded.org/layerindex/api/layerItems/ -O " + filename)
machines = json.load(open(OEROOT + '/index/machines.json'))
branches = json.load(open(OEROOT + '/index/branches.json'))
layerBranches = json.load(open(OEROOT + '/index/layerBranches.json'))
layerItems = json.load(open(OEROOT + '/index/layerItems.json'))

# fetch bitbake[master] so we can use bitbake-layers
if not os.path.isdir(OEROOT + "/index/bitbake"):
	os.system("git clone git://github.com/twoerner/bitbake.git " + OEROOT + "/index/bitbake")
else:
	os.system("cd " + OEROOT + "/index/bitbake; git checkout master; git pull")
os.environ["PATH"] = OEROOT + "/index/bitbake/bin" + os.pathsep + os.environ["PATH"]
BBpath = buildDir + os.pathsep + OEROOT + "/layers/openembedded-core/meta"
os.environ["BBPATH"] = BBpath
BBfiles = OEROOT + "/layers/openembedded-core/meta/recipes-*/*/*.bb"
os.environ["BBFILES"] = BBfiles

# make build,conf dir and some configuration files
if not os.path.isdir(buildDir + "/conf"):
	try:
		os.makedirs(buildDir + "/conf")
	except Exception, e:
		print "Can't create build,conf directory: " + buildDir + "/conf"
		print e
		sys.exit(1)
try:
	os.chdir(buildDir)
except Exception, e:
	pass
if not os.path.isdir(OEROOT + "/layers"):
	try:
		os.makedirs(OEROOT + "/layers")
	except Exception, e:
		print "Can't create " + OEROOT + "/layers dir"
		print e
		sys.exit(1)

# create bblayers.conf
bblayersconfname = buildDir + "/conf/bblayers.conf"
if os.path.isfile(bblayersconfname):
	os.system("rm -f " + bblayersconfname)
bblayersconf = open(bblayersconfname, "w")
bblayersconf.write("LCONF_VERSION = \"6\"\n\n")
bblayersconf.write("BBPATH = \"" + BBpath + "\"\n")
bblayersconf.write("BBFILES ?= \"" + BBfiles + "\"\n\n")
bblayersconf.write("BBLAYERS = \"\"\n")
bblayersconf.close()

# create auto.conf
siteconfname = buildDir + "/conf/auto.conf"
if os.path.isfile(siteconfname):
	os.system("rm -f " + siteconfname)
siteconf = open(siteconfname, "w")
siteconf.write("BBLAYERS_FETCH_DIR = \"" + OEROOT + "/layers\"\n")
siteconf.close()

# dialog init
d = Dialog(dialog="dialog")

# choose a branch
# sort by field "sort_priority" and ignore "oe-classic"
branchLines = sorted(branches, key=lambda k: k["sort_priority"])
branchLines = filter(lambda x: x["name"] != "oe-classic", branchLines)
choices = []
for line in branchLines:
	choices.append((str(line["name"]),""))
code, tag = d.menu("Please choose a branch:", height=0, width=0, menu_height=0, choices=choices)
if code != d.DIALOG_OK:
	sys.exit(1)
branchChoice = tag
branchChoiceID = 1 # choose branch 'master' as default, it is known (apriori) that branch id 1 == master
for thisBranch in branches:
	branchName = thisBranch["name"]
	if branchName == branchChoice:
		branchChoiceID = thisBranch["id"]
		break
if branchChoice == "denzil":
	bitbakeBranch = "1.14"
elif branchChoice == "danny":
	bitbakeBranch = "1.16"
elif branchChoice == "dylan":
	bitbakeBranch = "1.18"
elif branchChoice == "dora":
	bitbakeBranch = "1.20"
elif branchChoice == "daisy":
	bitbakeBranch = "1.22"
elif branchChoice == "dizzy":
	bitbakeBranch = "1.24"
elif branchChoice == "fido":
	bitbakeBranch = "1.26"
else:
	bitbakeBranch = "master"
if not os.path.isdir(OEROOT + "/layers/bitbake"):
	os.system("cd " + OEROOT + "/layers; git clone git://git.openembedded.org/bitbake.git -b " + bitbakeBranch)
else:
	os.system("cd " + OEROOT + "/layers/bitbake; git checkout " + bitbakeBranch + "; git pull")
if not os.path.isdir(OEROOT + "/layers/openembedded-core"):
	os.system("cd " + OEROOT + "/layers; git clone git://git.openembedded.org/openembedded-core.git -b " + branchChoice)
else:
	os.system("cd " + OEROOT + "/layers/openembedded-core; git checkout " + branchChoice + "; git pull")

# choose a machine:layer from the branch chosen above
choices = []
machineLines = sorted(machines, key=lambda k: k["name"])
for thisMachine in machineLines:
	machineLayerBranchID = thisMachine["layerbranch"]
	for thisLayerBranch in layerBranches:
		thisLayerBranchID = thisLayerBranch["id"]
		if thisLayerBranchID == machineLayerBranchID:
			machineLayerID = thisLayerBranch["layer"]
			machineBranchID = thisLayerBranch["branch"]
			if machineBranchID == branchChoiceID:
				choices.append((str(thisMachine["name"]) +":" + get_layer_name_from_id(machineLayerID), thisMachine["description"]))
code, tag = d.menu("Please choose a machine:", height=0, width=0, menu_height=0, choices=choices)
if code != d.DIALOG_OK:
	sys.exit(1)
machineChoice = tag.split(':')[0]
bspLayerChoice = tag.split(':')[1]
siteconf = open(siteconfname, "a+")
siteconf.write("MACHINE ?= \"" + machineChoice + "\"\n");
siteconf.close()
os.system("bitbake-layers layerindex-fetch --branch " + branchChoice + " " + bspLayerChoice)

# choose a distro layer
choices = []
distroLines = sorted(layerItems, key=lambda k: k["name"])
distroLines = filter(lambda x: x["layer_type"] == "D", distroLines)
choices.append(("nodistro", "The distro-less distro"))
for line in distroLines:
	choices.append((u''.join(line["name"]).encode('utf-8').strip(),u''.join(line["description"]).encode('utf-8').strip()))
code, tag = d.menu("Please choose a distro:", height=0, width=0, menu_height=0, choices=choices)
if code != d.DIALOG_OK:
	sys.exit(1)
distroLayerChoice = tag
if distroLayerChoice != "nodistro":
	os.system("bitbake-layers layerindex-fetch --branch " + branchChoice + " " + distroLayerChoice)

# choose a distro
distroChoice = "nodistro"
if distroLayerChoice != "nodistro":
	choices = []
	for root, dirs, files in os.walk(OEROOT + "/layers/" + distroLayerChoice):
		for file in files:
			if file.endswith(".conf"):
				if "conf/distro" in root:
					if "defaultsetup" not in file:
						choices.append((file[:-5], root))
	if choices.__len__() == 0:
		print "can't find a distro configuration in " + distroLayerChoice
	elif choices.__len__() > 1:
		code, tag = d.menu("Please choose:", height=0, width=0, menu_height=0, choices=choices)
		if code != d.DIALOG_OK:
			sys.exit(1)
		distroChoice = tag
	else: # == 1
		distroChoice = choices[0]
siteconf = open(siteconfname, "a+")
siteconf.write("DISTRO ?= \"" + distroChoice + "\"\n")
siteconf.close()
