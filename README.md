oe-layerindex-config
====================

This is a proof-of-concept, work-in-progress attempt at a new configuration
workflow for OE builds.

The idea is that a person wants to make a build for the board sitting on their
desk. As such they want a configuration setup that is board-focused. This
configuration helper leverages the information collected in the OE layer
index [1] to guide the user through the configuration process.

The user will still use bitbake to perform the build and is free to tweak the
configuration. This utility is meant to be a configuration helper, in essence,
a replacement for the "source openembedded-core/oe-init-build-env" step.

How to Use It
-------------

1. checkout this repository somewhere
2. source the oesetup.sh script

e.g.

	$ mkdir ~/devel/extern; cd ~/devel/extern
	$ git clone git://github.com/twoerner/oe-layerindex-config.git
	$ mkdir ~/oebuild; cd ~/oebuild
	$ . ~/devel/extern/oe-layerindex-config/oesetup.sh

The scripts guide you through selecting your branch, machine, distro, download
directory. When you are done it leaves you in the build directory from which
you can issue a bitbake command (e.g. bitbake core-image-minimal).



TODO
----

- it'd be nice if it could ask the user a bunch of other configuration
  questions, such as:
  	- compiler (version, linaro, external, etc)
  	- C library (musl, glibc, uclibc)
  	- sdk machine
  	- USER_CLASSES
  	- EXTRA_IMAGE_FEATURES
  	- recipes (?)
  	- package class (ipk, rpm, deb)
- it would be nice if there was more help for figuring out which images are
  available (e.g. with angstrom there is angstrom-image, console-image,
  etc... but if your distro isn't angstrom then these aren't available)





[1] http://layers.openembedded.org/layerindex
