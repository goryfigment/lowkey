from django.shortcuts import render, get_object_or_404
from rsefficiency.modules.base import get_base_url


def main(request):
    data = {
        'base_url': get_base_url()
    }

    return render(request, 'main.html', data)


def donate(request):
    data = {
        'base_url': get_base_url()
    }

    return render(request, 'donate.html', data)


def error_page(request):
    data = {
        'base_url': get_base_url()
    }

    return render(request, '404.html', data)


def server_error(request):
    data = {
        'base_url': get_base_url()
    }

    return render(request, '500.html', data)
