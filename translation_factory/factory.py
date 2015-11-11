__author__ = 'clobo'

import logging
import os
import shutil
import glob
import collections
import csv

from tags import extract_tags, test_tag_redundancy
from po_to_csv import po_to_csv
from csv_to_po import csv_to_po

LOCALE_CODES = {'Spanish': 'es_ES', 'German': 'de_DE', 'French': 'fr_FR'}


def build(directory, application_name, locale_codes_dict, build_dir, include_patterns=None, exclude_patterns=None,
          clean=False):

    """
    1. Extract tags into .po
    2. Convert .po to .csv
    3. Merge with any existing .csv files that contain translations
    4. Convert to .po
    5. Compile .po

    :param directory:
    :param application_name:
    :param locale_codes_dict:
    :param build_dir:
    :param include_patterns:
    :param exclude_patterns:
    :param clean:
    :return:
    """


    print 'Building translations for %s' % application_name
    if not os.path.isdir(build_dir):
        logging.info('Creating build directory: %s' % build_dir)
        os.makedirs(build_dir)
    else:
        logging.info('Build directory exists: %s' % build_dir)
        logging.info('Translation tables will be updated and merged whenever possible using existing tables')

    po_template = os.path.join(build_dir, 'messages.po')
    if os.path.isfile(po_template):
        os.remove(po_template)

    po_template = extract_tags(directories=directory,
                               pofile_path=os.path.join(build_dir, 'messages.po'),
                               include_patterns=include_patterns,
                               exclude_patterns=exclude_patterns)

    if po_template is None:
        logging.error('Translation build failed at extracting tags. Aborting.')
        return False
    try:
        redundancy_warnings = test_tag_redundancy(po_template)
    except Exception as e:
        print 'Tag redundancy check failed. See log for details.'
        logging.error(e)

    csv_template = po_to_csv(po_template, os.path.join(build_dir, 'messages.csv'))
    if csv_template is None:
        logging.error('Translation build failed at converting to csv. Aborting.')
        return False

    for locale, code in locale_codes_dict.iteritems():
        logging.info('Creating translation for locale {} - {}'.format(locale, code))
        # Create a directory for the locale
        locale_dir = os.path.join(build_dir, code)
        if not os.path.isdir(locale_dir):
            os.makedirs(locale_dir)

        # Copy the csv template for the application over if a csv does not already exist, otherwise use the existing csv
        # but add any new entries that may require translating
        locale_csv_path = os.path.join(locale_dir, "{} - {}.csv".format(application_name, locale))
        if os.path.isfile(locale_csv_path):
            # Rename the populated csv that already exists to a temporary file
            os.rename(locale_csv_path, locale_csv_path + '.temp')
            # Copy the template (which may have more/newer entries than the existing populated csv)
            shutil.copy2(csv_template, locale_csv_path)
            # Merge the existing csv into the template to ensure the new entries are transferred
            merge_csv(locale_csv_path + '.temp', locale_csv_path)
        else:
            shutil.copy2(csv_template, locale_csv_path)

        # Merge existing / already known translations into the csv
        print 'Atempting to merge existing tables..'
        for existing_translations in glob.glob(os.path.join(locale_dir, '*' + locale + '.csv')):
            if existing_translations == locale_csv_path:
                continue
            merges = merge_csv(existing_translations, locale_csv_path)
            print "{} entries found in {}.".format(merges, existing_translations)

        print 'Generating po file..'
        locale_po_file = os.path.join(locale_dir, application_name + '.po')
        csv_to_po(locale_csv_path, locale_po_file)

    if clean:
        os.remove(po_template)
        os.remove(csv_template)


def merge_csv(from_file, into_file):
    """
    Merge translations from existing from_file csv into into_file.

    :param from_file: File to look for existing translations
    :param into_file:  File to update with existing translations

    :return: Number of successful merge entries.
    """
    cells = collections.OrderedDict({})
    merge_entries = 0
    with open(into_file, 'r') as f1:
        f1_reader = csv.reader(f1)
        header1 = f1.readline()
        for line1 in f1_reader:
            phrase, translation = line1[:2]
            cells[phrase] = translation

    with open(from_file, 'r') as f2:
        header2 = f2.readline()
        csv_reader = csv.reader(f2)
        for line2 in csv_reader:
            phrase, translation = line2[:2]
            if translation and phrase in cells and cells[phrase] == '':
                merge_entries += 1
                cells[phrase] = translation

    with open(into_file, 'w') as f1:
        f1.write(header1)
        csv_writer = csv.writer(f1)
        for phrase, trans in cells.iteritems():
            csv_writer.writerow((phrase, trans))

    return merge_entries

if __name__ == '__main__':

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.info('test')
    locale_code_dict = {'Spanish': 'es_ES', 'German': 'de_DE', 'French': 'fr_FR'}

    # build("/home/local/SENSOFT/clobo/projects/conquest",
    #       'PygameConquest',
    #       locale_code_dict,
    #       '/home/local/SENSOFT/clobo/temp/translation_build',
    #       include_patterns=["(.+).py$"])

    build("/home/local/SENSOFT/clobo/projects/lmx",
          'PygameLMX',
          locale_code_dict,
          '/home/local/SENSOFT/clobo/temp/translation_build',
          include_patterns=["(.+).py$"],
          exclude_patterns=[".*eventdispatcher.*"])