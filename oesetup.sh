#!/usr/bin/env bash

OEROOT=$(pwd)
RUNFROMDIR="$(dirname $(realpath $BASH_SOURCE))"
BINNAME=$(basename $0)

# make sure we're sourced and not run in a subshell
if [ "$0" = "$BASH_SOURCE" ]; then
	echo "this script needs to modify your shell's environment"
	echo "as such, it needs to be sourced, rather than run in a subshell"
	echo "please run as:"
	echo "    $ . $0 [<options>]"
	echo "and not as:"
	echo "    $ ./$BINNAME [<options>]"
	exit 1
fi

# NOTE: a trap..EXIT won't work here because we're sourced
cleanup() {
	unset RUNFROMDIR
	unset OEROOT BINNAME BUILDDIR
	unset DISTRO DISTROLAYER DISTROS DISTROSCNT
	unset DL_DIR
}

# find programs
if [ ! -x $RUNFROMDIR/pysetup-int.py ]; then
	echo "can't find internal setup routine $RUNDROMDIR/pysetup-int.py"
	cleanup
	return 1
fi
which dialog > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "ERROR: can't find 'dialog' command"
	return 1
fi

# find local.conf
if [ ! -r $RUNFROMDIR/local.conf ]; then
	echo "can't find config file $RUNFROMDIR/local.conf"
	cleanup
	return 1
fi

BUILDDIR=${1:-build}
if [ "$(whoami)" = "root" ]; then
	echo "ERROR: please don't run this as root!"
	cleanup
	return 1
fi

$RUNFROMDIR/pysetup-int.py $BUILDDIR
if [ $? -ne 0 ]; then
	cleanup
	return 1
fi

# specify DL_DIR
read -e -p "Please indicate the location of your DL_DIR (downloads directory): " DL_DIR
cat >> $BUILDDIR/conf/auto.conf <<-EOF
	DL_DIR ?= "${DL_DIR}"
EOF

# Make sure Bitbake doesn't filter out the following variables from our environment.
export BB_ENV_EXTRAWHITE="MACHINE DISTRO TCMODE TCLIBC HTTP_PROXY http_proxy \
HTTPS_PROXY https_proxy FTP_PROXY ftp_proxy FTPS_PROXY ftps_proxy ALL_PROXY \
all_proxy NO_PROXY no_proxy SSH_AGENT_PID SSH_AUTH_SOCK BB_SRCREV_POLICY \
SDKMACHINE BB_NUMBER_THREADS BB_NO_NETWORK PARALLEL_MAKE GIT_PROXY_COMMAND \
SOCKS5_PASSWD SOCKS5_USER SCREENDIR STAMPS_DIR"

export PATH="$(echo ${PATH} | sed -e 's/\(:.\|:\)*:/:/g;s/^.\?://;s/:.\?$//')"
NEWPATHS="$OEROOT/layers/openembedded-core/scripts:$NEWPATHS"
NEWPATHS="$OEROOT/layers/bitbake/bin:$NEWPATHS"
export PATH=$NEWPATHS$(echo $PATH | sed -e "s|:$NEWPATHS|:|g" -e "s|^$NEWPATHS||")
unset NEWPATHS

cd $BUILDDIR
cp $RUNFROMDIR/local.conf conf

cat <<EOF
Your build environemnt has been configured with:

$(cat conf/auto.conf)
PATH = $PATH

You can now run bitbake commands.
Enjoy!
EOF

cleanup