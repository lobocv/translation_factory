__author__ = 'clobo'

from datetime import datetime
import re
import os
import csv
import sys
import argparse

_re_python_str_placeholder = re.compile('%\d?\.?\d?[sbcdoxXneEfFgG]|{[A-z,0-9]*:?\d*[sbcdoxXneEfFgG]?}')


def csv_to_po(csv_path, po_path, sort=True, src_lang='python', transform=None):
    """
    Convert a csv file into a po file.

    :param csv_path: path to csv file
    :param po_path: path to output po file
    :param sort: sort the strings alphabetically
    :param src_lang: source language (used to check format strings are not altered for python)
    :param transform: function applied to csv translation before writing to po file
                      (used for right to left / reshaped languages such as Arabic, Farsi)
    :return:
    """

    if not (csv_path.endswith('.csv') or csv_path.endswith('.xlsx')):
        raise ValueError('csv_path must be have extension .csv or .xlsx')
    place_holder_errors = 0
    po_path = os.path.splitext(po_path)[0] + '.po'

    try:
        language = re.match(".* - (.+)\.(csv|xlsx)", csv_path).group(1)
    except IndexError:
        language = 'LANGUAGE'
    with open(po_path, 'w') as poFile:
        # Add header information.
        poFile.write(''
                     '# GENERATED .po FILE FROM translation_factory\n'
                     '# https://github.com/lobocv/translation_factory\n'
                     '# Copyright (C) 2015 Calvin Lobo. All rights reserved\n'
                     '#\n'
                     'msgid ""\n'
                     'msgstr ""\n'
                     '"Project-Id-Version: PACKAGE VERSION\\n"\n'
                     '"POT-Creation-Date: {dt}\\n"\n'
                     '"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
                     '"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"\n'
                     '"Language-Team: \\n"\n'
                     '"Language: {lang}\\n"\n'
                     '"MIME-Version: 1.0\\n"\n'
                     '"Content-Type: text/plain; charset=UTF-8\\n"\n'
                     '"Content-Transfer-Encoding: ENCODING\\n"\n'
                     '"Generated-By: pygettext.py 1.5\\n"\n\n\n'.format(lang=language,
                                                                        dt=datetime.now().strftime('%d %B %Y, %I:%M %p'))
                     )

        if csv_path.endswith('.csv'):
            # Open the file writer and file reader
            with open(csv_path, 'r') as csvFile:
                csv_reader = csv.reader(csvFile)
                headers = csv_reader.next()
                if sort:
                    po_items = sorted((row[:2] for row in csv_reader), key=lambda x: x[0])
                else:
                    po_items = csv_reader
                # Write the information to the file.
                for row in po_items:
                    message, translation = row[:2]
                    if src_lang == 'python':
                        if translation:
                            if transform:
                                translation = transform(translation)
                            mph = set(_re_python_str_placeholder.findall(message))
                            tph = set(_re_python_str_placeholder.findall(translation))
                            if len(mph.symmetric_difference(tph)) > 0:
                                place_holder_errors += 1
                                print 'Warning. Placeholders do not match in %s translation table!' % language
                                print message + '\n' + translation
                                print 'Errors: %s' % ','.join(tph.difference(mph)) + '\n'

                    poFile.write('msgid "%s"\n' % message)
                    poFile.write('msgstr "%s"\n\n' % translation)

                if src_lang == 'python':
                    print '%d Place holder errors were found.' % place_holder_errors
        else:
            return False

    return True

if __name__ == '__main__':
    # Describe what this script does, and the parameters that are entered.
    parser = argparse.ArgumentParser(
        description='''The purpose of this program is to format a .csv file into a .po file, so that the spreadsheet
                        can be converted to a usable file format for the application. ''',
        epilog="""Last Revision: June 12th 2015""")
    parser.add_argument('filename1', nargs='*', type=str, default='messages.csv',
                        help='This is the file that information is read from.')
    parser.add_argument('filename2', nargs='*', default='messages.po',
                        help='This is the name of the file that is created or overwritten.')
    args = parser.parse_args()

    # If there are not enough arguments then exit.
    if len(sys.argv) != 3:
        print "Incorrect number of arguments. See help\n\n"
        parser.print_help()
        exit()


    csv_path = str(sys.argv[1])  # This argument stores the name of the first argument (The file to be copied)
    po_path = str(sys.argv[2])  # This argument stores the name of the second argument (The file to be created))

    passed = csv_to_po(csv_path, po_path)

    if passed:
        print "{} was successfully created from {}.".format(po_path, csv_path)