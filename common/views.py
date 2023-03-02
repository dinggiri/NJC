from django.shortcuts import render, redirect, get_object_or_404

def title(request):
    return render(request, 'common/0인트로.html')