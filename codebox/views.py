# Create your views here.
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render,get_object_or_404,redirect
from django.template import RequestContext

from .constants import RUN_URL, secret
from .models import Pen
from .forms import CodeBoxRun

import requests

def home(request):
    if request.method == "POST":
        form = CodeBoxRun(data = request.POST)
        if form.is_valid():
            data = form.data['text']
            std_in = form.data['inp']
            lang = form.cleaned_data['langs']
            name = form.cleaned_data['name']
            source = data
            json_src = {
                'client_secret': secret,
                'async': 0,
                'source': source,
                'lang': lang,
                'input':std_in,
            }
            r = requests.post(RUN_URL,data=json_src)
            r1 = r.json()
            hash = str(r1['code_id'])
            penObject = Pen()
            penObject.code = data
            penObject.lang = lang
            penObject.url_count += 1
            penObject.hash = str(r1['code_id'])
            penObject.publish()
            sessionTransferDict = {}
            sessionTransferDict['i'] = std_in
            sessionTransferDict['s'] = str(r1['run_status']['status'])
            sessionTransferDict['sd'] = r1['run_status']['status_detail']
            if sessionTransferDict['s'] == "CE":
                sessionTransferDict['o'] = r1['compile_status']
                sessionTransferDict['t'] = "0.0"
                sessionTransferDict['m'] = "0"
            else:
                sessionTransferDict['o'] = r1['run_status']['output_html']
                sessionTransferDict['t'] = r1['run_status']['time_used']
                sessionTransferDict['m'] = r1['run_status']['memory_used']
            request.session['data'] = sessionTransferDict
            redirect_url = '/'+str(hash)
            return redirect(redirect_url)
    else:
        form = CodeBoxRun()
    return render(request,'codebox/home.html',{'form':form})

def display(request, hash):
    penObject = get_object_or_404(Pen, hash=hash)
    source = penObject.code
    lang = penObject.lang
    count = penObject.get_count()
    name = penObject.name
    resultData = {}
    if 'data' in request.session:
        data_pass = request.session['data']
        resultData['output'] = data_pass['o']
        resultData['time']= data_pass['t']
        resultData['memory']= data_pass['m']
        resultData['status_detail'] = data_pass['sd']
        resultData['status']=data_pass['s']
        priorData = {}
        priorData['inp']=data_pass['i']
        priorData['text']=source
        priorData['langs']=lang
        priorData['name']=name
        form = CodeBoxRun(initial = priorData)
        method = 1
        request.session.pop('data')
        data_pass = {}
    else:
        method = 0
        resultData['output'] = ""
        resultData['time']= ""
        resultData['memory']= ""
        resultData['status_detail'] = ""
        priorData = {}
        priorData['text'] = source
        priorData['langs'] = lang
        form = CodeBoxRun(initial=priorData)
    return render(request,'codebox/display.html',{'form':form,'out':resultData,'method':method,'count':count })