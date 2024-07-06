import os
import re
import sys

# Ensure importing modules from local repo and not PyPI package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from LiveboxMonitor.__main__ import main

if __name__ == '__main__':
	sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
	sys.exit(main(True))
