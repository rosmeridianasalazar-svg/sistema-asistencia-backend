from django.contrib.auth.hashers import BCryptSHA256PasswordHasher


class BCryptSHA256Cost10PasswordHasher(BCryptSHA256PasswordHasher):
    rounds = 10