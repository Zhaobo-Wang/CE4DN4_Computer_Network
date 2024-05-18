#!/usr/bin/env python3

"""
python3 chr examples.

chr(i) returns the string representing a character whose Unicode code
point is the integer i.

"""

# Unicode string literals
greekOmega_1 = "\N{GREEK CAPITAL LETTER OMEGA}"
greekOmega_2  = "\u03a9"

print("greekOmega_1 = ", greekOmega_1)
print("greekOmega_2 = ", greekOmega_2)

greek_str = "\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8"
print("greek_str = ", greek_str)

greek_str_2 = "αβψδεφγηιξκλμνοπρστθωςχυζ"
print("greek_str_2 = ", greek_str_2)

print("chr(937) = ", chr(937))
print("chr(0x3a9) = ", chr(0x3a9))

print('The Greek letter for capital omega: ' + chr(0x3a9))
print('The Greek letter for capital omega: \u03a9')




