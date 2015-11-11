__author__ = 'clobo'

from openpyxl import load_workbook
from datetime import datetime
import re
import os
import sys
import argparse


def csv_to_po(csv_path, po_path):
    if not (csv_path.endswith('.csv') or csv_path.endswith('.xlsx')):
        raise ValueError('csv_path must be have extension .csv or .xlsx')

    po_path = os.path.splitext(po_path)[0] + '.po'

    try:
        language = re.match(".* - (.+)\.(csv|xlsx)", csv_path).group(1)
    except IndexError:
        language = 'LANGUAGE'
    with open(po_path, 'w') as poFile:
        # Add header information.
        poFile.write(''
                     '# GENERATED .po FILE FROM TABLE\n'
                     '# Copyright (C) 2015 Sensors and Software Inc. All rights reserved\n'
                     '# Calvin Lobo <clobo@sensoft.ca>, 2015\n'
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

                # Write the information to the file.
                while True:
                    newLine = csvFile.readline()

                    # If the .csv file is empty then exit the loop.
                    if newLine == '':
                        break

                    # Store the identifier (msgId).
                    # Note: When there is a comma in the sentence the first part of the .csv
                    # will be encased in double quotes.
                    if newLine.startswith('"'):
                        msgId = newLine[:newLine.find('"', 1) + 1] + '\n'
                        newLine = newLine[newLine.find('"', 1) + 2:]
                    else:
                        msgId = '"' + newLine[:newLine.find(',')] + '"\n'
                        newLine = newLine[newLine.find(',') + 1:]

                    # Store the translation (msgStr).
                    # Note: When there is a comma in the sentence the first part of the .csv
                    # will be encased in double quotes.
                    if newLine.startswith('"'):
                        msgStr = newLine[:newLine.find('"') + 1] + '\n'
                        newLine = newLine[newLine.find('"') + 2:]
                    else:
                        msgStr = '"' + newLine[:newLine.find(',')] + '"\n'
                        newLine = newLine[newLine.find(',') + 1:]

                    # Store the translators notes.
                    if newLine.startswith('"'):
                        notes = newLine[:newLine.find('"') + 1] + '\n'
                        newLine = newLine[newLine.find('"') + 2:]
                    else:
                        notes = newLine[:newLine.find(',')] + '\n'
                        newLine = newLine[newLine.find(',') + 1:]

                    # Write the information to the file.
                    poFile.write('#: ' + newLine)
                    poFile.write('# ' + notes)
                    poFile.write('msgid ' + msgId)
                    poFile.write('msgstr ' + msgStr)

                    # This newline character needs to be added for proper spacing.
                    poFile.write('\n')

        elif csv_path.endswith('.xlsx'):
            # Open the xlsx workbook
            wb = load_workbook(csv_path)
            ws = wb.active

            for row in ws.rows[1:]:
                values = ['', '', '', '']
                for i in range(4):
                    values[i] = row[i].value
                    if values[i] == None:
                        values[i] = ''

                poFile.write('#: "' + values[3] + '"\n')
                poFile.write('# "' + values[2] + '"\n')
                poFile.write('msgid "' + values[0] + '"\n')
                poFile.write('msgstr "' + values[1] + '"\n')
                poFile.write('\n')

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