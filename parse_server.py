#!/bin/env python3
# -*- coding: utf-8 -*-

import socket
import parse_msg
import os
import sys
import re
import logging
import csv
from threading import Thread

"""
EmailRelay eml parse threaded server process
date 170607
"""
__author__ = "Koray YILMAZ"
__email__ = 'kyilmaz80@gmail.com'
__version__ = "1.13"

# config constants
HOST = 'parser.test.local'
PORT = 1235
MAX_REQUESTS = 10
PATTERN_FILE = './PATTERNS'
EML_MOUNT = '/mnt/nfs'


class SocketThread(Thread):
    """
    A Listening Socket Thread Per Client
    """
    def __init__(self, name, clientsocket, addr):
        super().__init__()
        self.name = name
        self.clientsocket = clientsocket
        self.addr = addr

    def recieve(self):
        def get_msg_fpath(str_path, nfs_mount):
            '''
            str_path: string return from emailrelay
            nfs_mount: email relay spool out folder
            '''
            eml_name = str_path.split('/')[-1]
            return os.path.join(nfs_mount, eml_name)
        SOCKET_BUFFER = 1024
        data = clientsocket.recv(SOCKET_BUFFER).decode()
        logger.info("Data: %s" % str(data))
        msg_fpath = str(data)
        msg_fpath = msg_fpath.rstrip()
        self.msg_path = get_msg_fpath(msg_fpath, EML_MOUNT)

    def send(self):
        ret_code = parse_msg.main(self.msg_path, patterns, regexes)
        # no match or match free to go
        msg = ''
        if ret_code == 0 or ret_code == 100:
            msg = 'ok' + '\r\n'
        elif ret_code == 1:
            msg = 'Mail Cannot Forward!' + '\r\n'
        else:
            pass
        logger.info('Sending the parse result to EmailRelay server...')
        self.clientsocket.send(msg.encode('ascii'))
        self.clientsocket.close()

    def run(self):
        self.recieve()
        self.send()


def load_patterns(file_path):
    """
    loads the patterns from csv file
    """
    patternsDict = {}
    try:
        with open(file_path, mode='r') as csvfile:
            reader = csv.reader(csvfile)
            patternsDict = {rows[0]: (rows[1], rows[2]) for rows in reader}
    except FileNotFoundError:
        logging.error("patterns file not found!")
    return patternsDict


logging.basicConfig(format='%(asctime)s:%(name)s:%(threadName)s:' +
                    '%(levelname)s:%(message)s', filemode='a',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info('Pattern tree generating only once')

# load patterns
patterns = load_patterns(PATTERN_FILE)
patternsList = [t[0] for t in patterns.values()]
regexes = [re.compile(p) for p in patternsList]

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
logger.info('Server socket opened...')

# bind to the port
try:
    serversocket.bind((HOST, PORT))
    logger.info('%s:%s bind done', HOST, PORT)
except Exception as e:
    logger.error('%s:%s bind failure!', HOST, PORT)
    sys.exit(1)

# queue up to 10 requests
serversocket.listen(MAX_REQUESTS)
while True:
    logger.info('------------------------------------------')
    logger.info('Server is waiting for data on port: %s', PORT)
    clientsocket, addr = serversocket.accept()
    logger.info("Got a connection from %s" % str(addr))
    sock_thread = SocketThread("Thread-" + str(addr[1]),
                               clientsocket, addr)
    sock_thread.start()
