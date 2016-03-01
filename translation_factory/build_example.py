import logging
from factory import build


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info('Translation Factory build started')


locale_code_dict = {'Spanish': 'es_ES', 'German': 'de_DE', 'French': 'fr_FR'}

BUILD_CONQUEST = 0
BUILD_LMX200_RD1500 = 1
BUILD_LMX100_RD1100 = 0


if BUILD_CONQUEST:
    build_dir = '/home/local/SENSOFT/clobo/projects/conquestV2/lib/PygameWidgets/PygameWidgets/resources/translations'
    source_dir = "/home/local/SENSOFT/clobo/projects/conquestV2",
    build(directory=source_dir,
          application_name='Conquest 100',
          locale_codes_dict=locale_code_dict,
          build_dir=build_dir,
          include_patterns=["(.+).py$"],
          exclude_patterns=[".*eventdispatcher.*"],
          mo_name='Conquest 100')

if BUILD_LMX200_RD1500:
    build_dir = '/home/local/SENSOFT/clobo/projects/lmx/lib/PygameWidgets/PygameWidgets/resources/translations'
    source_dir = "/home/local/SENSOFT/clobo/projects/lmx"
    build(directory=source_dir,
          application_name='LMX200',
          locale_codes_dict=locale_code_dict,
          build_dir=build_dir,
          include_patterns=["(.+).py$"],
          exclude_patterns=[".*eventdispatcher.*"],
          mo_name='LMX200')

if BUILD_LMX100_RD1100:
    build_dir = '/home/local/SENSOFT/clobo/projects/lmx/lib/PygameWidgets/PygameWidgets/resources/translations'
    source_dir = "/home/local/SENSOFT/clobo/projects/lmx"
    build(directory=source_dir,
          application_name='LMX100',
          locale_codes_dict=locale_code_dict,
          build_dir=build_dir,
          include_patterns=["(.+).py$"],
          exclude_patterns=[".*eventdispatcher.*"],
          mo_name='LMX100')