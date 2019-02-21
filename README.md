# ejpm

**ejpm** stands for **e**<sup>**J**ANA</sup> **p**acket ~~**m**anager~~ helper

**The goal** of ejpm is to provide easy experience of:

* installing e<sup>JANA</sup> reconstruction framework and supporting packages
* uify installation in different environments: various operating systems, docker images, etc. 

The secondary goal is to help users with e^JANA plugin development cycle.



### The reason

why ejpm is here (and a pain, it tries to resolve) - is that 
there is no standard convention in our field of how all dependent packages are 
installed. Some packages (like eigen, xerces, etc.) are usually supported by 
OS maintainers, while others (Cern ROOT, Geant4) are usually built by users or 
other packet managers and could be located anywhere. 

It should be as easy as:

```bash
> ejpm find all            # try to automatically find dependent packets
> ejpm --top-dir=/opt/eic  # set where to install missing packets
> ejpm install all         # build and install missing packets
```

It also gives a possibility to fine control over dependencies

```bash
> ejpm set root /opt/root6_04_16  # manually add cern ROOT location to use
> ejpm rebuild jana && ejpm rebuild ejana  # rebuild packets after it 
```



What ejpm is not: 

1. It is not a real package manager, which automatically solves dependencies
2. **ejpm is not a requirment** for e<sup>JANA</sup>. It is not a part of e<sup>JANA</sup> 
    build system and one can compile and install e<sup>JANA</sup> without ejpm   

* A database stores the current state of installation and location of stored packets.
* Package installation contexts holds information of configuration and steps needed to install a package
* CLI (command line interface)- provides users with commands to manipulate packets

Users are pretty much encouraged to change the code and everything is done here to be user-change-friendly

## Installation

#### Regular:

```bash
pip install ejpm
```

#### Regular + JLab certs problems:
There could be problems on JLab machines (details are in the end):
```bash
python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --install ejpm
```

### Manual:
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




## Environment

```EJPM_DATA_PATH``` - sets the path where the configuration db.json and env.sh, env.csh are located


### JLab certificate problems

If you get errors like:
```
Retrying (...) after connection broken by 'SSLError(SSLError(1, u'[SSL: CERTIFICATE_VERIFY_FAILED]...
```

The problem is that ```pip``` is trustworthy enough to use secure connection to get packages. 
And JLab is helpful enough to put its root level certificates in the middle.

1. The easiest solution is to continue use pip declaring PiPy sites as trusted:  
    ```bash
    python -m pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org --install ejpm
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
 