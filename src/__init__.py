import sys
from os.path import dirname

# This allows imports to function correctly inside the docker container and for pytest
sys.path.append(dirname(__file__))
