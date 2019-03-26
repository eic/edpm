import os
import inspect
from setuptools import setup
from ejpm.version import version as ejpm_version

# The directory containing this file
this_script_dir = os.path.dirname(inspect.stack()[0][1])

# The text of the README file
with open(os.path.join(this_script_dir, "PYPI_README.md"), 'r') as readme_file:
    readme = readme_file.read()

# This call to setup() does all the work
setup(
    name="ejpm",
    version=ejpm_version,
    description="EIC Jana Package Manager",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/eic/ejpm",
    author="Dmitry Romanov",
    author_email="romanov@jlab.org",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["ejpm"],
    include_package_data=True,
    setup_requires=["click", "appdirs"],
    install_requires=["click", "appdirs"],
    entry_points={
        "console_scripts": [
            "ejpm=ejpm:ejpm_cli",
        ]
    },
)