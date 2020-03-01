# dappx/views.py
from django.shortcuts import render, redirect
from .forms import UserForm, DocumentForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .helper.rightmove import mailer_rightmove
from .helper.zoopla import mailer_zoopla
import csv
import os


def index(request):
    try:
        if request.method == 'POST' and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            return render(request, 'message/index.html', {
                'uploaded_file_url': uploaded_file_url
            })
    except KeyError:
        pass
    return render(request,'message/index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()
    return render(request,'message/registration.html',
                          {'user_form':user_form,
                           'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)

                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'message/login.html', {})

@api_view(['GET', 'POST', ])
def send(request):
    csvpath = request.POST['csvpath']
    print(csvpath)

    os.chdir(os.path.dirname(__file__))
    print(os.getcwd())
    with open('../' + csvpath, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip first row
        for row in reader:
            if len(row) == 10:
                url = row[0]
                query = {
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "postcode": row[4],
                    "status": row[5],
                    "message": row[6],
                    "request_viewing": row[7],
                    "send_news": row[8],
                    "send_offers": row[9]
                }
                print(query)
                with mailer_zoopla() as scraper:
                    scraper.get_account(url, query)
                print('zoopla')
            elif len(row) == 12:
                url = row[0]
                query = {
                    "view_property": row[1],
                    "title": row[2],  # ['Mr', 'Mrs', 'Miss', 'Ms']
                    "firstName": row[3],
                    "lastName": row[4],
                    "comments": row[5],
                    "telephone": row[6],
                    "email": row[7],
                    "country_code": row[8],  # ['AF', 'AL', 'DZ', 'AS', 'AD', 'AO', ...]
                    "postcode": row[9],
                    "address": row[10],
                    "emailAnswerEnquirerType": row[11]
                    # ['surveyor_agent', 'investor_developer' ,'tenant_buyer', 'other']
                }
                print(query)
                with mailer_rightmove() as scraper:
                    scraper.get_account(url, query)
                print('rightmove')

    return Response({'status': 'success'}, status=status.HTTP_200_OK)