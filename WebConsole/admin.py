from django import forms
from django.contrib import admin
from django.contrib.auth import password_validation
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from WebConsole.models import AuthUser


class AuthUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    class Meta:
        model = AuthUser
        fields = (
            'username', 'email', 'is_staff', 'is_active', 'show_name', 'sys_user', 'sys_uid',
            'kbe_root', 'kbe_res_path', 'kbe_bin_path')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次密码不一致")
        user = super(AuthUserCreationForm, self).save(commit=False)
        password_validation.validate_password(password2, user)
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(AuthUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AuthUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password3 = forms.CharField(label='旧密码', required=False, widget=forms.PasswordInput)
    password4 = forms.CharField(label='新密码', required=False, widget=forms.PasswordInput)

    class Meta:
        model = AuthUser
        fields = (
            'username', 'show_name', 'password3', 'password4', 'email', 'is_staff', 'is_active', 'sys_user', 'sys_uid',
            'kbe_root', 'kbe_res_path', 'kbe_bin_path')

    def clean_password4(self):
        password3 = self.cleaned_data.get('password3')
        password4 = self.cleaned_data.get('password4')
        if password3:
            user = super(AuthUserChangeForm, self).save(commit=False)
            if not user.check_password(password3):
                raise forms.ValidationError(
                    self.error_messages['旧密码错误'],
                    code='password_incorrect',
                )
            else:
                if not password4:
                    raise forms.ValidationError(
                        self.error_messages['新密码不能为空'],
                        code='password_mismatch',
                    )
            password_validation.validate_password(password4, user)
        return password4

    def save(self, commit=True):
        """Save the new password."""
        user = super(AuthUserChangeForm, self).save(commit=False)
        oldPassword = self.cleaned_data.get('password3')
        if oldPassword:
            if user.check_password(oldPassword):
                newPassword = self.cleaned_data["password4"]
                if newPassword:
                    user.set_password(newPassword)
        if commit:
            user.save()
        return user


class AuthUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = AuthUserChangeForm
    add_form = AuthUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'username', 'show_name', 'email', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'show_name', 'password3', 'password4', 'email', 'is_staff', 'is_active')}),
        ('KBEngine Config', {'fields': ('sys_user', 'sys_uid', 'kbe_root', 'kbe_res_path', 'kbe_bin_path')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'show_name', 'password1', 'password2', 'email', 'is_staff', 'is_active')}),
        ('KBEngine Config', {'fields': ('sys_user', 'sys_uid', 'kbe_root', 'kbe_res_path', 'kbe_bin_path')}),
    )
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(AuthUser, AuthUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)
