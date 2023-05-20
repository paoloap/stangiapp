from django.contrib import admin
from .models import *
# from address.models import Address
# from address.models import AddressField
# Register your models here.

class UserProfilePropertyAdmin(admin.ModelAdmin):
    list_display = ('order', 'name' )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'prop', 'value', )

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'vat' )

class UserCompanyBondAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role' )

class RoleRightAdmin(admin.ModelAdmin):
    list_display = ('role', 'right' )

class UserSettingPropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'stype' )

class UserSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'setting', 'value' )

class ReminderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rtype', 'expire_date', 'title', 'status')

class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'action', 'description')

# class AddressAdmin(admin.ModelAdmin):
#     list_display = ('raw' )

admin.site.register(UserProfileProperty, UserProfilePropertyAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Action)
admin.site.register(Role)
admin.site.register(Right)
admin.site.register(RoleRight, RoleRightAdmin)
admin.site.register(UserCompanyBond, UserCompanyBondAdmin)
admin.site.register(UserSettingProperty, UserSettingPropertyAdmin)
admin.site.register(UserSetting, UserSettingAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(ReminderType)
admin.site.register(UserType)
admin.site.register(FiscalType)
admin.site.register(SocialSecurityType)
admin.site.register(BooleanType)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(ReminderStatus)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(Town)
admin.site.register(Address)
# admin.site.register(Address, AddressAdmin)

