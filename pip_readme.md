# edpm

**edpm** stands for **E**IC **d**evelopment  **p**acket ~~**m**anager~~ helper

**The goal** of edpm is to provide esier experience of building EIC simulation and reconstruction 
framework and supporting packages on a user machine with development reasons. 

***TL;DR;*** example for CentOS/RHEL7
```bash

# INSTALL PREREQUESTIES
edpm req centos eicrecon         # get list of OS packets required to build jana and deps
sudo yum install ...          # install watever 'edpm req' shows

# or if you are a lucky bash user (yes, csh is still common in physics):
sudo yum install $(edpm req centos eicrecon --all) 

# SETUP edpm
edpm --top-dir=<where-to>   # Directory where packets will be installed
edpm set root `$ROOTSYS`    # (optional) if you have CERN.ROOT or other monster packets: 

# INSTALL PACKETS
edpm install eicrecon          # install eicrecon and dependencies (like genfit, jana and rave)
edpm install g4e            # install 'Geant 4 EIC' and dependencies (like vgm, hepmc)

# SET RIGHT ENVIRONMENT 
source<$(edpm env)          # set environment variables, 
source ~/.local/share/edpm/env.sh  # more convenient way. Use *.csh file for tcsh
```


### Motivation

**edpm** is here as there is no standard convention in HEP and NP of how to distribute and install software packages 
with its dependencies. Some packages (like eigen, xerces, etc.) are usually supported by 
OS maintainers, while others (Cern ROOT, Geant4, Rave) are usually built by users or 
other packet managers and could be located anywhere. Here comes "version hell" multiplied by lack of software manpower 
(e.g. to continuously maintain packages on distros level or even to fix GitHub issues) 
Still we love our users and try to get things easier for them!
So here is edpm.


At this points **edpm** tries to unify experience and make it simple to deploy e^JANA for:

- Users on RHEL 7, 8 and CentOS
- Users on Ubutnu/Debian (and Windows with WSL) \*\*
- Docker and other containers


It should be as easy as ```> edpm install eicrecon``` to build and install a packet called 'eicrecon'
 and its dependencies. But it should also provide a possibility to adopt existing installations
  and have a fine control over dependencies: ```> edpm set root /opt/root6_04_16```

**edpm** is not: 

1. It is not a **real** package manager, which automatically solves dependencies, 
download binaries (working with GPG keys, etc.), finds fastest mirrors, manage... etc. 
2. **edpm is not a requirment** for e<sup>JANA</sup>. It is not a part of e<sup>JANA</sup> 
    build system and one can compile and install e<sup>JANA</sup> without edpm   


## Get eicrecon installed

Step by step explained instruction:

1. **Install prerequisites** utilizing OS packet manager:

    ```bash
    # To see the prerequesties
    edpm req ubuntu         # for all packets that edpm knows
    edpm req centos eicrecon   # for eicrecon and its dependencies only
    
    # To put everything into packet manager 
    apt-get -y install `edpm req ubuntu --all`   # debian
    yum -y install `edpm req centos --all`       # centos/centos    
    ```
    
    At this point only ***'ubuntu'*** and ***'centos'*** are known words for req command. Put: 
    * ***ubuntu*** for debian family 
    * ***centos*** for RHEL and CentOS systems.

    *In the future this will be updated to support macOS and to have more detailed versions*

2. **Set top-dir**. This is where all missing packets will be installed.   

    ```bash
    edpm --top-dir=<where-to-install-all>
    ```
   
3. **Register installed packets**. You may have CERN.ROOT installed (req. version >= 6.14.00). Run this:
    ```bash
    edpm set root `$ROOTSYS` 
    ```
   
   You may set paths for other installed dependencies combining:  
   ```bash
   edpm install eicrecon --missing --explain    # to see missing dependencies
   edpm set <name> <path>                    # to set dependency path
   ```
   
   Or you may skip this step and just get everything installed by edpm
   
4. **Install eicrecon** and all missing dependencies:

    ```bash
    edpm install eicrecon
    ```

5. **Set environment**. There are 3 ways for doing this this: 
    
    1. Dynamically source output of ```edpm env``` command (recommended)
    
        ```bash        
        source <(edpm env)                # works for bash only
        ```
    2. Save output of ```edpm env``` command to a file (can be useful)
    
        ```bash
         edpm env sh  > your-file.sh       # get environment for bash or compatible shells
         edpm env csh > your-file.csh      # get environment for CSH/TCSH
        ```
    3. Use edpm generated ```env.sh``` and ```env.csh``` files (lazy and convenient)
    
        ```bash        
        $HOME/.local/share/edpm/env.sh    # bash and compatible
        $HOME/.local/share/edpm/env.csh   # for CSH/TCSH
        ```
        (!) The files are regenerated each time ```edpm <command>``` changes something in edpm.
        If you change ```db.json``` by yourself, edpm doesn't track it automatically, so call 'edpm env'
        to regenerate these 2 files
    

## Environment

 ```edpm_DATA_PATH```- sets the path where the configuration db.json and env.sh, env.csh are located


Each time you make changes to packets, 
edpm generates `env.sh` and `env.csh` files, 
that could be found in standard apps user directory.

For linux it is in XDG_DATA_HOME:

```
~/.local/share/edpm/env.sh      # sh version
~/.local/share/edpm/env.csh     # csh version
~/.local/share/edpm/db.json     # open it, edit it, love it
```

> XDG is the standard POSIX paths to store applications data, configs, etc. 
edpm uses [XDG_DATA_HOME](https://wiki.archlinux.org/index.php/XDG_Base_Directory#Specification)
to store `env.sh`, `env.csh` and `db.json` and ```db.json```

You can always get fresh environment with edpm ```env``` command 
```bash
edpm env
```

You can directly source it like:
```bash
source<(edpm env)
```

You can control where edpm stores data by setting ```edpm_DATA_PATH``` environment variable.


<br><br>

