import sys
import logging
import json
from factory import build

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info('Translation Factory build started')

args = sys.argv[1:]
if len(args) < 1:
    print "Build configuration file required"

config_file = args[0]

try:
    with open(config_file) as _f:
        config = json.load(_f)
    build(**config)
except Exception as e:
    logging.error(e)


