from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
	PROVIDER_CHOICES = [
		('netflix', 'Netflix'),
		('prime', 'Amazon Prime Video'),
		('apple', 'Apple TV'),
	]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=200)
	complete = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	tmdb_id = models.IntegerField(null=True, blank=True)
	provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, null=True, blank=True)

	class Meta:
		unique_together = [['tmdb_id', 'user']]

	def __str__(self):
		return self.title