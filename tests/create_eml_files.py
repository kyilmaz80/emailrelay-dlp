#!/bin/env python3

import sys
import os
import mimetypes
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

"""
Creates email eml messages from given attachment files
"""

if len(sys.argv) > 1:
    FILE_DIR = sys.argv[1]
    EML_DIR = sys.argv[2]
else:
    print('KULLANIM: ./create_eml_files.py <FILE_DIR> <ATTACH_DIR>')
    sys.exit(1)

if not os.path.exists(EML_DIR):
    print(EML_DIR, ' a ulasilamadi!')
    sys.exit(1)

# toplam dosyalar:
cnt = 0
for dirpath, dirnames, files in os.walk(FILE_DIR):
    for name in files:
        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer['Subject'] = 'MESSAGE ' + str(cnt)
        outer['To'] = 'test' + str(cnt) + '@test.local'
        outer['From'] = 'korayy@test.local'
        outer.preamble = 'MIME mail okuyucuda gozukmez.\n'

        attach_file = os.path.join(dirpath, name)
        filename, file_extension = os.path.splitext(attach_file)
        eml_file = os.path.join(EML_DIR, os.path.basename(filename) + '.eml')
        if os.path.isfile(attach_file):
            print(name, ' dosyasindan eml dosyasi', EML_DIR,
                  ' dizininde olusturuluyor..')
            path = os.path.join(dirpath, name)
            ctype, encoding = mimetypes.guess_type(path)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded
                # (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(path)
                # Note: we should handle calculating the charset
                msg = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(path, 'rb')
                msg = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(path, 'rb')
                msg = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(path, 'rb')
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(fp.read())
                fp.close()
                # Encode the payload using Base64
                encoders.encode_base64(msg)
            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment', filename=name)
            outer.attach(msg)
            with open(eml_file, 'w') as fp:
                fp.write(outer.as_string())
            # ret = parse_msg.main(path)
            # eml_res[name] = ret
            cnt = cnt + 1
        else:
            print(name, "dosya değil!")

print('Toplam dosya sayisi: ', cnt)
