# translation_factory
A workflow tool for creating and managing translation tables.

This module helps developers with internationalization and localization of their applications by following a typical
work flow for translating applications.

Workflow
--------

1. Extract tags from all source files into a .po file.

2. Convert the .po file to CSV format for better visibility. Create one .po file for each language.

3. Check if any phrases have already been translated in previous applications and update their translations into the CSV.

4. Examine the tagged phrases for any potential improvements. This checks phrases to see if they end with a colon or
new line character or have empty placeholders in them (in python, formatted strings with empty curly brackets {})

5. At this point the CSV can then be sent to be populated by the translator.

6. The CSV is converted into a .po file with the application's name (one for each language).

7. The .po files are compiled into a .mo file.

8. Insert the .mo files into your application and they can be translated!


Benefits of using translation_factory
-------------------------------------
Translations created by the translation_factory are designed to be continuously iterated upon. When starting from scratch
an empty CSV template is created. When this CSV is translated, it can replace the empty CSV template in the build directory.
This not only allows the build to create the .mo file which is the end-point of the factory, but it allows the next application
to use translations from the first. This greatly reduces the number of words you will need to translate for each application if
they share many common translatable strings.


Notes and Caveats
-----------------

This module was designed on linux using python and GNU gettext. In theory this module should work on
any programming language but it has only been tested on python.

translation_factory uses xgettext to extract tags from source code. In the future this can be swapped out to use any
tool that creates .po files.

translation_factory uses msgfmt to compile .po files into .mo files.

For Arabic and Farsi languages, [arabic_reshaper](https://github.com/mpcabd/python-arabic-reshaper) and [python-bidi](https://github.com/MeirKriheli/python-bidi) are required to combine individual characters to their 
word form as well as to convert to right-to-left.
