from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from k_user import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from k_user.common import response
from k_user.common.token import generate_token
from k_user import serializers


class RegisterView(APIView):

    authentication_classes = ()
    permission_classes = ()

    """
    注册:{
        "user": "demo"
        "password": "1321"
        "email": "1@1.com"
    }
    """

    def post(self, request):

        try:
            password = request.data["password"]
            email = request.data["email"]
            username = request.data["username"]
            isadmin = request.data["isadmin"]
        except KeyError:
            return Response(response.KEY_MISS)

        # 用户名是否重复
        if models.UserInfo.objects.filter(username=username).first():
            return Response(response.REGISTER_LOGINNAME_EXIST)

        # 邮箱是否重复
        if models.UserInfo.objects.filter(email=email).first():
            return Response(response.REGISTER_EMAIL_EXIST)

        # 密码加密
        request.data["password"] = make_password(password)

        # 序列化用户信息
        serializer = serializers.UserInfoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(response.REGISTER_SUCCESS)
        else:
            return Response(response.SYSTEM_ERROR)


class LoginView(APIView):
    """
    登陆视图，用户名与密码匹配返回token
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        """
        用户名密码一致返回token
        {
            loginname: str
            password: str
        }
        """
        try:
            username = request.data["username"]
            password = request.data["password"]
        except KeyError:
            return Response(response.KEY_MISS)

        user = models.UserInfo.objects.filter(username=username, status=0).first()

        if not user:
            return Response(response.USER_NOT_EXISTS)
        # 检查密码
        if not check_password(password, user.password):
            return Response(response.LOGIN_FAILED)

        # 生成一个token
        token = generate_token(user.username)

        # 更新或生成token记录
        try:
            models.UserToken.objects.update_or_create(user=user, defaults={"token": token})
        except ObjectDoesNotExist:
            return Response(response.SYSTEM_ERROR)
        # else:
        #     response.LOGIN_SUCCESS["token"] = token
        #     response.LOGIN_SUCCESS["user"] = user.username
        #     response.LOGIN_SUCCESS["role"] = user.isadmin
        #     response.LOGIN_SUCCESS["isSso"] = user.isSsoUser
        return Response(response.LOGIN_SUCCESS)



class UserList(ViewSet):
    """
    返回用户列表
    """
    def get_user_list(self, request):
        user_list = models.UserInfo.objects.all().values("id", "username", "email", "status").order_by("create_time")
        return Response({
            "code":"0001",
            "success": False,
            "msg": "查询成功",
            "data": user_list
        })