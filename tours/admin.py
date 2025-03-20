from django.contrib import admin
from django.apps import apps
from .models import Country, Highlight

# Get all models in the current app
app = apps.get_app_config('tours')  # Replace 'tours' with your app's name if needed

# Register all models dynamically
for model in app.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass  # Model is already registered, so we skip it

# HighlightAdmin should be registered with the Highlight model
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'description', 'icon')  # Add fields to display
    search_fields = ('title', 'country__name')

# Check if Highlight is already registered
if not admin.site.is_registered(Highlight):
    admin.site.register(Highlight, HighlightAdmin)
