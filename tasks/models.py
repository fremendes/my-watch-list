from django.db import models

# Create your models here.
class Task(models.Model):
	PROVIDER_CHOICES = [
		('netflix', 'Netflix'),
		('prime', 'Amazon Prime Video'),
		('apple', 'Apple TV'),
	]
	
	title = models.CharField(max_length=200)
	complete = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
	provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, null=True, blank=True)

	def __str__(self):
		return self.title