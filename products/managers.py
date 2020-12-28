from django.db import models


class ProductManager(models.Manager):
    def get_by_natural_key(self, category, type):
        return self.get(category=category, type=type)
