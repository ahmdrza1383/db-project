from rest_framework import serializers

class CustomUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=100, write_only=True)
    name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(max_length=100)
    phone_number = serializers.CharField(max_length=15, required=False)
    city = serializers.CharField(max_length=20, required=False)
    date_of_sign_in = serializers.DateTimeField(required=False)
    profile_picture = serializers.ImageField(required=False)
    user_role = serializers.ChoiceField(choices=['USER', 'ADMIN'])
    authentication_method = serializers.ChoiceField(choices=['EMAIL', 'PHONE_NUMBER'])
