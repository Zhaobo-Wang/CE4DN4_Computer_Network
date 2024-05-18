#!/usr/bin/env python3

"""
Unicode encode and decode examples.

"""

print()

greek_str = 'αβψδεφγηιξκλμνοπρστθωςχυζ'
print("greek_str = ", greek_str)
print()

greek_str_utf8 = greek_str.encode('utf-8')
print("greek_str (utf-8) = ", greek_str_utf8)
print()

greek_str_utf16 = greek_str.encode('utf-16-le')
print("greek_str (utf-16-le) = ", greek_str_utf16)
print()

greek_str_utf32 = greek_str.encode('utf-32-le')
print("greek_str (utf-32-le) = ", greek_str_utf32)
print()

greek_str_utf8_decoded = greek_str_utf8.decode('utf-8')
print("greek_str_utf8_decoded = ", greek_str_utf8_decoded)
print()

greek_str_utf16_decoded = greek_str_utf16.decode('utf-16-le')
print("greek_str_utf16-le_decoded = ", greek_str_utf16_decoded)
print()

greek_str_utf32_decoded = greek_str_utf32.decode('utf-32-le')
print("greek_str_utf32-le_decoded = ", greek_str_utf32_decoded)

print()




