# Rest-Framework
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters import rest_framework as filters

# Project
from tatarby.serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model, login
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework import viewsets

# Models and Serializers
from tatarby.models import Dialog, Vote, Question, Answer, UserAnswer, UserDialogQuestion
from tatarby.serializers import DialogSerializer, VoteSerializer, QuestionSerializer, AnswerSerializer, UserAnswerSerializer, UserDialogQuestionSerializer

User = get_user_model()


class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        # Update session with user's ID
        request.session['user_id'] = user.id

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def registration_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # authenticate the user
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        # generate token upon successful registration
        if user is not None:
            login(request, user)
            # Update session with user's ID
            request.session['user_id'] = user.id

            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(ObtainAuthToken):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # delete the authentication token associated with the current user
    
        Token.objects.filter(user=request.user).delete()

        # return a success message
        return Response({'message': 'User successfully logged out.'}, status=status.HTTP_200_OK)
       

class DialogViewSet(viewsets.ModelViewSet):
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dialog_id = serializer.validated_data['dialog'].id

        # Check if the user has already voted on the same dialog
        existing_vote = Vote.objects.filter(user=request.user, dialog=dialog_id).first()

        if existing_vote:
            # If the user already voted, update the existing vote
            existing_vote.vote_type = serializer.validated_data['vote_type']
            existing_vote.save()
        else:
            # If the user hasn't voted, create a new vote
            self.perform_create(serializer)

        # Update the vote_score of the associated dialog
        self.update_dialog_vote_score(dialog_id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        dialog_id = instance.dialog.id

        self.perform_destroy(instance)

        # Update the vote_score of the associated dialog
        self.update_dialog_vote_score(dialog_id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update_dialog_vote_score(self, dialog_id):
        # Calculate and update the vote_score of the associated dialog
        dialog = Dialog.objects.get(pk=dialog_id)
        upvotes = Vote.objects.filter(dialog=dialog_id, vote_type=1).count()
        downvotes = Vote.objects.filter(dialog=dialog_id, vote_type=-1).count()
        dialog.vote_score = upvotes - downvotes
        dialog.save()


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class UserAnswerViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer

class UserDialogQuestionViewSet(viewsets.ModelViewSet):
    queryset = UserDialogQuestion.objects.all()
    serializer_class = UserDialogQuestionSerializer
