# AbstractBaseUser를 쓰면서 해당 코드에 에러가 발생하여 현재 새로운 코드 작업중
# 현 PR은 모델링에 대한 PR로 아래 코드는 주석처리하고 우선적으로 진행하도록 하겠습니다.

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserCreationForm, CustomUserChangeForm
# from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ["email", "username",]

# admin.site.register(CustomUser, CustomUserAdmin)