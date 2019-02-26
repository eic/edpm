# ejpm

**ejpm** stands for **e**<sup>**J**ANA</sup> **p**acket ~~**m**anager~~ helper

**The main goal** of ejpm is to provide easy experience of:

* installing e<sup>JANA</sup> reconstruction framework and dependent packages
* unify installation for different environments: various operating systems, docker images, etc. 

The secondary goal is to help users with e^JANA plugin development cycle.



### Motivation

**ejpm** is here as there is no standard convention in HEP and NP of how to distribute and install software packages 
with its dependencies. Some packages (like eigen, xerces, etc.) are usually supported by 
OS maintainers, while others (Cern ROOT, Geant4, Rave) are usually built by users or 
other packet managers and could be located anywhere. Here comes "version hell" and lack of software manpower (e.g. to 
continuously maintain all required packages on distros level) 

At this points **ejpm** tries to unify experience for:

- Users on RHEL 7 and CentOS
- Users on Ubutnu
- Docker and other containers


It should be as easy as:

```bash
> ejpm find all            # try to automatically find dependent packets* 
> ejpm --top-dir=/opt/eic  # set where to install missing packets
> ejpm install all         # build and install missing packets
```

It also provides a possibility to fine control over dependencies

```bash
> ejpm set root /opt/root6_04_16           # manually add cern ROOT location to use
> ejpm rebuild jana && ejpm rebuild ejana  # rebuild* packets after it 
```

> \* - (!) 'find' and 'rebuild' commands are not yet implemented



**ejpm** is not: 

1. It is not a real package manager, which automatically solves dependencies
2. **ejpm is not a requirment** for e<sup>JANA</sup>. It is not a part of e<sup>JANA</sup> 
    build system and one can compile and install e<sup>JANA</sup> without ejpm   


## Get ejana installed

1. Install or check OS maintained required packages:

    ```bash
    > ejpm req ubuntu         # for all packets ejpm knows to built/install
    > ejpm req usubnu ejana   # for ejana and its dependencies only
    ```
   
   > At this point only ***'ubuntu'*** and ***'fedora'*** are known for req command. 
     Put 'ubuntu' for debian family and 'fedora' for RHEL and CentOS systems.
     In future this will be updated to support macOS and to have more details

2. Set <b><blue>top-dir</blue></b> to start. This is where all missing packets will be installed.   

    ```bash
    > ejpm --top-dir=<where-to-install-all>
    ```
   
3. You may have CERN.ROOT installed (req. version >= 6.14.00). Run this:
    ```bash
    > ejpm set root `$ROOTSYS` 
    ```
   
   You may set paths for other installed dependencies combining:  
   ```bash
   > ejpm install ejana --missing --explain    # to see missing dependencies
   > ejpm set <name> <path>                    # to set dependency path
   ```
   
   Or you may skip this step and just get everything installed by ejpm
   
4. Then you can install ejpm and all missing dependencies:

    ```bash
    > ejpm install ejana --missing
    ```

5. Set right environment variables. There are 3 ways for doing this this: 
    
    1. Dynamically source output of ```ejpm env``` command (recommended)
    
        ```bash        
        source <(ejpm env)                # (ejpm env csh) for CSH/TCSH
        ```
    2. Save output of ```ejpm env``` command to a file (can be useful)
    
        ```bash
         ejpm env sh  > your-file.sh       # get environment for bash or compatible shells
         ejpm env csh > your-file.csh      # get environment for CSH/TCSH
        ```
    3. Use ejpm generated ```env.sh``` and ```env.csh``` files (lazy and convenient)
    
        ```bash        
        $HOME/.local/share/ejpm/env.sh    # bash and compatible
        $HOME/.local/share/ejpm/env.csh   # for CSH/TCSH
        ```
        (!) The files are regenerated each time ```ejpm <command>``` changes something in EJPM.
        If you change ```db.json``` by yourself, ejpm doesn't track it automatically, so call 'ejpm env'
        to regenerate these 2 files
    

## Environment

 ```EJPM_DATA_PATH```- sets the path where the configuration db.json and env.sh, env.csh are located


Each time you make changes to packets, 
EJPM generates `env.sh` and `env.csh` files, 
that could be found in standard apps user directory.

For linux it is in XDG_DATA_HOME:

```
~/.local/share/ejpm/env.sh      # sh version
~/.local/share/ejpm/env.csh     # csh version
~/.local/share/ejpm/db.json     # open it, edit it, love it
```

> XDG is the standard POSIX paths to store applications data, configs, etc. 
EJPM uses [XDG_DATA_HOME](https://wiki.archlinux.org/index.php/XDG_Base_Directory#Specification)
to store `env.sh`, `env.csh` and `db.json` and ```db.json```

You can always get fresh environment with ejpm ```env``` command 
```bash
ejpm env
```

You can directly source it like:
```bash
source <(ejpm env)
```

You can control where ejpm stores data by setting ```EJPM_DATA_PATH``` environment variable.


<br><br>

