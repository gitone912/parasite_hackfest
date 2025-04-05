from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Survey)
admin.site.register(SurveyLink)
admin.site.register(Response)
admin.site.register(Feedback)