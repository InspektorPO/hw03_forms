from django.core.paginator import Paginator

from yatube.settings import PAGE


def get_paginator(obj, page_number):
    paginator = Paginator(obj, PAGE)
    page_obj = paginator.get_page(page_number)

    return page_obj
