# ejpm

**ejpm** stands for **e**<sup>**J**ANA</sup> **p**acket ~~**m**anager~~ helper

**The goal** of ejpm is to provide easy experience of:

* installing e<sup>JANA</sup> reconstruction framework and supporting packages
* unify installation for different environments: e.g. various operating systems, docker images, etc. 

The secondary goal is to help users with e^JANA plugin development cycle.

### Table of contents:
* [Motivation](#motivation)
* [EJPM installation](#installation)
* [Get ejana installed](#get-ejana-installed)
* [Manage environment](#environment)
* [Troubleshooting](#installation-troubleshooting)
* [Manual or devel installation](#manual-or-development-installation)
* [Adding a package](#adding-a-package)
   * [Adding Git+Cmake package example](#adding-git-cmake-package)


***Cheat sheet:***

Install ejpm:

```bash
# install EJPM
sudo python -m pip install ejpm

# OR without sudo: add --user flag and ensure ~/.local/bin is in your PATH
python -m pip install --user -U ejpm
```

> JLab machines with certificate problems - add these flags to the command above:  
>  --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org  
> see [Troubleshooting](#installation-troubleshooting) chapter for details


Install everything else

```bash

# install prerequesties
ejpm req centos ejana         # get list of OS packets required to build jana and deps
sudo yum install ...          # install whatever 'ejpm req' shows

# setup installation dir and existing packets, introspect
ejpm --top-dir=<where-to>     # Directory where packets will be installed
ejpm                          # To see how ejpm is configured
ejpm install ejana --explain  # To see what is to be installed
ejpm set root `$ROOTSYS`      # if you have CERN.ROOT. Or skip this step
ejpm set <packet> <path>      # set other existing packets. Or skip this step!!!

# Build and install the rest
ejpm install ejana            # install ejana and dependencies (like genfit, jana and rave)
ejpm install g4e              # install Geant-4-Eic and dependencies (Geant4, etc)

# Set environment
source<(ejpm env)             # set environment variables
ejpm env csh > your.csh       # if you are still on CSH

# If that worked don't read the next...
```



# Motivation

***TL;DR;*** Major HEP and NP scientific packages are not supported by some major distros and 
usually are crappy (at least in terms of dependency requirements). Everybody have to reinvent the wheel to include 
such packages in their software chains and make users' lives easier. And we do. 

***Longer reading***

**ejpm** is here as there is no standard convention in HEP and NP of how to distribute and install software packages 
with its dependencies. Some packages (like eigen, xerces, etc.) are usually supported by 
OS maintainers, while others (Cern ROOT, Geant4, Rave) are usually built by users or 
other packet managers and could be located anywhere. We also praise "version hell" (e.g. when GenFit doesn't compile 
with CLHEP from ubuntu repo) and lack of software manpower (e.g. to sufficiently and continuously maintain packages 
for major distros or even to fix some simple issues on GitHub). 

Still we love our users and ~~know they will never install everything on their own~~ so we try to get things easier for them!


At this points **ejpm** tries to unify experience and make it simple to deploy eJANA for:

- Users on RHEL 7 and CentOS
- Users on Ubutnu (and Windows with WSL)
- Docker and other containers

The experience should be as easy as pointing right configuration and installing everything 
automatically with just few commands. But also it should provide a possibility to fine control 
over installed dependencies and help with development. 

**Design features**

* Essentials:
    * ejpm is written in pure python (2 and 3 compatible) with minimum dependencies 
    * it is shipped by pip (python official repo), so can be installed with one command on all major platforms
    * CLI (command line interface) - provides users with commands to manipulate packets 
    * JSON database stores the current state and packets locations
    * It makes easy to... e.g. switch between known versions, rebuild packets, deploy missing packets, continue after fail, etc.

* Under the hood:
    * Each packet has a single python file that defines how it will be installed and configured
    * Each such file is easy to read and modify by ***inexperienced*** users in case they would love to
    * Installation steps written in a style close to Dockerfile (same command names, etc) 



**Alternatives**  

Is there something existing? What others do? - Simple bash build scripts quickly get bloated and complex. 
Dockerfiles and similar stuff are too-tool-related. Build systems like scons or cmake also too centric on compiling 
something rather than managing packets chains. Full featured package managers and tools like Homebrew are pretty 
complex to tame (for dealing with just 5 deps). 

So ejpm is something more advanced than build scripts, but less cumbersome than real packet managers, 
it is in pure python, and being focused on our specific problems. 
 

***ejpm* is not**: 

1. It is not a real package manager which automatically solves dependency trees
2. **ejpm is not a requirment** for e<sup>JANA</sup>. It is not a part of e<sup>JANA</sup> 
    build system and one can compile and install e<sup>JANA</sup> without ejpm   


Users are pretty much encouraged to change the code and everything is done here to be user-change-friendly


<br><br>

## Installation

***TL;DR;***

```bash
sudo pip install --upgrade ejpm    # system level installation
pip install --user --upgrade ejpm  # User level. $HOME/.local/bin should be in $PATH
```

If you have certificate  problems on JLab machines: ([more options on certificates](#jlab-certificate-problems)):
```bash
# System level copy-paste:
sudo python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org -U ejpm
# User level copy-paste:
python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --user -U ejpm
```

More on this:

* See [INSTALLATION TROUBLESHOOTING](#installation-troubleshooting) If you don't have pip or right python version.
* See [Jlab root certificate problems](#jlab-certificate-problems) and how to solve them
* See [Manual or development installation](#manual-or-development-installation) to use this repo directly, develop EJPM or don't want to mess with pip at all?  


<br><br>

## Get ejana installed

(or crash course to ejpm)

***TL;DR;*** example for CentOS/RHEL7
```bash
ejpm req centos ejana         # get list of OS packets required to build jana and deps
sudo yum install ...          # install watever 'ejpm req' shows
ejpm --top-dir=<where-to>     # Directory where packets will be installed
ejpm set root `$ROOTSYS`      # if you have CERN.ROOT. Or skip this step
ejpm install ejana --missing  # install ejana and dependencies (like genfit, jana and rave)
source<(ejpm env)             # set environment variables
```


**Step by step explained instruction**:

1. Install (or check) required packages form OS:

    ```bash
    ejpm req ubuntu         # for all packets that ejpm knows
    ejpm req centos ejana   # for ejana and its dependencies only
    ```
   
    At this point only ***'ubuntu'*** and ***'centos'*** are known words for ```req``` command. Put: 
    * ```ubuntu``` for debian family 
    * ```centos``` for RHEL and CentOS systems.

    > In future macOS and more detailed os-versions will be supported

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
   ejpm set jana <path to jana2 install>     # JANA2 as an example
   ```
   
   Or you may skip this step and just get everything installed by ejpm
   
4. Then you can install ejpm and all missing dependencies:

    ```bash
    ejpm install ejana
    ```

5. Set right environment variables (right in the next section)
    
    
<br><br>

## Environment

***TL;DR;*** Just source it like:
```bash
source <(ejpm env)      
# or
source ~/.local/share/ejpm/env.sh    # .csh for CSH/TCSH
ejpm env                             # To generate env & regenerate env files 
```

```EJPM_DATA_PATH``` - sets the path where the configuration db.json and env.sh, env.csh are located

***longer reading:***

1. Dynamically source output of ```ejpm env``` command (recommended)
    
    ```bash        
    source <(ejpm env)                # works on bash
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
    (!) The files are regenerated each time ```ejpm``` changes something.
    If you change ```db.json``` by yourself, ejpm doesn't track it automatically, so call ```ejpm env```
    to regenerate these 2 files

**Where EJPM data is stored:**

There are standard directories for users data for each operating system. EJPM use them to store
db.json and generated environment files (EJPM doesnt use the files by itself).
 
For linux it is XDG_DATA_HOME\*:

```
~/.local/share/ejpm/env.sh      # sh version
~/.local/share/ejpm/env.csh     # csh version
~/.local/share/ejpm/db.json     # open it, edit it, love it
```

> \* - XDG is the standard POSIX paths to store applications data, configs, etc. 


**```EJPM_DATA_PATH```** - You can control where ejpm stores data by setting ```EJPM_DATA_PATH``` environment variable.


<br><br>

## INSTALLATION TROUBLESHOOTING



***But... there is no pip:***  
Install it!
```
sudo easy_install pip       # system level
easy_install pip --user     # user level
```

For JLab lvl1&2 machines, there is a python installations that have ```pip``` :
```bash
/apps/python/     # All pythons there have pip and etc
/apps/anaconda/   # Moreover, there is anaconda (python with all major math/physics libs) 
``` 

***But there is no 'pip' command?***  
If ```easy_install``` installed something, but ```pip``` command is not found after, do:

1. If ```--user``` flag was used, make sure ```~/.local/bin``` is in your ```$PATH``` variable
2. you can fallback to ```python -m pip``` instead of using ```pip``` command:
    ```bash
    python -m pip install --user --upgrade ejpm
    ``` 
 


***But... there is no easy_install!***  
Install it!
```bash
sudo yum install python-setuptools python-setuptools-devel   # centos and RHEL/CentOS 
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

# OR clone and add ejpm/bin to your PATH
export PATH=`pwd`/ejpm/bin:$PATH
```


**requirments**:

```Click``` and ```appdirs``` are the only requirements. If you have pip do: 

```bash
pip install --upgrade click appdirs
```
> If for some reason you don't have pip, you don't know python well enough 
and don't want to mess with it, pips, shmips and doh...
Just download and add to ```PYTHONPATH```: 
[this 'click' folder](https://pypi.org/project/click/)
and some folder with [appdirs.py](https://github.com/ActiveState/appdirs/blob/master/appdirs.py)


<br>

## Adding a package

Each packet is represented by a single python file - a recipe which has instructions 
of how to get and build the package. Usually it provides:
- download/clone command 
- build command 
- setup of environment variables
- system dependencies (which can be installed by OS packet managers: yum, apt) 


For simplicity (at this point) all recipes are located in a folder inside this repo: 
[ejpm/recipes](ejpm/recipes).


### Adding Git-CMake package

The most of packages served now by ejpm use git to get source code and cmake to build 
the package. As git + cmake became a 'standard' there is a basic recipe class which makes
adding new git+cmake packets straight forward. 

As a dive-in example of adding packets, 
lets look on how to add such packet using Genfit as a copy-paste example. 


[ejpm/recipes/genfit.py](ejpm/recipes/genfit.py)


**1. Set packet name and where to clone from**

One should change 3 lines: 

```python
class GenfitRecipe(GitCmakeRecipe):
    def __init__(self):
        """Installs Genfit track fitting framework"""
        
        # This name is used in ejpm commands like 'ejpm install genfit'
        super(GenfitRecipe, self).__init__('genfit')
    
        # The branch or tag to be cloned (-b flag)
        self.config['branch'] = 'master'

        # Repo address
        self.config['repo_address'] = 'https://github.com/GenFit/GenFit'   
```

Basically that is enough to build the package and one can test:

```bash
ejpm install yourpacket
```

**2. Set environment variables**

This is a done in `gen_env` function. By using this function ejpm generates environments for 
csh/tcsh, bash and python*. So 3 commands to be used in this function:

* `Set(name, value)` - equals `export name=value` in bash
* `Append(name, value)` - equals `export name=$name:value` in bash
* `Prepend(name, value)` - equals `export name=value:$name` in bash

```python
@staticmethod
def gen_env(data):
    path = data['install_path']   # data => installation information 

    yield Set('GENFIT_HOME', path)

    # add bin to PATH
    yield Prepend('PATH', os.path.join(path, 'bin'))
   
    # add lib to LD_LIBRARY_PATH
    yield Append('LD_LIBRARY_PATH', os.path.join(path, 'lib'))
```

One can test gen_env with:

```bash
ejpm env
```

> \* - if other python packages use ejpm programmatically to build something


**3. System requirments**

If packet has some dependencies that can be installed by OS packet managers such as apt, one can
add them to os_dependencies array.

```python
os_dependencies = {
    'required': {
        'ubuntu': "libboost-dev libeigen3-dev",
        'centos': "boost-devel eigen3-devel"
    },
    'optional': {
        'ubuntu': "",
        'centos': ""
    },
}
```

> (!) don't remove any sections from the map, leave them blank

To test it one can run:

```python
ejpm req ubuntu
ejpm req centos
```

### Adding a custom package

Compared to the previous example, several more functions should be added:

- `setup` - configures the package
- `step_clone`, `step_build`, `step_install` - execute commands to perform the step

**1. Setup**

Setup should provide all values, that are going to be used later in 'step_xxx' functions. 
Usually it is just 3 things:

```python
def setup(self):
    #
    # use_common_dirs_scheme() sets standard package variables:
    # source_path  = {app_path}/src/{branch}          # Where the sources for the current version are located
    # build_path   = {app_path}/build/{branch}        # Where sources are built. Kind of temporary dir
    # install_path = {app_path}/root-{branch}         # Where the binary installation is
    self.use_common_dirs_scheme()

    # Git download link. Clone with shallow copy
    self.clone_command = "git clone --depth 1 -b {branch} {repo_address} {source_path}".format(**self.config)

    # make command:
    self.build_command = './configure && make -j{build_threads} install'.format(**self.config)

```


**2. Step functions**

3 docker alike functions that helps to execute stuff:

* `run(command)` - executes the console command
* `workdir(dir)` - changes the working directory
* `env(name, value)` - sets an environment variable


```python
run(self.clone_command)         # Execute git clone command
workdir(self.source_path)       # Go to our build directory
run('./bootstrap')              # This command required to run by rave once...
env('RAVEPATH', self.install_path)
```   