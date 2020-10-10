from django.contrib import admin
from . import models

admin.site.register(models.Game)
admin.site.register(models.Round)
admin.site.register(models.Question)
admin.site.register(models.Team)
admin.site.register(models.T_Answer)
admin.site.register(models.T_Member)
admin.site.register(models.Poll)
admin.site.register(models.Poll_Answer)