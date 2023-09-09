from django.contrib import admin

# Register your models here.
from tatarby.models import User, Dialog, Vote, Question, Answer, UserAnswer, UserDialogQuestion


admin.site.register(User)
admin.site.register(Dialog)
admin.site.register(Vote)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserAnswer)
admin.site.register(UserDialogQuestion)