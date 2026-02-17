from django.urls import path
from . import views
urlpatterns = [
	path('', views.index, name="list"),
	path('update_task/<str:pk>/', views.updateTask, name="update_task"),
	path('delete_task/<str:pk>/', views.deleteTask, name="delete"),
	path('add_netflix/', views.add_netflix_series, name="add_netflix"),
	path('add_prime/', views.add_prime_series, name="add_prime"),
	path('add_apple/', views.add_apple_series, name="add_apple"),
	path('clear_watchlist/', views.clear_watchlist, name="clear_watchlist"),
]