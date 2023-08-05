from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    account = models.ForeignKey(
        Account, related_name="transactions", on_delete=models.CASCADE
    )
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vendor = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.description} ({self.amount})"
