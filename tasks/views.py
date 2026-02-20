from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .models import *
from .forms import *
import requests
import base64
import secrets

def signup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			if user:
				login(request, user)
				messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
				return redirect('list')
		else:
			messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
	else:
		form = UserCreationForm()
	return render(request, 'tasks/signup.html', {'form': form})

def logout_view(request):
	logout(request)
	return redirect('login')

def france_connect_login(request):
	state = secrets.token_urlsafe(32)
	nonce = secrets.token_urlsafe(32)
	request.session['fc_state'] = state
	request.session['fc_nonce'] = nonce
	request.session.save()
	
	auth_url = (
		f"{settings.FRANCE_CONNECT_BASE_URL}/authorize?"
		f"response_type=code&"
		f"client_id={settings.FRANCE_CONNECT_CLIENT_ID}&"
		f"redirect_uri={settings.FRANCE_CONNECT_REDIRECT_URI}&"
		f"scope={settings.FRANCE_CONNECT_SCOPE}&"
		f"acr_values=eidas1&"
		f"state={state}&"
		f"nonce={nonce}"
	)
	
	return redirect(auth_url)

def france_connect_callback(request):
	try:
		code = request.GET.get('code')
		state = request.GET.get('state')
		
		if not code or not state:
			messages.error(request, 'Erreur lors de l\'authentification France Connect.')
			return redirect('login')
		
		saved_state = request.session.get('fc_state')
		if not saved_state or state != saved_state:
			messages.error(request, f'Erreur de sécurité lors de l\'authentification. State reçu: {state}, State attendu: {saved_state}')
			return redirect('login')
		
		del request.session['fc_state']
		if 'fc_nonce' in request.session:
			del request.session['fc_nonce']
		
		token_data = {
			'grant_type': 'authorization_code',
			'code': code,
			'redirect_uri': settings.FRANCE_CONNECT_REDIRECT_URI,
			'client_id': settings.FRANCE_CONNECT_CLIENT_ID,
			'client_secret': settings.FRANCE_CONNECT_CLIENT_SECRET,
		}
		
		auth_header = base64.b64encode(
			f"{settings.FRANCE_CONNECT_CLIENT_ID}:{settings.FRANCE_CONNECT_CLIENT_SECRET}".encode()
		).decode()
		
		headers = {
			'Authorization': f'Basic {auth_header}',
			'Content-Type': 'application/x-www-form-urlencoded'
		}
		
		token_response = requests.post(
			f"{settings.FRANCE_CONNECT_BASE_URL}/token",
			data=token_data,
			headers=headers,
			timeout=10
		)
		
		if token_response.status_code != 200:
			error_detail = token_response.text if hasattr(token_response, 'text') else str(token_response.status_code)
			messages.error(request, f'Erreur lors de la récupération du token: {error_detail}')
			return redirect('login')
		
		token_json = token_response.json()
		access_token = token_json.get('access_token')
		
		if not access_token:
			messages.error(request, 'Token d\'accès non reçu.')
			return redirect('login')
		
		userinfo_headers = {
			'Authorization': f'Bearer {access_token}'
		}
		
		userinfo_response = requests.get(
			f"{settings.FRANCE_CONNECT_BASE_URL}/userinfo",
			headers=userinfo_headers,
			timeout=10
		)
		
		if userinfo_response.status_code != 200:
			error_detail = userinfo_response.text if hasattr(userinfo_response, 'text') else str(userinfo_response.status_code)
			messages.error(request, f'Erreur lors de la récupération des informations utilisateur: {error_detail}')
			return redirect('login')
		
		userinfo = userinfo_response.json()
		sub = userinfo.get('sub')
		given_name = userinfo.get('given_name', '')
		family_name = userinfo.get('family_name', '')
		email = userinfo.get('email', '')
		
		if not sub:
			messages.error(request, 'Identifiant utilisateur non reçu.')
			return redirect('login')
		
		username = f"fc_{sub}"
		
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			full_name = f"{given_name} {family_name}".strip() or "Utilisateur France Connect"
			user = User.objects.create_user(
				username=username,
				email=email if email else f"{username}@franceconnect.local",
				first_name=given_name,
				last_name=family_name
			)
			messages.success(request, f'Compte créé avec succès ! Bienvenue {full_name}.')
		
		login(request, user)
		return redirect('list')
	except Exception as e:
		messages.error(request, f'Erreur lors de l\'authentification: {str(e)}')
		return redirect('login')

def google_login(request):
	state = secrets.token_urlsafe(32)
	request.session['google_state'] = state
	request.session.save()
	
	auth_url = (
		f"https://accounts.google.com/o/oauth2/v2/auth?"
		f"client_id={settings.GOOGLE_CLIENT_ID}&"
		f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
		f"response_type=code&"
		f"scope={settings.GOOGLE_SCOPE}&"
		f"state={state}&"
		f"access_type=offline&"
		f"prompt=consent"
	)
	
	return redirect(auth_url)

def google_callback(request):
	try:
		code = request.GET.get('code')
		state = request.GET.get('state')
		
		if not code or not state:
			messages.error(request, 'Erreur lors de l\'authentification Google.')
			return redirect('login')
		
		saved_state = request.session.get('google_state')
		if not saved_state or state != saved_state:
			messages.error(request, 'Erreur de sécurité lors de l\'authentification Google.')
			return redirect('login')
		
		del request.session['google_state']
		
		token_data = {
			'code': code,
			'client_id': settings.GOOGLE_CLIENT_ID,
			'client_secret': settings.GOOGLE_CLIENT_SECRET,
			'redirect_uri': settings.GOOGLE_REDIRECT_URI,
			'grant_type': 'authorization_code',
		}
		
		token_response = requests.post(
			'https://oauth2.googleapis.com/token',
			data=token_data,
			headers={'Content-Type': 'application/x-www-form-urlencoded'},
			timeout=10
		)
		
		if token_response.status_code != 200:
			error_detail = token_response.text if hasattr(token_response, 'text') else str(token_response.status_code)
			messages.error(request, f'Erreur lors de la récupération du token Google: {error_detail}')
			return redirect('login')
		
		token_json = token_response.json()
		access_token = token_json.get('access_token')
		
		if not access_token:
			messages.error(request, 'Token d\'accès Google non reçu.')
			return redirect('login')
		
		userinfo_response = requests.get(
			'https://www.googleapis.com/oauth2/v2/userinfo',
			headers={'Authorization': f'Bearer {access_token}'},
			timeout=10
		)
		
		if userinfo_response.status_code != 200:
			error_detail = userinfo_response.text if hasattr(userinfo_response, 'text') else str(userinfo_response.status_code)
			messages.error(request, f'Erreur lors de la récupération des informations utilisateur Google: {error_detail}')
			return redirect('login')
		
		userinfo = userinfo_response.json()
		google_id = userinfo.get('id')
		email = userinfo.get('email', '')
		given_name = userinfo.get('given_name', '')
		family_name = userinfo.get('family_name', '')
		picture = userinfo.get('picture', '')
		
		if not google_id:
			messages.error(request, 'Identifiant Google non reçu.')
			return redirect('login')
		
		username = f"google_{google_id}"
		
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			if email and User.objects.filter(email=email).exists():
				messages.error(request, 'Un compte avec cet email existe déjà.')
				return redirect('login')
			
			full_name = f"{given_name} {family_name}".strip() or "Utilisateur Google"
			user = User.objects.create_user(
				username=username,
				email=email if email else f"{username}@google.local",
				first_name=given_name,
				last_name=family_name
			)
			messages.success(request, f'Compte créé avec succès ! Bienvenue {full_name}.')
		
		login(request, user)
		return redirect('list')
	except Exception as e:
		messages.error(request, f'Erreur lors de l\'authentification Google: {str(e)}')
		return redirect('login')

@login_required
def index(request):
	tasks = Task.objects.filter(user=request.user).order_by('-created')
	context= {'tasks':tasks}
	return render(request, 'tasks/list.html',context)

@login_required
def updateTask(request,pk):
	task = Task.objects.get(id=pk, user=request.user)
	form = TaskForm(instance=task)

	if request.method == "POST":
		form = TaskForm(request.POST,instance=task)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'tasks/update_task.html',context)

@login_required
def deleteTask(request,pk):
	item = Task.objects.get(id=pk, user=request.user)

	if request.method == "POST":
		item.delete()
		return redirect('/')

	context = {'item':item}
	return render(request, 'tasks/delete.html', context)

@login_required
def clear_watchlist(request):
	if request.method == "POST":
		Task.objects.filter(user=request.user).delete()
		return redirect('/')
	return redirect('/')

@login_required
def add_netflix_series(request):
	try:
		headers = {
			'Authorization': f'Bearer {settings.TMDB_API_KEY}',
			'accept': 'application/json'
		}
		
		series_added = 0
		page = 1
		max_pages = 50
		consecutive_empty_pages = 0
		
		while series_added < 10 and page <= max_pages:
			params = {
				'with_watch_providers': '8',
				'watch_region': 'FR',
				'sort_by': 'vote_average.desc',
				'vote_count.gte': 500,
				'first_air_date.gte': '2010-01-01',
				'page': page
			}
			
			response = requests.get(f'{settings.TMDB_API_URL}/discover/tv', headers=headers, params=params, timeout=10)
			
			if response.status_code != 200:
				break
			
			data = response.json()
			results = data.get('results', [])
			
			if not results:
				consecutive_empty_pages += 1
				if consecutive_empty_pages >= 3:
					break
				page += 1
				continue
			
			consecutive_empty_pages = 0
			found_new_series = False
			
			for series in results:
				if series_added >= 10:
					break
					
				tmdb_id = series.get('id')
				title = series.get('name', 'Sans titre')
				
				if tmdb_id and title:
					if not Task.objects.filter(tmdb_id=tmdb_id, user=request.user).exists():
						try:
							Task.objects.create(
								user=request.user,
								title=title,
								tmdb_id=tmdb_id,
								provider='netflix',
								complete=False
							)
							series_added += 1
							found_new_series = True
						except Exception as e:
							continue
			
			page += 1
		
		return redirect('/')
	except Exception as e:
		return HttpResponse(f"Erreur: {str(e)}", status=500)

@login_required
def add_prime_series(request):
	try:
		headers = {
			'Authorization': f'Bearer {settings.TMDB_API_KEY}',
			'accept': 'application/json'
		}
		
		series_added = 0
		page = 1
		max_pages = 50
		consecutive_empty_pages = 0
		
		while series_added < 10 and page <= max_pages:
			params = {
				'with_watch_providers': '9',
				'watch_region': 'US',
				'sort_by': 'vote_average.desc',
				'vote_count.gte': 500,
				'page': page
			}
			
			response = requests.get(f'{settings.TMDB_API_URL}/discover/tv', headers=headers, params=params, timeout=10)
			
			if response.status_code != 200:
				break
			
			data = response.json()
			results = data.get('results', [])
			
			if not results:
				consecutive_empty_pages += 1
				if consecutive_empty_pages >= 3:
					break
				page += 1
				continue
			
			consecutive_empty_pages = 0
			
			for series in results:
				if series_added >= 10:
					break
					
				tmdb_id = series.get('id')
				title = series.get('name', 'Sans titre')
				
				if tmdb_id and title:
					if not Task.objects.filter(tmdb_id=tmdb_id, user=request.user).exists():
						try:
							Task.objects.create(
								user=request.user,
								title=title,
								tmdb_id=tmdb_id,
								provider='prime',
								complete=False
							)
							series_added += 1
						except Exception as e:
							continue
			
			page += 1
		
		return redirect('/')
	except Exception as e:
		return HttpResponse(f"Erreur: {str(e)}", status=500)

@login_required
def add_apple_series(request):
	try:
		headers = {
			'Authorization': f'Bearer {settings.TMDB_API_KEY}',
			'accept': 'application/json'
		}
		
		series_added = 0
		page = 1
		max_pages = 50
		consecutive_empty_pages = 0
		
		while series_added < 10 and page <= max_pages:
			params = {
				'with_watch_providers': '2',
				'watch_region': 'FR',
				'sort_by': 'vote_average.desc',
				'vote_count.gte': 500,
				'first_air_date.gte': '2010-01-01',
				'page': page
			}
			
			response = requests.get(f'{settings.TMDB_API_URL}/discover/tv', headers=headers, params=params, timeout=10)
			
			if response.status_code != 200:
				break
			
			data = response.json()
			results = data.get('results', [])
			
			if not results:
				consecutive_empty_pages += 1
				if consecutive_empty_pages >= 3:
					break
				page += 1
				continue
			
			consecutive_empty_pages = 0
			
			for series in results:
				if series_added >= 10:
					break
					
				tmdb_id = series.get('id')
				title = series.get('name', 'Sans titre')
				
				if tmdb_id and title:
					if not Task.objects.filter(tmdb_id=tmdb_id, user=request.user).exists():
						try:
							Task.objects.create(
								user=request.user,
								title=title,
								tmdb_id=tmdb_id,
								provider='apple',
								complete=False
							)
							series_added += 1
						except Exception as e:
							continue
			
			page += 1
		
		return redirect('/')
	except Exception as e:
		return HttpResponse(f"Erreur: {str(e)}", status=500)