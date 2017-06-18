#!/bin/env python3

import ../parse_msg
import sys
import os
from pprint import pprint

if len(sys.argv) > 1:
    EML_DIR = sys.argv[1]
eml_res = {}
exp_res = {}
if not os.path.exists(EML_DIR):
    print(EML_DIR, ' a ulasilamadi!')
    sys.exit(1)

# toplam dosyalar:
cnt = 0
fp = open('farklar', 'w')
for dirpath, dirnames, files in os.walk(EML_DIR):
    for name in files:
        # print("dir:", dirpath,"---", name)
        eml_file = os.path.join(dirpath, name)
        filename, file_extension = os.path.splitext(eml_file)
        # if file_extension == '.meta' or file_extension == '.tgz' :
        if file_extension != '.eml':
            continue
        # print(eml_file, "işleniyor.....")
        if os.path.isfile(eml_file):
            print(eml_file, "işleniyor.....")
            ret = parse_msg.main(os.path.join(dirpath, name))
            if 'dlp' in name or 'ho_' in name:
                exp_res[name] = 100
            else:
                exp_res[name] = 0
            eml_res[name] = ret
            if eml_res[name] != exp_res[name]:
                print(name, "icin eml_res ile exp_res degerleri farkli geldi!")
                fp.write(name + " icin eml_res ile exp_res degerleri" +
                         "farkli geldi!\n")
            cnt = cnt + 1
        else:
            print(name, "dosya değil!")
fp.close()
print('Toplam dosya sayisi: ', cnt)

with open('eml_res_sonuclar.txt', 'w') as out:
    pprint(eml_res, stream=out)
with open('exp_res_sonuclar.txt', 'w') as out:
    pprint(exp_res, stream=out)

