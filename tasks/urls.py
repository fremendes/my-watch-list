from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
	path('', views.index, name="list"),
	path('signup/', views.signup, name="signup"),
	path('login/', auth_views.LoginView.as_view(template_name='tasks/login.html'), name="login"),
	path('logout/', views.logout_view, name="logout"),
	path('france-connect/login/', views.france_connect_login, name="france_connect_login"),
	path('callback', views.france_connect_callback, name="france_connect_callback"),
	path('google/login/', views.google_login, name="google_login"),
	path('google/callback', views.google_callback, name="google_callback"),
	path('update_task/<str:pk>/', views.updateTask, name="update_task"),
	path('delete_task/<str:pk>/', views.deleteTask, name="delete"),
	path('add_netflix/', views.add_netflix_series, name="add_netflix"),
	path('add_prime/', views.add_prime_series, name="add_prime"),
	path('add_apple/', views.add_apple_series, name="add_apple"),
	path('clear_watchlist/', views.clear_watchlist, name="clear_watchlist"),
]