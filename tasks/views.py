from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from .models import *
from .forms import *
import requests
# Create your views here.
def index(request):
	tasks = Task.objects.all().order_by('-created')

	context= {'tasks':tasks}
	return render(request, 'tasks/list.html',context)

def updateTask(request,pk):
	task = Task.objects.get(id=pk)
	form = TaskForm(instance=task)

	if request.method == "POST":
		form = TaskForm(request.POST,instance=task)
		if form.is_valid():
			form.save()
			return redirect('/')


	context = {'form':form}
	return render(request, 'tasks/update_task.html',context)

def deleteTask(request,pk):
	item = Task.objects.get(id=pk)

	if request.method == "POST":
		item.delete()
		return redirect('/')

	context = {'item':item}
	return render(request, 'tasks/delete.html', context)

def clear_watchlist(request):
	if request.method == "POST":
		Task.objects.all().delete()
		return redirect('/')
	return redirect('/')

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
					if not Task.objects.filter(tmdb_id=tmdb_id).exists():
						try:
							Task.objects.create(
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
					if not Task.objects.filter(tmdb_id=tmdb_id).exists():
						try:
							Task.objects.create(
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
					if not Task.objects.filter(tmdb_id=tmdb_id).exists():
						try:
							Task.objects.create(
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