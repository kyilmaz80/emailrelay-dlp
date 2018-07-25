#!/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import datetime
from pdfrw import PdfReader
from tika import parser
from elasticsearch import Elasticsearch
from PIL import Image
from PIL import ImageFilter
import sys
import email
import re
import logging
import coloredlogs
import json
import socket
import copy
import os
import subprocess
import pyocr
import pyocr.builders
import requests
import csv
import params

"""
E-mail eml/str message parser
date 180725
"""
__author__ = 'KORAY YILMAZ'
__email__ = 'kyilmaz80@gmail.com'
__version__ = '1.05'


class EmailMessage(object):
    """
    Custom Email Message Parser Class for file eml
    """
    def __init__(self, message_fname='', message_string=''):
        """
        usage: EmailMessage(message_fname='filepath') or
               EmailMessage(message_string='data')
        :param message_fname: file path of message
        :param message_string: string contents of message
        """
        self.message_fname = message_fname
        self.message_string = message_string
        self.PARSE_FROM_EML = message_fname != ''
        self.PARSE_FROM_STR = message_string != ''
        self.parts = []
        # create email message object from message file or string
        if self.message_fname != '':
            try:
                with open(message_fname, encoding="utf-8", errors="surrogateescape") as fp:
                    logging.info(message_fname + ' isleniyor...')
                    self.message = email.message_from_file(fp)
            except FileNotFoundError:
                logging.error(message_fname + " not found!")
            # store also the string of message object if needed
            self.message_string = self.message.as_string()
        elif self.message_fname == '' and self.message_string != '':
            # if eml file not given, convert the string to the builtin email object
            self.message = email.message_from_string(self.message_string)
        else:
            pass

        self.message_id = self.message.get('Message-ID')
        self.message_from = self.message.get('from')
        self.message_to = self.message.get('to')
        self.message_subject = self.message.get('subject')

    def get_message(self):
        """
        Returns the message object
        :return: email message object
        """
        # self.message must be email obj
        assert isinstance(self.message, email.message.Message)
        return self.message

    def set_message_string(self):
        """
        updates the message string. must run after changing the message obj
        :return:
        """
        self.message_string = self.message.as_string()

    def export_message(self, file_name):
        """
        exports the message string to file
        :return: state
        """
        try:
            with open(file_name, 'w', newline='\r\n') as fp:
                logging.info("email message string added to %s", file_name)
                fp.write(self.message_string)
            return True
        except Exception as e:
            logging.error(e)
            logging.error(file_name + " file not found in export_message()")
            return False

    def search_body_content(self):
        """
        Return the contents of mail body
        :return: text content list of mail parts
        """

        def find_parent(lst, part_tuple):
            """
            finds the parent in mail tree
            :param lst: message part list
            :param part_tuple: tupple
            :return: parent of part message
            """
            if len(lst) == 0:
                return False
            elif lst[-1] == part_tuple:
                return True
            else:
                lst_copy = copy.copy(lst)
                lst_copy.pop()
                return find_parent(lst_copy, part_tuple)

        def tika_content(string, file_name,
                         serverEndPoint=u'http://' + params.TIKA_HOST + ':9998'):
            """
            converts the binary file to string via Apache Tika interface
            return converted string
            :param string: attachment as string
            :param file_name: attachment file name
            :param serverEndPoint: tika parse url
            :return:(content, contentType) tupple
            """

            def convert_to_pdf(file_path):
                """
                convert the file_path file to pdf via libreoffice
                libreoffice --headless --convert-to pdf file_path --outdir /tmp
                :param file_path: file path of pdf file
                :return: state of success
                """
                if not os.path.isfile(file_path):
                    logging.error('%s file may be not there or no permission',
                                  file_path)
                    return None
                try:
                    libre_exec = subprocess.check_output(['which', 'libreoffice'])
                    libre_exec = libre_exec.rstrip().decode()
                    subprocess.call([libre_exec, '--headless', '--convert-to', 'pdf',
                                     file_path, '--outdir', '/tmp'])
                    pdf_file = os.path.splitext(file_path)[0] + '.pdf'
                    logging.info('%s file converted as %s', file_path, pdf_file)
                    if os.path.isfile(pdf_file):
                        logging.info('%s file to pdf convert successful', file_path)
                        return True
                    else:
                        logging.info('%s pdf file not found', pdf_file)
                        return None
                except Exception as e:
                    logging.error(e)
                    logging.warning('LibreOffice package needed!')
                    return None

            def is_office_file(file_path):
                """
                office file type extension control wrapper func
                :param file_path: file path of office file
                :return: True if file_path is an office file
                """
                ext = os.path.splitext(file_path)[1]
                return any(ext in _ext for _ext in
                           ['.xlsx', '.docx', '.pptx', '.ppsx'])

            file_name = clean_str(file_name)
            try:
                parsed = parser.from_buffer(string, serverEndPoint)
            except Exception as e:
                logging.error(e)
                logging.error("tika parse sorunu")
                return None
            if type(parsed) is not dict:
                logging.error("tika verilen string i parse edemedi!")
                return None
            # for org.apache.tika.exception.TikaException: Unexpected RuntimeException
            # from org.apache.tika.parser.microsoft.OfficeParser convert doc to pdf
            # than tika content
            elif type(parsed) is dict and len(parsed) == 0 and \
                    is_office_file(file_name):
                attachment = '/tmp/' + file_name
                open(attachment, 'wb').write(string)
                res = convert_to_pdf(attachment)
                if res is None:
                    logging.warning('convert_to_pdf returned None!')
                    return None
                attachment_pdf = os.path.splitext(attachment)[0] + '.pdf'
                # if res and os.path.isfile(attachment_pdf):
                if res:
                    logging.info("%s file converted to pdf e and parsing via tika",
                                 file_name)
                    parsed = parser.from_file(attachment_pdf, serverEndPoint)
                    return parsed['content']
                else:
                    logging.error("%s pdf file open failure!", attachment_pdf)
                    return None
            elif type(parsed) is dict and len(parsed) == 0:
                logging.error('Tika parse problem. %s file could not be parsed via\
                              Tika', file_name)
                return None
            else:
                return (parsed['content'], parsed['metadata']['Content-Type'])

        def clean_str(mystr, str_rep='', removeNonUnicode=False):
            """
            removes the special characters in the str.
            :param mystr: a string
            :param str_rep: replace string chacter
            :param removeNonUnicode: boolean
            :return: modified string
            """
            if type(mystr) is str or mystr is not None:
                if removeNonUnicode:
                    return re.sub('\W+', str_rep, mystr)
                else:
                    return re.sub('[^A-Za-z0-9._]+', '', mystr)
            else:
                return mystr

        def remove_blank_lines(str_content):
            """
            removes the blank lines in string
            :param str_content: string content
            :return: "" if error occurred, removed string if no error
            """
            if type(str_content) is not str:
                logging.warning('str type is expected for str_content but %s type\
                                is recieved', type(str_content))
                return ""
            elif str_content is not None:
                # wierd email forward can occur sometimes if not cleaned
                # replace non unicode chars with ? char
                # return os.linesep.join([clean_str(s,' ? ',True) for s in
                # str_content.splitlines() if s])
                return os.linesep.join([s for s in str_content.splitlines() if s])
            else:
                return ""

        def get_attachment_content(part):
            """
            converts the binary content in the message part to text
            :param part: email message object part object
            :return: (content, contentType) tupple of attachment file string or None if error
            """
            sub_type = part.get_content_subtype()
            file_name = part.get_filename()
            if sub_type == 'octet-stream' or sub_type == 'pdf' or \
                    'officedocument' in sub_type or sub_type == 'msword' or \
                    'excel' in sub_type or 'opendocument' in sub_type:
                str_attachment = part.get_payload(decode=True)
                content_attachment_tupple = tika_content(str_attachment, file_name)
                if content_attachment_tupple is None:
                    logging.error("no data from tika!")
                    return None
                t1 = remove_blank_lines(content_attachment_tupple[0])
                t2 = content_attachment_tupple[1]
                return (t1, t2)
            else:
                return None

        def remote_ocr_content(files, lang):
            """
            gets the text content from image files remotely
            :param files: image files list
            :param lang: language tr, en, ...
            :return: ocr text content list from image files or None if error
            """
            ocr_url = 'http://' + params.OCR_HOST + ':' + params.OCR_PORT + '/v1/ocr'
            img_url = 'http://' + params.IMG_HTTP_HOST + ':' + params.IMG_HTTP_PORT

            def post_request(file_path):
                """
                wrapper helper function for making post request
                to remove server
                :param file_path: file path of image file
                :return: json data output or '' if error
                """
                file_name = os.path.basename(file_path)
                logging.info("file_name = %s", file_name)
                headers = {'Content-Type': 'application/json'}
                payload = {'image_url': img_url + '/' + file_name}
                try:
                    response = requests.post(ocr_url, data=json.dumps(payload),
                                             headers=headers)
                except OSError:
                    logging.error("%s ocr request problem!", params.OCR_HOST)
                    return ''
                json_data = json.loads(response.text)
                # logging.info("Json data: %s", json_data)
                if 'output' in json_data:
                    return json_data['output']
                else:
                    logging.error("%s ocr request result is not as expected,\
                                  image web server running?", params.OCR_HOST)
                    return ''

            if files is None or len(files) == 0:
                return None

            logging.info('trying to convert image to text...')
            content_list = []
            for img_file in files:
                txt = post_request(img_file)
                content_list.append(txt)
            return "\n".join(content_list)

        def ocr_content(files, lang):
            """
            gets the text content from image files locally
            :param files: file path of image file
            :param lang: language tr, en, ...
            :return: text ocr content
            """
            if files is None or len(files) == 0:
                return None
            tools = pyocr.get_available_tools()
            if len(tools) == 0:
                logging.warning("No OCR tool found")
                return None
            # logging.info("Tools : %s", ",".join(tools))
            tool = tools[0]
            logging.info("Will use tool '%s'" % (tool.get_name()))
            langs = tool.get_available_languages()
            logging.info("Available languages: %s" % ", ".join(langs))
            if lang in langs:
                logging.info("Will use lang '%s'" % (lang))
            else:
                logging.warning("tesseract-%s lang package not found.\
                                yum install tesseract-%s", lang)
                return None
            logging.info('trying to convert image to text...')
            content_list = []
            for img_file in files:
                try:
                    ifds = Image.open(img_file)
                    ifds.filter(ImageFilter.SHARPEN)
                except FileNotFoundError:
                    logging.warning('%s image file not found!', img_file)
                    continue
                logging.info('processing %s image file...', img_file)
                txt = tool.image_to_string(
                    ifds,
                    lang=lang,
                    builder=pyocr.builders.TextBuilder()
                )
                content_list.append(txt)
            return "\n".join(content_list)

        def extract_image_pdf(file_path):
            """
            extracts the embedded image in pdf file
            :param file_path: file path of pdf file
            :return: extracted image files list or None if error
            """
            def get_pdf_rotation(file_path):
                """
                returns pdf file rotation
                :param file_path: file path of pdf file
                :return: 0 or int value
                """
                file_name, file_extension = os.path.splitext(file_path)
                if not os.path.exists(file_path):
                    logging.error("%s path is not vaild!", file_path)

                if file_extension != '.pdf':
                    logging.error('%s is not a pdf file!', file_path)
                    return None

                reader = PdfReader(file_path)
                pg_rotation = 0
                for pg in reader.pages:
                    if pg.Rotate != 0 or pg.Rotate != '':
                        pg_rotation = pg.Rotate
                        break
                # for pdfs that have not Rotate attr
                # assume not rotated
                if pg_rotation is None:
                    return 0
                else:
                    return int(pg_rotation)

            def rotate_image(img_path, angle):
                """
                rotates the image with the given angle and save
                :param img_path: file path of image file
                :param angle: degree
                :return: if error return None
                """

                file_name, file_extension = os.path.splitext(img_path)
                # dir_name = os.path.dirname(img_path)

                if not os.path.exists(img_path):
                    logging.error("%s file path is not a valid path!", img_path)
                    return None
                im = Image.open(img_path)
                # out_path = os.path.join(dir_name,file_name+"_rotated"+file_extension)
                im.rotate(angle).save(img_path)

            def convert_to_jpg(files):
                """
                converts the pbm files list to jpg
                :param files: image files list
                :return:
                """
                for file in files:
                    im = Image.open(file)
                    t = os.path.splitext(file)
                    new_file = t[0] + '.jpg'
                    im.save(new_file)

            # END OF WRAPPER FUNCTIONS of search_body_content

            if not os.path.exists('/usr/bin/pdfimages'):
                # TODO: Apache pdfbox may be used
                logging.error("/usr/bin/pdfimages command not found!")
                return None

            pdf_name = clean_str(file_path.split('/')[-1].split('.')[0])
            img_root = params.IMG_PATH + '/' + '_img_' + pdf_name

            # get pdf page rotation xobj
            pdf_rotation = get_pdf_rotation(file_path)
            logging.info("pdf_rotation = %s", pdf_rotation)
            # check if is it neccessary to rotate image
            img_rotation = 0
            if type(pdf_rotation) == int and pdf_rotation != 0:
                logging.info("pdf file xobj Rotate value > 0 found")
                img_rotation = pdf_rotation - 180

            # ocr the first FIRST_FIVE pages max
            reader = PdfReader(file_path)
            page_count = int(reader.numPages)

            FIRST_FIVE = params.FIRST_FIVE
            if page_count < FIRST_FIVE:
                FIRST_FIVE = page_count

            ret = subprocess.call(['/usr/bin/pdfimages', '-j',
                                   file_path, img_root])
            if ret == 0:
                logging.info('pdfimages successfully ended')
                files = [os.path.join(params.IMG_PATH, f) for f in
                         os.listdir(params.IMG_PATH) if '_img_' + pdf_name in f]

                if len(files) > FIRST_FIVE:
                    files = files[:FIRST_FIVE]

                logging.info("files = %s", files)

                # convert to jpg for remote tesseract ocr api
                pbm_files = [p for p in files if '.pbm' in p]
                if len(pbm_files) > 0:
                    convert_to_jpg(pbm_files)
                    files2 = [x.replace('.pbm', '.jpg') if '.pbm' in x else
                              x for x in files]
                    files = list(set(files2))

                # rotate images for pdf extract image with rotation problems
                # TODO: rotation must mave margins, some data may lost
                if img_rotation != 0:
                    for img in files:
                        logging.info("rotating the image files...")
                        rotate_image(img, img_rotation)
                if len(files) > params.OCR_THRESHOLD:
                    return files[0:params.OCR_THRESHOLD]
                return files
            else:
                logging.error("PDFIMAGES for %s not successfull!", file_path)
                return None

        clist = []
        if self.message.is_multipart():
            email.iterators._structure(self.message)
            walked_parts_stack = []
            for part in self.message.walk():
                # text/plain is sufficient for alternative part
                part_type = (part.get_content_maintype(),
                             part.get_content_subtype())
                walked_parts_stack.append(part_type)
                if part_type[0] == "text" and part_type[1] == "html":
                    if find_parent(walked_parts_stack,
                                   ('multipart', 'alternative')):
                        logging.info("multipart/alternative altinda \
                                     text/html yakalandi. Es geciliyor..")
                        continue
                if part.get_content_maintype() == "text":
                    if (part.get('Content-Transfer-Encoding') == 'base64'):
                        # if part type is text, then get payload text
                        if (part.get_content_maintype() == 'text'):
                            logging.info("base64 type readable txt data added to\
                                         the list")
                            clist.append(part.get_payload(decode=True).
                                         decode('utf-8', errors='surrogateescape'))
                        else:
                            logging.info('attached file ' + part.get_filename() +
                                         ' binary!')
                            logging.info("base64 type file is converting")
                            attachmentContent = get_attachment_content(part)[0]
                            logging.info("attached file content is added to the\
                                         list")
                            clist.append(attachmentContent)
                    else:
                        try:
                            logging.info("text data is adding to the list...")
                            clist.append(part.get_payload(decode=True).
                                         decode('utf-8', errors='surrogateescape'))
                        except UnicodeDecodeError:
                            logging.warning("UnicodeDecodeError error handled")
                            clist.append(part.get_payload(decode=True).
                                         decode('utf-8', errors='replace'))
                        except UnicodeEncodeError as e:
                            logging.error(e)
                            # TODO: handle UnicodeEncodeErrors
                            logging.error("UnicodeEncodeError not handled!")
                            pass

                elif part.get_content_maintype() == 'application':

                    logging.info("application %s", part.get_content_subtype())
                    attachmentContentTupple = get_attachment_content(part)
                    if attachmentContentTupple is not None:
                        attachmentContent = attachmentContentTupple[0]
                        attachmentContentType = attachmentContentTupple[1]
                    else:
                        attachmentContent = ''
                        attachmentContentType = ''
                    if attachmentContentType == 'application/pdf' \
                            and attachmentContent == '':
                        # TODO: some pdf scanned files can be parsed but content
                        # is not ''. Check pdffonts like control to detect
                        # scanned image pdf
                        logging.info('the pdf may have image on it, tryin to ocr\
                                     the pdf...')
                        filename = part.get_filename()
                        str_attachment = part.get_payload(decode=True)
                        pdf_file_path = '/tmp/' + clean_str(filename)
                        open(pdf_file_path, 'wb').write(str_attachment)
                        img_files = extract_image_pdf(pdf_file_path)
                        # print(img_files)
                        logging.info("IMG_FILES: %s", img_files)
                        # use turkish lang for detection
                        # TODO: detect the document language (via for ex. tika)
                        if params.REMOTE_OCR:
                            attachmentContent = remote_ocr_content(img_files,
                                                                   params.OCR_LANG)
                        else:
                            attachmentContent = ocr_content(img_files,
                                                            params.OCR_LANG)

                        attachmentContent = remove_blank_lines(attachmentContent)
                        # logging.info("pdf image file content: %s",
                        #             attachmentContent)

                    if attachmentContent is not None:
                        clist.append(attachmentContent)
                    else:
                        logging.warning("%s type not retrieved from tika!",
                                        part.get_content_subtype())
                # else:
                #    print(part.get_content_maintype())
        else:
            try:
                if self.message.get_content_type() != 'text/calendar':
                    clist.append(self.message.get_payload(decode=True).
                                 decode('utf-8', errors='surrogateescape'))
                else:
                    logging.info('text/calendar type pass...')
            except UnicodeEncodeError as e:
                logging.error(e)
                # TODO: handle UnicodeEncodeError
                logging.error("UnicodeEncodeError not handled!")
                pass

        return clist

    def add_dlp_header(self):
        """
        add header to the processed email object/file
        :return:
        """
        file_name = self.message_fname
        if self.message.get('X-MailRelay-DLP') == '1':
            if self.PARSE_FROM_EML:
                logging.info("X-MailRelay-DLP header found for %s,\
                             not adding...", file_name)
            else:
                logging.info("X-MailRelay-DLP header found for message,\
                                             not adding...")
            return

        if self.message_string == '':
            logging.error('msg_string empty! exiting from add_dlp_header.')
            return

        self.message.add_header('X-MailRelay-DLP', '1')
        self.set_message_string()

        if self.PARSE_FROM_EML:
            logging.info("X-MailRelay-DLP header is adding for %s... ",
                         file_name)
        else:
            logging.info("X-MailRelay-DLP header is adding to message... ",)
        # if eml file given, write the email str to file
        if self.PARSE_FROM_EML:
            if self.export_message(file_name):
                logging.info("X-MailRelay-DLP header added")
            else:
                logging.warning("X-MailRelay-DLP header could not added!")

    def search_leaks(self, patterns_dict=None, regexes_list=None):
        """
        main program to parse the e-mail file and search for content
        :param patterns_dict: dictionary of leakage patterns {'TCID':'\b[0-9]{11}\b'}
        :param regexes_list: precompiled list of regex for patterns
        :return: non-zero value indicating the leakage found or zero indicating
                 no leakage found
        """
        message_fname = self.message_fname
        message_str = self.message_string

        def date_handler(obj):
            return obj.isoformat() if hasattr(obj, 'isoformat') else obj

        def load_patterns(file_path):
            """
            loads the patterns from csv file
            :param file_path: file path of csv pattern file
            :return: dict of patterns
            """
            patternsDict = {}
            try:
                with open(file_path, mode='r') as csvfile:
                    reader = csv.reader(csvfile)
                    patternsDict = {rows[0]: (rows[1], rows[2]) for rows in reader}
            except FileNotFoundError:
                logging.error("patterns file not found!")
            return patternsDict

        def patterns_match_score(content, _patterns, _regexes_list=None):
            """
            finds if content matches to given patterns, then
            generates a score based on number of matches
            :param content: str content
            :param _patterns: dict of leakage patterns
            :param _regexes_list: regex pattern list
            :return:
            """

            def get_regexes(_patterns):
                assert type(_patterns) == dict
                return [t[0] for t in _patterns.values()]

            def is_turkish_id(x):
                """
                checks if given id is valid TC ID
                :param x: int value
                :return: boolean value
                """
                if len(str(x)) != 11:
                    return False
                str_id = str(x)

                # first 10 digit sum mod 10 equals 11th digit control
                lst_id = [int(n) for n in str_id if n.isdigit()]
                if lst_id[0] == 0:
                    return False

                # first 10 digit sum
                first_10_sum = sum(lst_id[:10])
                if first_10_sum % 10 != lst_id[-1]:
                    return False

                total_odds = sum(lst_id[0::2][:-1])
                total_evens = sum(lst_id[1::2][:-1])

                is_10 = (total_odds * 7 + total_evens * 9) % 10 == lst_id[9]
                is_11 = (total_odds * 8) % 10 == lst_id[-1]

                if not is_10 or not is_11:
                    return False
                else:
                    return True

            # END OF WRAPPER FUNCTIONS of patterns_match_score

            if _regexes_list is None:
                regexes = [re.compile(p) for p in get_regexes(_patterns)]
            else:
                logging.info("Generated regex list using")
                regexes = regexes_list
            match_score = 0
            # logging.info("content = %s", content)
            for regex in regexes:
                matches = re.findall(regex.pattern, content, re.IGNORECASE)
                logging.info("regex pattern = %s", regex.pattern)
                if len(matches) > 0:
                    # TC ID control
                    if regex.pattern == '\\b[0-9]{11}\\b':
                        logging.info("Possible TC ID found. Checking...")
                        matches_list = list(map(lambda tc: is_turkish_id(tc), matches))
                        match_score = match_score + matches_list.count(True) * \
                                      int(_patterns['TCID'][1])
                        # tcmatches_list = [tc for tc in matches if
                        #                  is_turkish_id(tc) is True]
                        # logging.info("Found TC ID matches %s %s",
                        logging.info("Found TC ID matches %s",
                                     matches_list.count(True))
                    # SGK ID control
                    elif regex.pattern == '\\b[0-9]{13}\\b':
                        logging.info("Found SGK ID matches %s %s", len(matches),
                                     matches)
                        match_score = match_score + len(matches) * \
                                      int(_patterns['SGK'][1])
                    # Hizmete Ozel
                    else:
                        logging.info("Found Hizmete Özel keywork matches %s %s",
                                     len(matches), matches)
                        match_score = match_score + len(matches) * \
                                      int(_patterns['HO'][1])
            return match_score

        coloredlogs.install()
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(threadName)s - %(message)s',
                            filename='/tmp/parsemsg.log',
                            filemode='a', level=logging.DEBUG)

        logging.info('-------------------- PROCESS START --------------------')
        logging.info('App started')
        if message_str == '':
            logging.info("parsing the eml %s file...", message_fname)
        else:
            logging.info("parsing the message string...")

        # dlp data will be inserted to elastic search server

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((params.ES_SERVER, 9200))
        except socket.gaierror:
            logging.error("[Errno -3] Temporary failure in name resolution")
            result = 1
        if result == 0:
            logging.info("Elastic Search port is open")
            es = Elasticsearch(hosts=params.ES_SERVER, http_auth=params.ES_AUTH)
            if es.ping():
                isClusterReady = True
            else:
                isClusterReady = False
        else:
            logging.warning("Elastic Search port is not open")
            isClusterReady = False

        # the datas to be logged to elastic search
        data = {}
        data['filename'] = message_fname
        data['timestamp'] = datetime.utcnow()
        data['message-id'] = self.message.get('Message-ID')
        data['from'] = self.message.get('from')
        data['to'] = self.message.get('to')
        data['subject'] = self.message.get('subject')

        # print("Multipart?", msg.is_multipart())

        # print("*******************************")
        # msg_struct = email.iterators._structure(msg)
        # print("*******************************")

        contentList = self.search_body_content()

        PATTERN_FILE = './PATTERNS'
        if patterns_dict is None:
            patterns = load_patterns(PATTERN_FILE)
        else:
            patterns = patterns_dict

        try:
            str_content = "\n".join(contentList)
            # str_content = str_content.encode('ascii', 'replace').decode()
        except TypeError:
            logging.error("possible None from content in str_content!")
            logging.error('App ended!')
        else:
            # paternler eslesiyor mu
            data['message'] = str_content.rstrip('\n')
            if patterns_match_score(str_content, patterns,
                                  regexes_list) >= params.PATTERN_THREASHOLD:
                logging.warning('Pattern found')
                logging.info('logging the %s long pattern record...',
                             len(data['message']))
                # elastic search dlp logging
                if isClusterReady:
                    try:
                        datajson = json.dumps(data, default=date_handler,
                                              sort_keys=True)
                    except UnicodeDecodeError:
                        logging.error('datajson unicode dump error!')
                        logging.warning('elasticsearch index problem! ')
                    except ValueError as e:
                        logging.warning('json dumps error!')
                        logging.error(e)
                    else:
                        try:
                            es.index(index=params.ES_INDEX_NAME,
                                     doc_type='message',
                                     body=datajson, request_timeout=30)
                            logging.info('elasticsearch index successful')
                        except Exception as e:
                            logging.error('elasticsearch index failure')
                            logging.error(e)
                            pass
                else:
                    # TODO: if es cluster not ready, store in a file.
                    logging.warning('elasticsearch insert problem. May be the ' +
                                    'cluster is not ready!')

                #  add_dlp_header(file_name, msg)
                self.add_dlp_header()
                logging.info('----------------- PROCESS DONE ---------------')
                logging.info('App ended.')
                return params.ACTION['AUDIT']
                # sys.exit(100)
            else:
                logging.info('----------------- PROCESS DONE ---------------')
                logging.info('App ended.')
                # sys.exit(0)
                return 0


if __name__ == "__main__":
    try:
        file_name = sys.argv[1]
    except IndexError:
        logging.error('File Path not specified!')
        sys.exit(1)
    email_message = EmailMessage(file_name, '')
    if len(sys.argv) == 2:
        email_message.search_leaks()
    elif len(sys.argv) > 2:
        patterns_dict = sys.argv[2]
        regexes_list = sys.argv[3]
        email_message.search_leaks(patterns_dict, regexes_list)
