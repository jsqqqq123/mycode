#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""
from rest_framework.pagination import CursorPagination


class MyPagination(CursorPagination):
    cursor_query_param = 'cursor'
    page_size = 10
    ordering = 'id'
    page_size_query_param = None
    max_page_size = 10
    offset_cutoff = 1000



