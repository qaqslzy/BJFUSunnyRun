from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.(自定义对所有的访问进行认证)
    """

    def has_permission(self, request, view):
        try:
            return False if request.user.user_name == '' else True
        except:
            return False

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.(对GET方法放过处理，其它进行认证)
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            False if request.user.username == '' else True
        )