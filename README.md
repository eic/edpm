# ejpm

**ejpm** stands for **e**<sup>**J**ANA</sup> **p**acket ~~**m**anager~~ helper

**The goal** of ejpm is to provide easy experience of:

* installing e<sup>JANA</sup> reconstruction framework and supporting packages
* uify installation in different environments: various operating systems, docker images, etc. 

The secondary goal is to help users with e^JANA plugin development cycle.



# Motivation

***TL;DR;*** Major HEP and NP scientific packages are not supported by some major distros and 
usually are crappy in terms of dependency/version requirements. Everybody have to reinvent the wheel to include 
such packages in their software chains and make users' lives easier. And we do. 

***Longer reading***

**ejpm** is here as there is no standard convention in HEP and NP of how to distribute and install software packages 
with its dependencies. Some packages (like eigen, xerces, etc.) are usually supported by 
OS maintainers, while others (Cern ROOT, Geant4, Rave) are usually built by users or 
other packet managers and could be located anywhere. Here comes "version hell" and lack of software manpower (e.g. to 
continuously maintain all required packages on distros level) 

At this points **ejpm** tries to unify experience for:

- Users on RHEL 7 and CentOS
- Users on Ubutnu (and Windows with WSL)
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


**Alternatives considered**  
Is there something existing? - Simple bash build scripts get bloated and complex. Dockerfiles and similar stuff are 
too-tool-related. Build systems like scons or cmake can be used but too build specific oriented. 
Full featured package managers and tools like Homebrew are pretty complex to tame (for dealing with just 5 deps).
So here is ejpm

***ejpm* is not**: 

1. It is not a real package manager which automatically solves dependencies
2. **ejpm is not a requirment** for e<sup>JANA</sup>. It is not a part of e<sup>JANA</sup> 
    build system and one can compile and install e<sup>JANA</sup> without ejpm   

**Design features**

* External:
    * ejpm is written in pure python with minimum dependencies (2 and 3 compatible)
    * CLI (command line interface) - provides users with commands to manipulate packets 
    * JSON database stores the current state of installation and packets locations.

* Under the hood:
    * Each packet has a single python file that defines how it will be installed and configured
    * Each such file is easy to read of modify by users in case they would love to
    * Installation steps written in a style close to Dockerfile (same command names, etc) 

Users are pretty much encouraged to change the code and everything is done here to be user-change-friendly


<br><br>

## Installation

***TL;DR;***

```bash
pip install ejpm
```

If you have certificate  problems on JLab machines ([more details and options are here](#jlab-certificate-problems)):
```bash
python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org ejpm
```

More on this:

* See [INSTALLATION TROUBLESHOOTING](#installation-trougleshooting) If you don't have pip or right python version.
* See [Jlab root certificate problems](#jlab-certificate-problems) and how to solve them
* See [Manual or development installation](#manual-or-development-installation) to use this repo directly, develop EJPM or don't want to mess with pip at all?  


<br><br>

## Get ejana installed

(or crash course to ejpm)

***TL;DR;*** example for CentOS/RHEL7
```bash
ejpm req fedora ejana         # get list of OS packets required to build jana and deps
sudo yum install ...          # install watever 'ejpm req' shows
ejpm --top-dir=<where-to>     # Directory where packets will be installed
ejpm set root `$ROOTSYS`      # if you have CERN.ROOT. Or skip this step
ejpm install ejana --missing  # install ejana and dependencies (like genfit, jana and rave)
source<(ejpm env)             # set environment variables
```


Step by step explained instruction:

1. Install (or check) required packages form OS:

    ```bash
    ejpm req ubuntu         # for all packets that ejpm knows
    ejpm req fedora ejana   # for ejana and its dependencies only
    ```
   
    At this point only ***'ubuntu'*** and ***'fedora'*** are known words for req command. Put: 
    * ***ubuntu*** for debian family 
    * ***fedora*** for RHEL and CentOS systems.

    *In the future this will be updated to support macOS and to have more detailed versions*

2. Set <b><blue>top-dir</blue></b>. This is where all missing packets will be installed.   

    ```bash
    ejpm --top-dir=<where-to-install-all>
    ```
   
3. You may have CERN.ROOT installed (req. version >= 6.14.00). Run this:
    ```bash
    ejpm set root `$ROOTSYS` 
    ```
   
   You may set paths for other installed dependencies combining:  
   ```bash
   ejpm install ejana --missing --explain    # to see missing dependencies
   ejpm set <name> <path>                    # to set dependency path
   ```
   
   Or you may skip this step and just get everything installed by ejpm
   
4. Then you can install ejpm and all missing dependencies:

    ```bash
    ejpm install ejana --missing
    ```

5. Set right environment variables (right in the next section)
    
    
<br><br>

## Environment

***TL;DR;*** Just source it like:
```bash
source <(ejpm env)      
# or
source ~/.local/share/ejpm/env.sh    # or same with .csh
```

 ```EJPM_DATA_PATH```- sets the path where the configuration db.json and env.sh, env.csh are located

***longer reading:***

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

## INSTALLATION TROUBLESHOOTING



***But... there is no pip:***  
Install it!
```
sudo easy_install pip
```

For JLab lvl1&2 machines, there is a python installations that have ```pip``` :
```bash
/apps/python/     # All pythons there have pip and etc
/apps/anaconda/   # Moreover, there is anaconda (python with all major math/physics libs) 
``` 



***But... there is no easy_install!***  
Install it!
```bash
sudo yum install python-setuptools python-setuptools-devel   # Fedora and RHEL/CentOS 
sudo apt-get install python-setuptools                       # Ubuntu and Debian
# Gentoo. I should not write this for its users, right?
```

For python3 it is ```easy_install3``` and ```python3-setuptools```

***I dont have sudo privileges!***  

Add "--user" flag both for pip and easy_install for this. 
[Read SO here](https://stackoverflow.com/questions/15912804/easy-install-or-pip-as-a-limited-user)



### JLab certificate problems

If you get errors like:
```
Retrying (...) after connection broken by 'SSLError(SSLError(1, u'[SSL: CERTIFICATE_VERIFY_FAILED]...
```

The problem is that ```pip``` is trustworthy enough to use secure connection to get packages. 
And JLab is helpful enough to put its root level certificates in the middle.

1. The easiest solution is to declare PiPy sites as trusted:  
    ```bash
    python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org ejpm
    ```
2. Or to permanently add those sites as trusted in pip.config 
    ```
    [global]
    trusted-host=
        pypi.python.org
        pypi.org
        files.pythonhosted.org
    ```
    ([The link where to find pip.config on your system](https://pip.pypa.io/en/stable/user_guide/#config-file))
3. You may want to be a hero and kill the dragon. The quest is to take [JLab certs](https://cc.jlab.org/JLabCAs). 
 Then [Convert them to pem](https://stackoverflow.com/questions/991758/how-to-get-pem-file-from-key-and-crt-files).
 Then [add certs to pip](https://stackoverflow.com/questions/25981703/pip-install-fails-with-connection-error-ssl-certificate-verify-failed-certi).
 Then **check it really works** on JLab machines. And bring the dragon's head back (i.e. please, add the exact instruction to this file) 
 
 <br><br>
### Manual or development installation:
***TL;DR;*** Get EJPM, install requirements, ready:
```bash
git clone https://gitlab.com/eic/ejpm.git
pip install -r ejpm/requirements.txt
python ejpm/run_ejpm.py
```

***'ejpm'*** **command**:

Calling ```python <path to ejpm>/run_ejpm.py``` is inconvenient!
It is easy to add alias to your .bashrc (or whatever)
```sh
alias ejpm='python <path to ejpm>/run_ejpm.py'
```
So if you just cloned it copy/paste:
```bash
echo "alias='python `pwd`/ejpm/run_ejpm.py'" >> ~/.bashrc
```

**requirments**:

```Click``` and ```appdirs``` are the only requirements. If you have pip do: 

```bash
pip install Click appdirs
```
> If for some reason you don't have pip, you don't know python well enough 
and don't want to mess with it, pips, shmips and doh...
Just download and add to ```PYTHONPATH```: 
[this 'click' folder](https://pypi.org/project/click/)
and some folder with [appdirs.py](https://github.com/ActiveState/appdirs/blob/master/appdirs.py)

