from django.shortcuts import render

def info_reader(request):
    context = {

    }
    return render(request, 'info_collector/info_reader.html', context)
