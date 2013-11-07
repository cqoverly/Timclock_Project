# Python Std Library imports

# Django imports
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied

# Project imports


def manager_only(func):
    managers = User.objects.filter(groups__name='Manager')
    def wrapper(*args, **kwargs):
        request = args[0]
        print request.user
        if request.user in managers or request.user.is_superuser:
            return func(*args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper



