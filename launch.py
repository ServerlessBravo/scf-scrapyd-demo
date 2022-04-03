import sys
import os

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)

from twisted.scripts.twistd import run
from os.path import join, dirname
from sys import argv


def main():
    argv[1:1] = ['-n', '-y', join(dirname(__file__), 'scf_txapp.py')]
    run()

if __name__ == '__main__':
    main()
