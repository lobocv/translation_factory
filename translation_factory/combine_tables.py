import os
import csv
import itertools


def create_master_table(build_dir, application_name, locale_codes_dict, fmt='xlsx', outfile=None):

    if fmt not in ('xlsx', 'csv'):
        raise ValueError('format argument must either be xlsx or csv')

    if outfile is None:
        outfile = os.path.join(build_dir, 'all_translations.' + fmt)

    open_files = {}
    csv_readers = {}
    # Find all the language CSV files and open them
    print 'Searching for CSV tables.'
    for lang, locale_code in locale_codes_dict.iteritems():
        csv_path = os.path.join(build_dir, locale_code, "{} - {}.csv".format(application_name, lang))
        if os.path.isfile(csv_path):
            lang_header = "%s (%s)" % (lang, locale_code)
            open_files[lang_header] = open(csv_path, 'r')
            csv_readers[lang_header] = csv.reader(open_files[lang_header])
            header = csv_readers[lang_header].next()
            print '%s CSV found.' % lang_header

    print 'Combining tables for %s into a master table' % ', '.join(open_files.iterkeys())
    with open(outfile, 'w') as _csv:
        csvFile = csv.writer(_csv)
        outfile_headers = ['Original Text'] + open_files.keys() + ['Additional Comments']
        csvFile.writerow(outfile_headers)
        row = {'Additional Comments': ''}
        filecount = 0
        # Iterate through all the csv's one row at a time and combine them into one row in the master table
        for lang, csv_reader in itertools.cycle(csv_readers.iteritems()):
            filecount += 1
            try:
                original, translated, comment = csv_reader.next()
            except StopIteration as e:
                break
            if row.get('Original Text', None) is None:
                # If this was the first language in the iteration for this row, set it's original text column
                row['Original Text'] = original
                row[lang] = translated
            elif row['Original Text'] == original:
                # Add this csv's translation to the row
                row[lang] = translated
            else:
                print "Translation table's row for:\n" \
                      "'%s'\n" \
                      "does not correctly align with other CSVs. Skipping this row" % original
                continue
            # If there is a comment, add it to the other comments
            if comment:
                if row['Additional Comments']:
                    row['Additional Comments'] += '\n%s: %s' % (lang, comment)
                else:
                    row['Additional Comments'] = '%s: %s' % (lang, comment)

            if filecount == len(open_files):
                # We reached the end of the row, write the row and restart
                csvFile.writerow([row[c] for c in outfile_headers])
                filecount = 0
                row = {'Additional Comments': ''}

        for f in open_files.itervalues():
            f.close()
        print 'Master table is ready at %s' % outfile






