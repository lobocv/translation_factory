__author__ = 'clobo'

import os
import sys
import subprocess
import argparse
import logging
import re


def extract_tags(directories, pofile_path, include_patterns=None, exclude_patterns=None):
    """
    Recursively iterate through directories and extract gettext tags.
    :param directories: Directory or list of directories to iterate through
    :param pofile_path: Path to the write the po file to
    :param include_patterns: regex patterns of files to include
    :param exclude_patterns: regex patterns of files to exclude
    :return: path to the po file
    """
    if isinstance(directories, basestring):
       directories = (directories, )

    pofile_path = os.path.splitext(pofile_path)[0]
    for directory in directories:
        for top, dirs, files in os.walk(directory):
            for f in files:
                fullpath = os.path.join(top, f)
                skip = False
                # If no include patterns are provided, always call gettext on the file
                do_call = False if include_patterns else True

                # Exclude files that match the exclude_patterns regex
                if exclude_patterns:
                    for exc in exclude_patterns:
                        if re.match(exc, fullpath):
                            skip = True
                            break
                if skip:
                    continue

                if include_patterns:
                    for inc in include_patterns:
                        do_call = re.match(inc, fullpath)
                        if do_call:
                            break

                if do_call:

                    if os.path.isfile(pofile_path + '.po'):
                        call_args = ('xgettext', fullpath, '--join-existing', '-L', 'python', '--default-domain=%s' % pofile_path)
                        with open(pofile_path + '.po', 'r') as _po:
                            po_lines = _po.readlines()

                        for ii, line in enumerate(po_lines):
                            if "Content-Type" in line:
                                po_lines[ii] = line.replace("CHARSET", "ASCII")

                        with open(pofile_path + '.po', 'w') as _po:
                            _po.writelines(po_lines)

                    else:
                        # On the first call
                        call_args = ('xgettext', fullpath, '-L', 'python', '--default-domain=%s' % pofile_path)
                    logging.debug('Searching %s' % fullpath)
                    result = subprocess.call(call_args, stdout=sys.stdout, stderr=sys.stderr)

        return pofile_path + '.po'


def test_tag_redundancy(pofile_path):
    """
    Checks several conditions to reduce redundancy in the po file:

    - Checks for empty place holders, ie {} in str.format()
    - Checks for lines ending with \n
    - Checks for lines ending with :

    :param pofile_path: path to po file
    :return: number of warnings

    """
    pofile_path = os.path.splitext(pofile_path)[0] + '.po'
    warnings = 0
    re_empty_bracket = re.compile(r'\".*\{\}.*\"$')
    re_new_line_char = re.compile(r'\".*\\n\"$')
    re_ends_with_colon = re.compile(r'\".*:\"$')
    with open(pofile_path, 'r') as _po:
        for ii, line in enumerate(_po):
            if re.findall(re_empty_bracket, line):
                print "Empty placeholder in line {}: {}".format(ii, line.strip())
                warnings += 1
            if re.findall(re_new_line_char, line):
                print "New line character found in line {}: {}".format(ii, line.strip())
                warnings += 1
            if re.findall(re_ends_with_colon, line):
                print "Colon detected at the end of line {}: {}".format(ii, line.strip())
                warnings += 1

    print "%d Warnings found." % warnings
    return warnings

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory in which to search for _() tagged files")
    parser.add_argument("outfile", help="outpul po file path")
    parser.add_argument("--include_patterns", action='append', help="list of regex expressions for files to include")
    parser.add_argument("--exclude_patterns", help="list of regex expressions for files to exclude")
    args = parser.parse_args()

    po_path = os.path.splitext(args.outfile)[0] + '.po'
    if os.path.isfile(po_path):
        os.remove(po_path)
    extract_tags(directory=args.directory,
            pofile_path=args.outfile,
            include_patterns=args.include_patterns,
            exclude_patterns=args.exclude_patterns)
    test_tag_redundancy(po_path)
