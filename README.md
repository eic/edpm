# ejpm

**ejpm** stands for **e**<sup>**J**ANA</sup> **p**acket ~~**m**anager~~ helper

**The goal** of ejpm is to provide easy experience of installing e<sup>JANA</sup> reconstruction framework and supporting packages in different environments: various operating systems, docker images, etc. The secondary goal is to help users with e^JANA plugin development cycle.

**The reason** why ejpm is here (and a pain, which it tries to ease) - is that there is no standard convention of how all dependent packages are installd in our field. Some packages (like eigen, xerces, etc.) are usually supported by OS maintainers, while others (Cern ROOT, Geant4) are usually built by users or other packet managers and could be placed anywhere. 

**ejpm is complementary** to e<sup>JANA</sup>. It is not a part of e<sup>JANA</sup> build system and one can compile and install e<sup>JANA</sup> without ejpm   

* A database stores the current state of installation and location of stored packets.
* Package installation contexts holds information of configuration and steps needed to install a package
* CLI (command line interface)- provides users with commands to manipulate packets

Users are pretty much encouraged to change the code and everything is done here to be user-change-friendly

So the directory structure is made according to the concepts:

* **packages** - files for each package, with information of configuration and steps needed to install a package
* **db** - classes to work with the "Current state database"
* **cli** - commands for command line interface
* **side_packages** - Side packages that are used as a fallback if such packages are not installed
 