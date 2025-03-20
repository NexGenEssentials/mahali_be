from django.contrib import admin
from django.apps import apps

# Get all models in the current app
app = apps.get_app_config('car_rental')  # Replace 'your_app_name' with your app's name
for model in app.get_models():
    admin.site.register(model)
