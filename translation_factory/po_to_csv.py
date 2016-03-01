__author__ = 'clobo'

import os
import sys
import csv
import argparse

from itertools import chain


def po_to_csv(po_path, csv_path, sort=True):
    """
    Convert the po file to a csv file that can be sent to the translator
    :param po_path: path to the po file
    :param csv_path: output path to the csv

    :return: csv_path if successful else None
    """
    # If arguments are not the right file type then the program exits.
    po_path = os.path.splitext(po_path)[0] + '.po'

    if not os.path.isfile(po_path):
        return ValueError('No po file "%s" exists' % po_path)

    msgid = []
    msgstr = []
    msgid_sorted = []
    count = 0
    with open(po_path, 'r') as poFile:
        with open(csv_path, 'w') as _csv:
            csvFile = csv.writer(_csv)
            append_to = None
            for line in chain(poFile, '\n'):
                # Decide if the line is part of the phrase or the translation and assign it to the corresponding list
                if line.startswith('msgstr'):
                    append_to = msgstr
                elif line.startswith('msgid'):
                    append_to = msgid

                if append_to is not None:
                    append_to.append(line)

                if line == '\n':
                    append_to = None
                    count += 1
                    if count == 1:
                        pass
                    else:
                        if count == 2:
                            csvFile.writerow(('Original Text', 'Translation', 'Additional Comments'))
                        t = ''.join([m.strip('"') for m in msgid])
                        t = t.replace('msgid "', '')
                        t = t.replace('"\n', '')
                        if sort:
                            msgid_sorted.append(t)
                        else:
                            csvFile.writerow((t, '', '', '' ))
                    del msgid[:]
                    del msgstr[:]

            if sort:
                msgid_sorted.sort()
                for t in msgid_sorted:
                    csvFile.writerow((t, '', '', '' ))

    return csv_path


if __name__ == '__main__':

    # Describe what this script does, and the parameters that are entered.
    parser = argparse.ArgumentParser(
        description='''The purpose of this program is to format a .po file into a .csv file, so that the translator
                       can enter the translations into excel. ''')
    parser.add_argument('po_path',
                        nargs='*',
                        type=str,
                        default='messages.po',
                        help='This is the file that information is read from.')

    parser.add_argument('csv_path',
                        nargs='*',
                        default='messages.csv',
                        help='This is the name of the file that is created or overwritten.')

    args = parser.parse_args()

    # If there are not enough arguments then exit.
    if len(sys.argv) != 3:
        print "Incorrect number of arguments. See help\n\n"
        parser.print_help()
        exit()

    csv_path = str(sys.argv[1])  # This argument stores the name of the first argument (The file to be copied)
    po_path = str(sys.argv[2])  # This argument stores the name of the second argument (The file to be created))

    if po_to_csv(po_path, csv_path):
        print "Successfully created {} from {}".format(csv_path, po_path)
