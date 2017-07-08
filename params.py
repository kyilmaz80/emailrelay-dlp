#!/bin/env python3
# -*- coding: utf-8 -*-

# parse_msg variables
IMG_PATH = '/images'
FIRST_FIVE = 5
OCR_THRESHOLD = 5
OCR_HOST = 'image-parser'
OCR_PORT = '5000'
IMG_HTTP_HOST = 'images-web'
IMG_HTTP_PORT = '8000'
TIKA_HOST = 'tika-parser'
ES_SERVER = 'elasticsearch'
ES_AUTH = ('elastic', 'changeme')
ES_INDEX_NAME = 'test'
PATTERN_THREASHOLD = 2
REMOTE_OCR = True
OCR_LANG = 'tur'
ACTION = {}
ACTION['AUDIT'] = 100
ACTION['BLOCK'] = 1

# parse_server variables
HOST = 'emailrelay-parser'
PORT = 1235
MAX_REQUESTS = 10
PATTERN_FILE = './PATTERNS'
EML_MOUNT = '/var/spool/emailrelay'
