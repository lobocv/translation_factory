import logging
from factory import build


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info('Translation Factory build started')


locale_code_dict = {
                    'Spanish': 'es_ES',
                    'German': 'de_DE',
                    'French': 'fr_FR',
                    'Czech': 'cs_CZ',
                    'Polish': 'pl_PL',
                    'Dutch': 'nl_NL',
                    'Italian': 'it_IT',
                    'Turkish': 'tr_TR',
                    'Greek': 'el_GR',
                    'Russian': 'ru_RU',
                    'Bulgarian': 'bg_BG',
                    'Romanian': 'ro_RO',
                    'Hungarian': 'hu_HU',
                    'Simplified Chinese': 'Simplified Chinese'
                    }



build_dir = 'path_to_place_output_translations'
source_dir = "path_to_grab tags_from",

build(directory=source_dir,
      application_name='MyApp',
      locale_codes=locale_code_dict,
      build_dir=build_dir,
      include_patterns=["(.+).py$"],
      exclude_patterns=[".*eventdispatcher.*"],
      mo_name='MyApp')
