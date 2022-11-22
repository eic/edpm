# python3 build_images.py <flags> <name>
# 
# to build and push the "latest" version:
#    python3 build_images.py --no-cache --push eic
# to build and push the tagged version
#    python3 build_images.py --no-cache --push --tag=<name> eic
#
# Flags:
#  --no-cache - clean build
#  --push     - push after build
#  --tag      - tag name of an image (this is like "latest", not full docker name)
#  --latest   - add 'latest' tag to this image too
# Names:
#    eic - collection of eic images
#    devops - devops images,
#    or image name without namespace: escalate


import inspect
import json
import os
from os import path
import shlex
import subprocess
import argparse
import multiprocessing
from datetime import datetime
from typing import Tuple, Union, List, Dict
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('build.log')
# create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# create console handler with a higher log level
ch = logging.StreamHandler()

# Set pathes and global variables
this_path = path.dirname(path.abspath(inspect.stack()[0][1]))

# Number of CPU-s
cpu_count = multiprocessing.cpu_count()
if cpu_count > 1:
    cpu_count -= 1  # Leave 1 CPU to a user. Ha. Ha. Ha.

logger.debug("CPU COUNT ", cpu_count)

class ImageInfo:
    def __init__(self, category:str='', org:str='', alias:str='', name:str='', path:str='', tag:str='', depends_on:str='',  flags:str=''):
        """
        # Alias can be used to have the ImageInfo with the same name but different flags
        """
        self.category = category
        self.organization = org
        self.aslias = alias
        self.name = name
        if not alias:
            self.aslias = self.name
        self.tag = tag        
        self.depends_on = depends_on        
        self.path = path     
        self.flags = flags    # Additional flags needed to build

    @property
    def full_name(self):
        return f"{self.organization}/{self.name}:{self.tag}"
    
    @property
    def tag_latest_name(self):
        return f"{self.organization}/{self.name}:latest"

    def __repr__(self):
        return f"Image '{self.full_name}'"

# List of images
image_chains = {}
images = []

def configure_default_images(tag = 'dev', jobs=cpu_count):
    def set_images_params(images, root_path, organization, tag):
        for name,image in images.items():            
            image.tag = tag
            image.path = os.path.join(root_path, name)
            image.organization=organization

    global image_chains, images

    # List of images (and its dependencies)
    images = [
        ImageInfo(category='devops', name='eicrecon-ubuntu22-prereq', flags='--build-arg BUILD_THREADS={}'.format(jobs)),  # doesn't depends on images from this collection
        ImageInfo(category='devops', name='eicrecon-ubuntu22',   depends_on='eicrecon-ubuntu22-prereq'),
        #ImageInfo(category='devops', name='eicrecon-rhel-ubi8-prereq', flags='--build-arg BUILD_THREADS={}'.format(jobs)),
        # ImageInfo(category='devops', name='ejana-ubuntu18-prereq'),
        # ImageInfo(category='devops', name='miniconda-ubuntu16'),
        # ImageInfo(category='eic',    name='eic-science', flags='--build-arg BUILD_THREADS={}'.format(jobs)),
        # ImageInfo(category='eic',    name='eic-mceg'   , depends_on='eic-science'),
        # ImageInfo(category='eic',    name='escalate'   , depends_on='eic-mceg'),
    ]

    # put image_chains as {<category>:{<alias>:ImageInfo}} dictionary
    # and all_images {<alias>:ImageInfo}
    all_images = {}
    image_chains = {}
    for image in images:
        if image.category not in image_chains:
            image_chains[image.category] = {}        
        image_chains[image.category][image.aslias] = image
        all_images[image.aslias] = image

    # add missing info
    set_images_params(image_chains['devops'], devops_root_path, 'eicdev', tag)
#    set_images_params(image_chains['eic'], eic_root_path, 'electronioncollider', tag)
    
    image_chains['all'] = all_images

    

# Create a default images with the number of jobs = cpu_count
configure_default_images()

def _run(command: Union[str, list]) -> Tuple[int, datetime, datetime, List]:
    """Wrapper around subprocess.Popen that returns:


    :return retval, start_time, end_time, lines

    """
    if isinstance(command, str):
        command = shlex.split(command)

    # Pretty header for the command
    pretty_header = "RUN: " + " ".join(command)
    logger.info('=' * len(pretty_header))
    logger.info(pretty_header)
    logger.info('=' * len(pretty_header))

    # Record the start time
    start_time = datetime.now()
    lines = []

    # stderr is redirected to STDOUT because otherwise it needs special handling
    # we don't need it and we don't care as C++ warnings generate too much stderr
    # which makes it pretty much like stdout
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        time.sleep(0)

        output = process.stdout.readline().decode('latin-1')

        if process.poll() is not None and output == '':
            break
        if output:
            term = fh.terminator
            term = ch.terminator
            fh.terminator = ""
            ch.terminator = ""
            logger.debug(output)
            fh.terminator = term
            ch.terminator = term            
            lines.append(output)

    # Get return value and finishing time
    retval = process.poll()
    end_time = datetime.now()

    logger.info("------------------------------------------")
    logger.info(f"RUN DONE. RETVAL: {retval} \n\n")

    return retval, start_time, end_time, lines


class DockerAutomation(object):

    def __init__(self, images: Dict[str, ImageInfo]):  # like "ejana-centos7-prereq"
        self.operation_logs: List[dict] = []
        self.images_by_name = images        
        self.check_deps = True
        self.no_cache = False
        self.push_after_build = True
        self.tag_latest = False
        self.built_images_by_name = {}

    def _append_log(self, op, name, ret_code, start_time, end_time, output):
        """Saves data to specially formatted record"""
        duration = end_time - start_time
        self.operation_logs.append({'op':op,
                                    'name': name,
                                    'ret_code': ret_code,
                                    'start_time': start_time,
                                    'start_time_str': start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    'end_time': end_time,
                                    'end_time_str': end_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    'duration': duration,
                                    'duration_str': str(duration)[:9],
                                    'output': output})

    def _build_image(self, image: ImageInfo):
        """
            docker build --tag=ejana-centos7-prereq .
            docker tag ejana-centos7-prereq eicdev/ejana-centos7-prereq:latest
            docker push eicdev/ejana-centos7-prereq:latest
        """
        # Check if we built dependency
        if self.check_deps:
            if image.depends_on and image.depends_on not in self.built_images_by_name.keys():
                message = f"The image {image.name} depends on {image.depends_on} which has not been built. " \
                          f"Run this script with check-deps=false in order to force {image.name} building"
                logger.error(message)

                # Save it to the logs
                self._append_log('check', image.full_name,  1, datetime.now(), datetime.now(), [message])                
                return

        # no-cache flag given?
        no_cache_str = "--no-cache" if self.no_cache else ""

        # RUN DOCKER BUILD COMMAND
        logger.debug(f"image.path = {image.path}")

        os.chdir(image.path)
        retval, start_time, end_time, output = _run(f"docker build {no_cache_str} {image.flags} --tag={image.full_name} .")

        # Log the results:
        self._append_log('build', image.full_name, retval, start_time, end_time, output)

        if retval:
            logger.error(f"(! ! !)   ERROR   (! ! !) build op return code is: {retval}")
            return
        
        # Add to built images list built 
        self.built_images_by_name[image.aslias]=image
        
        # Tag this build as latest
        if self.tag_latest:
            retval, start_time, end_time, output = _run(f"docker tag {image.full_name} {image.tag_latest_name}")

            # Log the results:
            self._append_log('tag-latest', image.tag_latest_name, retval, start_time, end_time, output)
            
            if retval:
                logger.error(f"(! ! !)   ERROR   (! ! !) tag latest return code is: {retval}")

        # Push image after built
        if self.push_after_build:
                self.push(image)

    def build(self, image_name: str):
        self._build_image(self.images_by_name[image_name])

    def build_all(self):
        images = self.images_by_name.values()
        for image in images:
            self._build_image(image)

    def push(self, name_or_image):
        if isinstance(name_or_image, ImageInfo):
            image = name_or_image
        else:
            image = self.images_by_name[name_or_image]
        os.chdir(image.path)
        retval, start_time, end_time, output = _run(f"docker push {image.full_name}")

        # Log the results:
        self._append_log('push', image.full_name, retval, start_time, end_time, output)       

        if retval:
            logger.error(f"(! ! !)   ERROR   (! ! !) PUSH operation return code is: {retval}")

        # Push also the latest branch
        if self.tag_latest:
            retval, start_time, end_time, output = _run(f"docker push {image.tag_latest_name}")

            # Log the results:
            self._append_log('push-latest', image.tag_latest_name, retval, start_time, end_time, output)
            
            if retval:
                logger.error(f"(! ! !)   ERROR   (! ! !) tag latest return code is: {retval}")


    def push_all(self):
        for name in self.images_by_name.keys():
            self.push(name)

def main():
    def print_images():
        for image_set_name, image_set in image_chains.items():
            print(image_set_name)
            for image in image_set:
                print(f'   {image}')

    # Argument parsing
    cwd = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-cache", help="Use docker --no-cache flag during build", action="store_true")
    parser.add_argument("--tag", help="Set version tag name. latest is set by default", default='dev')
    parser.add_argument("--push", action="store_true", help="If true - push images if built successfully")
    parser.add_argument("--latest", action="store_true", help="If true - also tag this image as 'latest' tag")
    parser.add_argument("--log-to-file", action="store_true", help="Log to file instead of stdout")
    parser.add_argument("--check-deps", type=bool, help="Check that dependency is built", default=True)
    parser.add_argument("-j", "--jobs", type=int, default=cpu_count, help="Number of parallel jobs")

    parser.add_argument("command", type=str, help="'list' = list known images. 'devops', 'eic', 'eic-ubuntu' 'all' = build set of images. exact image name = build that image")
    args = parser.parse_args()

    configure_default_images(args.tag, args.jobs)

    if args.log_to_file:

        # create file handler which logs even debug messages
        fh.setLevel(logging.DEBUG)
        ch.setLevel(logging.INFO)
        logger.addHandler(fh)
    else:

        ch.setLevel(logging.DEBUG)


    # add the handlers to the logger
    
    logger.addHandler(ch)


    if args.command == 'list':
        print_images()
        exit(0)

    if args.command in ['devops', 'eic', 'all']:
        single_image_build = False
        automation = DockerAutomation(image_chains[args.command])
    else:
        single_image_build = True
        automation = DockerAutomation(image_chains['all'])
        automation.check_deps = False

    automation.no_cache = args.no_cache
    automation.push_after_build = args.push
    automation.tag_latest = args.latest

    if single_image_build:
        automation.build(args.command)
    else:
        automation.build_all()

    logs = automation.operation_logs

    os.chdir(cwd)

    error_code = 0

    logger.info('SUMMARY:')
    logger.info("{:<12} {:<38} {:<9} {:<11} {:<21} {:<21}"
          .format('ACTION', 'IMAGE NAME', 'RETCODE', 'DURATION', 'START TIME', 'END TIME'))
    for log in logs:
        logger.info("{op:<12} {name:<38} {ret_code:<9} {duration_str:<11} {start_time_str:<21} {end_time_str:<21}".format(**log))
        if log['ret_code'] !=0:
            error_code = log['ret_code']

    #import json
    #with open('result.json', 'w') as outfile:
    #    json.dump(logs, outfile, indent=4, ensure_ascii=False)
    return error_code, logs

if __name__ == '__main__':
    error_code, _ = main()

    if error_code != 0:
        exit(error_code)
        
