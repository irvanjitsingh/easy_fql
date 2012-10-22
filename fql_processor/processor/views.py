from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import urllib, urllib2
import urlparse
import simplejson as json
import re
import pdb


app_id = ''
secret = ''
access_token = ''
redirect_uri = 'http://localhost:8000/authenticate/'
state = 'randomStateString'



def index(request):
	return render_to_response('index.html')

# def login_page(request):
# 	return render_to_response('login_form.html')

@csrf_exempt
def authentication_page(request):
	# redirect to facebook OAuth
	oauthDialogUrl = 'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=user_about_me&state=%s' % (app_id, redirect_uri, state)
	return render_to_response('authorization_page.html', RequestContext(request, {'oauth': oauthDialogUrl}))
	# return render_to_response('html_form.html')

@csrf_exempt
def authenticate(request):

	# retrieve code fron response url and use it to request access token
	code = request.REQUEST['code']
	token_url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (app_id, redirect_uri, secret, code)
	
	# retrieve and parse token response
	token_url_response = urllib.urlopen(token_url).read()
	parsed_token_response = urlparse.parse_qs(token_url_response)
	raw_token = dict(parsed_token_response).get( 'access_token')
	global access_token
	access_token = ''.join(str(x) for x in raw_token)
	
	# present a form to request fql query from user
	return render_to_response('query_form.html')

@csrf_exempt
def query_processor(request):
	fql_query = request.POST['query']
	filtered_query = re.search('select(.*)from', fql_query)
	rows = (filtered_query.group(1)).split(',')
	request = 'https://graph.facebook.com/fql?q=%s&access_token=%s' % (fql_query, access_token)
	json_response = urllib.urlopen(request).read()
	result = json.loads(json_response)['data'][0]
	keys = []
	values = []
	for key in result:
		if result[key] is not None:
			keys.append(key)
			values.append(result[key])
		else: 
			keys.append(key)
			values.append('none')
	return render_to_response('results.html', {'keys': keys, 'values': values})

# @csrf_exempt
# def login_processor(request):
# 	# if 'username' in request.POST and request.POST['username']:
# 	username = request.POST['username']
# 	# if 'email' in request.POST and request.POST['email']:
# 	# if 'password' in request.POST and request.POST['username']:
# 	password = request.POST['password']
# 	user = username + password
# 	return render_to_response('form_processor.html', RequestContext(request, {'user': user}))


