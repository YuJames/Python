#!/usr/bin/env python3

"""PyPDF2 ATP (acceptance test procedure) pdf parsing.

This module uses PyPDF2 v.1.26.0 to parse ATP pdf files at B/E Aerospace. The
purpose is to encourage data gathering.

Arguments:
    argv[1]: pdf file path

ToDo:
    compare this and data analysis boiler plates are the same
    
"""

#~~~~  IMPORTS  ~~~~#
import PyPDF2
import re

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#
_REQUIREMENT = "_required"
_MEASUREMENT = "_measured"

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#

#~~~~  PUBLIC CLASSES  ~~~~#

#~~~~  PRIVATE FUNCTIONS  ~~~~#

#~~~~  PUBLIC FUNCTIONS  ~~~~#

#~~~~  MAIN  ~~~~#
file_path = r"C:\Users\James\Google Drive\Etc\Testing\test_pdf_file_formatted.pdf"

# read pdf
pdf_obj = PyPDF2.PdfFileReader(file_path)

# parse pdf
forms = pdf_obj.getFormTextFields()
form_names = forms.keys()

print(type(PyPDF2.pdf))

# find test forms
test_pattern = re.compile("^test\d+$")
required_pattern = re.compile("(?P<min>\d+)-(?P<max>\d+)")

test_list = []
for key in form_names:
    match = test_pattern.search(key)
    # found test
    if match != None:
        test_list.append(match.group(0))
        
# find tests' requirement
for test in test_list:
    print("TEST: {}".format(forms[test]))
    match = required_pattern.search(forms[test + _REQUIREMENT])
    min = float(match.group("min"))
    max = float(match.group("max"))
    print("  REQUIREMENT IS MIN: {}, MAX: {}".format(min, max))
    measured = float(forms[test + _MEASUREMENT])
    status = "PASSED" if measured >= min and measured <= max else "FAILED"
    print("  TEST {} WITH VALUE OF {}".format(status, measured))
    
#~~~~  DEAD CODE  ~~~~#