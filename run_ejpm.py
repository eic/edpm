import sys
import os
import inspect

if __name__ == '__main__':

    # make sure 'python run_ejpm.py' command would work
    # this_dir = os.path.dirname(os.path.dirname(inspect.stack()[0][1]))
    # sys.path.insert(0, "this_dir")

    import ejpm

    # Run ejpm cli
    ejpm.ejpm_cli()
