#!/bin/env python3
# -*- coding: utf-8 -*-
import re


def clean_str(mystr, str_rep='', remove_non_unicode=False):
    """
    removes the special characters in the str.
    :param mystr: a string
    :param str_rep: replace string chacter
    :param remove_non_unicode: boolean
    :return: modified string
    """
    if type(mystr) is str or mystr is not None:
        if remove_non_unicode:
            return re.sub('\W+', str_rep, mystr)
        else:
            return re.sub('[^A-Za-z0-9._]+', '', mystr)
    else:
        return mystr
