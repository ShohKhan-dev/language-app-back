
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tatarby.views import login_view, registration_view, LogoutView, UserView, DialogViewSet, VoteViewSet, QuestionViewSet, AnswerViewSet, UserAnswerViewSet, UserDialogQuestionViewSet


router = DefaultRouter()
router.register(r'dialogs', DialogViewSet, 'dialogs')
router.register(r'votes', VoteViewSet, 'votes')
router.register(r'questions', QuestionViewSet, 'questions')
router.register(r'answers', AnswerViewSet, 'answers')
router.register(r'useranswers', UserAnswerViewSet, 'useranswers')
router.register(r'userdialogquestions', UserDialogQuestionViewSet, 'userdialogquestions')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('register/', registration_view, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserView.as_view()),
]
