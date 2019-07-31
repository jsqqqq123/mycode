from django.contrib import admin

# Register your models here.

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import MyUsers, MyBi, Rooms, MyAgent, ChargeHistory, UserBi, Combi, UserOperator
from daterange_filter.filter import DateRangeFilter


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUsers
        fields = ('username', 'user_id')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUsers
        fields = ('username', 'nickname', 'password', 'user_id', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'user_id', 'nickname', 'avatar_url', 'agent_id', 'fencheng', 'is_vip', 'is_active', 'is_robot', 'is_talke', 'is_admin', 'state')
    list_filter = ('is_admin',)
    search_fields = ('username', 'nickname', 'agent_id')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'nickname', 'user_id')}),
        ('Personal info', {'fields': ('avatar_url', 'agent_id', 'fencheng')}),
        ('Permissions', {'fields': ('is_admin','is_vip', 'is_active', 'is_robot', 'is_talke', 'state')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'user_id', 'nickname', 'password1', 'password2')}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


#@admin.register(MyBi)
#class MyBiAdmin(admin.ModelAdmin):
#    list_display = ('user_id', 'total_m', 'cur_m', 'get_m', 'recharge_lasttime', 'withdraw_lastime')
#    search_fields = ('user_id__username',)


@admin.register(Rooms)
class MyAdminRooms(admin.ModelAdmin):
    list_display = ('room_id', 'room_name', 'room_video', 'is_active', 'is_public', 'is_vip', 'passwd', 'agent_id', 'room_admin')
    search_fields = ('room_name', 'room_id')
# Now register the new UserAdmin...


@admin.register(MyAgent)
class MyAdminAgent(admin.ModelAdmin):
    list_display = ('agent_id', 'username', 'agent_name', 'father_agent', 'pre_agent', 'next_agent', 'agent_percent')
    search_fields = ('username', 'agent_name')


@admin.register(ChargeHistory)
class MyAdminChargeHistory(admin.ModelAdmin):
    list_display = ('date_time', 'opusername', 'username', 'operator', 'content')
    search_fields = ('username', 'date_time')
    list_filter =['date_time', ('date_time', DateRangeFilter)]
    date_hierarchy = ('date_time')


@admin.register(UserBi)
class MyAdminUserBi(admin.ModelAdmin):
    list_display = ("username", "agent_name", "zx_xima_total" , "sb_xima_total", "zx_total" , "sb_total", "yx_total", "date_time")
    search_fields = ('username', 'date_time')
    list_filter =['date_time', ('date_time',DateRangeFilter)]
    date_hierarchy = ('date_time')


@admin.register(Combi)
class MyAdminCombi(admin.ModelAdmin):
    list_display = ("date_time", "zx_total", "zx_xima_total" , "sb_total", "sb_com_total" , "sb_user_total", "ls_com_total")
    list_filter =['date_time', ('date_time', DateRangeFilter)]
    date_hierarchy = ('date_time')


@admin.register(UserOperator)
class MyAdminUserOperator(admin.ModelAdmin):
    list_display = ("username", "bacc_num", "xiazhu", "pre_yue", "result", "after_yue", "xiazhu_date")
    search_fields = ('username',)
    list_filter =['xiazhu_date', ('xiazhu_date', DateRangeFilter)]
    date_hierarchy = ('xiazhu_date')

admin.site.register(MyUsers, UserAdmin)

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
