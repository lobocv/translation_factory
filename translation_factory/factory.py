__author__ = 'clobo'

import logging
import os
import shutil
import glob
import collections
import csv

from functools import partial

from tags import extract_tags, test_tag_quality
from po_to_csv import po_to_csv
from csv_to_po import csv_to_po
from combine_tables import create_master_table

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ARABIC_TRANSFORM(text, locale):
        t = text.decode('utf-8')
        # Converts individual characters to their word respresentation
        reshaped = arabic_reshaper.reshape(t)
        # To prevent escaped quotes from being reversed, reverse them ahead of time so they get re-reversed
        reshaped = reshaped.replace('\\"', '"\\')
        reshaped = reshaped.replace("\\'", "'\\")
        if locale == 'ar_AE':
            # Reverse the string (Right to Left)
            T = get_display(reshaped)
        else:
            T = reshaped
        converted = T.encode('utf-8')
        return converted

except ImportError as e:
    ARABIC_TRANSFORM_LIBRARY = None


def build(directory, application_name, locale_codes, build_dir, include_patterns=None, exclude_patterns=None,
          clean=True, src_lang='python', mo_name=None, sort_messages=True, **kwargs):

    """
    1. Extract tags into .po
    2. Convert .po to .csv
    3. Merge with any existing .csv files that contain translations
    4. Convert to .po
    5. Compile .po

    :param directory: Directory to recursively search for tags
    :param application_name: Name of the application being translated
    :param locale_codes: List of tuples of the form (language, locale_code for languages that require translating)
    :param build_dir: Directory to build to
    :param include_patterns: regex patterns of files to include in search for tags
    :param exclude_patterns: regex patterns of files to exclude in search for tags
    :param clean: clean intermediate files
    :return: Success or fail
    """

    print 'Building translations for %s' % application_name
    if mo_name is None:
        mo_name = application_name
    if not os.path.isdir(build_dir):
        logging.info('Creating build directory: %s' % build_dir)
        os.makedirs(build_dir)
    else:
        logging.info('Build directory exists: %s' % build_dir)
        logging.info('Translation tables will be updated and merged whenever possible using existing tables')

    # Search through the source code and find all the tags to put into a po file
    po_template = os.path.join(build_dir, 'messages.po')
    if os.path.isfile(po_template):
        os.remove(po_template)
    print 'Extracting tags.. this may take several minutes.'
    po_template = extract_tags(directories=directory,
                               pofile_path=os.path.join(build_dir, 'messages.po'),
                               include_patterns=include_patterns,
                               exclude_patterns=exclude_patterns,
                               src_lang='python')
    files_to_clean = [po_template]
    if po_template is None:
        logging.error('Translation build failed at extracting tags. Aborting.')
        return False

    # Go through the template and check for any redundancies in the tags
    # This doesn't fix anything, just notifies you to manually change the tags.
    try:
        redundancy_warnings = test_tag_quality(po_template)
    except Exception as e:
        print 'Tag redundancy check failed. See log for details.'
        logging.error(e)

    # Conver the po template into a csv for easier modification / comparison
    csv_template = po_to_csv(po_template, os.path.join(build_dir, 'messages.csv'), sort=sort_messages)
    files_to_clean.append(csv_template)
    if csv_template is None:
        logging.error('Translation build failed at converting to csv. Aborting.')
        return False

    # For each language we want to generate a translation for, create a copy of the po template,
    # then fill the template with any words that have already been translated in previous po files.
    # After merging the po files, compile the merged po into the mo file
    #
    # Note:
    # Tags that have no translations will be blank in the csv file, it is up to you to fill this csv
    # in place. Once you do that, run this same script again and it will compile the added phrases into
    # the mo.

    for locale, code in locale_codes:
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
            files_to_clean.append(locale_csv_path + '.temp')
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
        po_name = application_name + ' - %s.po' % locale
        locale_po_file = os.path.join(locale_dir, po_name)
        if code in ('fa_IR', 'ar_AE'):
            if ARABIC_TRANSFORM is None:
                print 'Warning: Cannot import arabic-reshaper or python-bidi. These libraries are required ' \
                      'in order to reshape arabic characters into their word representation and to ' \
                      'reverse the strings (right to left language)'
                csv_transform = None
            else:
                csv_transform = partial(ARABIC_TRANSFORM, locale=code)
        else:
            csv_transform = None
        csv_to_po(locale_csv_path, locale_po_file, sort=sort_messages, transform=csv_transform)

        print 'Compiling po file..'
        if not os.path.isdir(os.path.join(locale_dir, 'LC_MESSAGES')):
            os.makedirs(os.path.join(locale_dir, 'LC_MESSAGES'))
        ec = os.system("msgfmt -o '{0}/LC_MESSAGES/{1}.mo' '{0}/{2}'".format(locale_dir, mo_name, po_name))
        if ec != 0:
            print 'Compiling failed. Please ensure msgfmt is installed.'

    print 'Creating master table.'
    create_master_table(build_dir, application_name, locale_codes)

    if clean:
        print 'Cleaning files..'
        for _f in files_to_clean:
            try:
                os.remove(_f)
            except OSError as e:
                logging.error(e)

    return True


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
        header1 = f1_reader.next()
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
        csv_writer = csv.writer(f1)
        csv_writer.writerow(header1)
        row = [''] * len(header1)
        for phrase, trans in cells.iteritems():
            row[0], row[1] = phrase, trans
            csv_writer.writerow(row)

    return merge_entries