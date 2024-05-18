#!/usr/bin/env python3

import base64
import StringSamples

msg = "ABC"
msg = "ABCD"
msg = "ABCDE"
msg = "ABCDEF"

# msg = "Hello World!"
# msg = StringSamples.OCANADA
# msg = StringSamples.GREEK
# msg = "Man"
# msg = 'TTodd'

print("msg = ", msg)

# msg_base64_encoded = base64.b64encode(msg)
# print("msg_base64_encoded = ", msg_base64_encoded)

# msg_decoded = base64.b64decode(msg_base64_encoded)
# print("msg_decoded = ", msg_decoded)

msg_utf8_encoded = msg.encode('utf-8')
print("msg_utf8_encoded = ", msg_utf8_encoded) 

msg_utf8_base64_encoded = base64.b64encode(msg_utf8_encoded)
print("msg_utf8_base64_encoded = ", msg_utf8_base64_encoded)

msg_utf8_decoded = base64.b64decode(msg_utf8_base64_encoded)
print("msg_utf8_decoded = ", msg_utf8_decoded)

msg_decoded = msg_utf8_decoded.decode('utf-8')
print("msg_decoded = ", msg_decoded)



