# jepm

Experiments with lean jana

* Database (json file at this moment) stores the current state of installation.
* Package installation contexts holds information of configuration and steps needed to install a package
* CLI (command line interface)- provides users with commands to manipulate packages

Users are pretty much encouraged to change the code and everything is done here to be user-change-friendly

So the directory structure is made according to the concepts:

* **packages** - files for each package, with information of configuration and steps needed to install a package
* **db** - classes to work with the "Current state database"
* **cli** - commands for command line interface
* **side_packages** - Side packages that are used as a fallback if such packages are not installed
 