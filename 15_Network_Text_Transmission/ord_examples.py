#!/usr/bin/env python3

"""
python3 ord examples.

ord(c): Given a string representing one Unicode character, return an
integer representing the Unicode code point of that character.

hex(i): Given an integer, return a string corresponding to its
hexadecimal representation.

"""

print("ord('a') = {} ({})".format(ord('a'), hex(ord('a'))))
print("ord('b') = {} ({})".format(ord('b'), hex(ord('b'))))
print("ord('c') = {} ({})".format(ord('c'), hex(ord('c'))))

print( "ord('€') (Euro sign) = ", ord('€') )
print( "ord('€') (Euro sign) = ", hex(ord('€')) )

greek_omega_1 = "\N{GREEK SMALL LETTER OMEGA}"
greek_omega_2 = "\u03c9"

greek_Omega_1 = "\N{GREEK CAPITAL LETTER OMEGA}"
greek_Omega_2  = "\u03a9"

gk_O_1_ord = ord(greek_omega_1)
Gk_O_1_ord = ord(greek_omega_2)

print("Greek Small Omega ord = {} ({} hex)".format(gk_O_1_ord, hex(gk_O_1_ord)))
print("Greek Capital Omega ord = {} ({} hex)".format(Gk_O_1_ord, hex(Gk_O_1_ord)))

string_list = ["NETWORK", "₦Ɇ₮₩ØⱤ₭"]
for s in string_list:
    for c in s:
        print("{} {} ({})".format(c, ord(c), hex(ord(c))))


