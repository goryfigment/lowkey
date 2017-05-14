from django.shortcuts import render
from rsefficiency.modules.base import get_base_url


def main(request):
    data = {
        'base_url': get_base_url()
    }

    return render(request, 'main.html', data)
