#!/bin/env python3
# -*- coding: utf-8 -*-

# parse_msg variables
OCR_HOST = 'ocr.test.local'
IMG_HTTP_HOST = 'images.test.local'
TIKA_HOST = 'tika.test.local'
ES_SERVER = 'elk.test.local'
ES_AUTH = ('elastic', 'changeme')
ES_INDEX_NAME = 'test'
PATTERN_THREASHOLD = 2
REMOTE_OCR = True
OCR_LANG = 'tur'
ACTION = {}
ACTION['AUDIT'] = 100
ACTION['BLOCK'] = 1

# parse_server variables
HOST = 'parser.test.local'
PORT = 1235
MAX_REQUESTS = 10
PATTERN_FILE = './PATTERNS'
EML_MOUNT = '/var/spool/emailrelay'
