from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .utils import generate_token, generate_password_reset_token, send_password_reset_mail
from rest_framework import permissions
from .models import Profile
from .serializers import ProfileSerialzer


User = get_user_model()


class AuthTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['middle_name'] = user.middle_name
        token['email'] = user.email
        token['email_verified'] = user.email_verified

        return token


class AuthTokenObtainPairView(TokenObtainPairView):
    serializer_class = AuthTokenObtainPairSerializer

# Create your views here.


class SignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)
        middle_name = data.get('last_name', '')
        password = data.get('password', None)
        re_password = data.get('re_password', None)
        email = data.get('email', None)

        if first_name is None or last_name is None or password is None or re_password is None or email is None:
            context = {
                'success': False,
                'description': 'Invalid form data'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        if password != re_password:
            context = {
                'success': False,
                'description': 'Passwords do not match'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.get(email=email)
            context = {
                'success': False,
                'description': 'A user with this email already exists'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # if a user does not exist create one
            user = User(first_name=first_name,
                                last_name=last_name,
                                middle_name=middle_name,
                                email=email)
            user.set_password(password)
            user.save()

            context = {
                'success': True,
                'description': 'Account Successfully created , proceed to login'
            }
            return Response(context, status=status.HTTP_200_OK)


class RetriveUsers(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self , request):
        queryset = Profile.objects.all()
        serializer = ProfileSerialzer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RetriveProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
            serializer = ProfileSerialzer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data
        email = data.get('email', None)

        if email is None:
            context = {
                "error": True,
                "text": "Email is invalid"
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        try:
            context = {
                "error": False,
                "text": "Instructions have been sent to your mail on how to reset your password"
            }
            user = User.objects.get(email=email)
            send_password_reset_mail(user)
            return Response(context, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            context = {
                "error": True,
                "text": "User does not exist"
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        data = request.data
        new_password = data.get('password', None)

        if token is None or uidb64 is None or new_password is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
            if user and generate_password_reset_token.check_token(user, token):
                user.set_password(new_password)
                user.save()
                context = {
                    'success': True,
                    'description': 'Password Reset Successful'
                }
                return Response(context, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        if token is None or uidb64 is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
            if user and generate_token.check_token(user, token):
                user.email_verified = True
                user.save()
                context = {
                    'success': True,
                    'description': 'Email successfully verified'
                }
                return Response(context, status=status.HTTP_200_OK)
        except Exception as E:
            return Response(status=status.HTTP_400_BAD_REQUEST)