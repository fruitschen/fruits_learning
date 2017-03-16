from django.shortcuts import render

def my_feedreader(request):
    context = {

    }
    return render(request, 'my_feedreader/my_feedreader.html', context)
