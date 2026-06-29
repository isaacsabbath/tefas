from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


kenyan_phone_validator = RegexValidator(
	regex=r"^2547\d{8}$",
	message="Enter a valid Kenyan phone number in the format 2547XXXXXXXX.",
)


class User(AbstractUser):
	email = models.EmailField(unique=True)
	phone_number = models.CharField(max_length=12, unique=True, validators=[kenyan_phone_validator])

	def __str__(self) -> str:
		return self.get_full_name() or self.username

# Create your models here.
