from django.db import models
from django.conf import settings
#from address.models import AddressField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class UserProfileProperty(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    order = models.PositiveIntegerField(unique=True)
    #object_id = models.CharField(max_length=20, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    #content_object = GenericForeignKey('content_type', 'object_id')
    def __str__(self):
        try:
            ct = self.content_type
        except BaseException:
            ct = "generic"
        return "{}|{}|{}".format(self.order, self.name, ct)
    class Meta: 
        verbose_name_plural = "User Profile Properties"


class UserProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        default=None,
        on_delete=models.CASCADE
    )
    prop = models.ForeignKey(UserProfileProperty, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    def __str__(self):
        target_user = "none"
        if self.user:
            target_user = self.user.username
        return "{}|{}|{}".format(target_user, self.prop.name, self.value)
    class Meta:
        unique_together = ('user', 'prop')
        verbose_name_plural = "User Profiles"


class Action(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    def __str__(self):
        return self.name

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)
    def __str__(self):
        return str(self.id) + "|" + self.user.username + "|" + self.action.name + "|" + str(self.date) + "|" + self.description

class Role(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    def __str__(self):
        return self.name

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    vat = models.CharField(max_length=200)
    def __str__(self):
        return self.id + "|" + self.vat
    class Meta: 
        verbose_name_plural = "Companies"

class UserCompanyBond(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username + "|" + self.company.vat + "|" + self.role.name
    class Meta:
        unique_together = ('user', 'company')
        verbose_name_plural = "User Company Bonds"

class Right(models.Model):
    name =  models.CharField(max_length=200, primary_key=True)
    def __str__(self):
        return self.name

class RoleRight(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    right = models.ForeignKey(Right, on_delete=models.CASCADE)
    def __str__(self):
        return self.role.name + "|" + self.right.name
    class Meta:
        unique_together = ('role', 'right')
        verbose_name_plural = "Role Rights"


class UserSettingProperty(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    stype = models.CharField(max_length=20)
    def __str__(self):
        return self.name
    class Meta: 
        verbose_name_plural = "User Setting Properties"

class UserSetting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    setting = models.ForeignKey(UserSettingProperty, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username + "|" + self.setting.name
    class Meta:
        unique_together = ('user', 'setting')
        verbose_name_plural = "User Settings"


class ReminderType(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Reminder Types"

class ReminderStatus(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Reminder Statuses"

class Reminder(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rtype = models.ForeignKey(ReminderType, null=True, on_delete=models.SET_NULL)
    expire_date = models.DateField()
    status = models.ForeignKey(ReminderStatus, null=True, on_delete=models.SET_NULL)
    #archived = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=5000)
    def __str__(self):
        exp_date = str(self.expire_date)
        rtype_name = 'deleted'
        if self.rtype is not None:
            rtype_name = self.rtype.name
        return str(self.id) + "|" + self.user.username + "|" + rtype_name + "|" + exp_date + "|" + self.title

class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.code
    class Meta:
        verbose_name_plural = "Countries"

class State(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=2)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self):
        return "{} ({})".format(self.code, self.country.code)
    class Meta:
        unique_together = ('code', 'country')

class Town(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    def __str__(self):
        return "{} ({})".format(self.name, self.state.code)
    class Meta:
        unique_together = ('name', 'state')

class Address(models.Model):
    raw = models.CharField(max_length=100, primary_key=True)
    num = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    extra = models.CharField(max_length=100, null=True)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    town = models.ForeignKey(Town, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.raw
    class Meta:
        verbose_name_plural = "Addresses"

class UserProfileType(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    def __str__(self):
        return self.name
    class Meta:
        abstract = True

class UserType(UserProfileType):
    class Meta:
        verbose_name_plural = "User Types"
        verbose_name = "UserType"

class FiscalType(UserProfileType):
    class Meta:
        verbose_name_plural = "Fiscal Types"
        verbose_name = "FiscalType"

class SocialSecurityType(UserProfileType):
    class Meta:
        verbose_name_plural = "Social Security Types"
        verbose_name = "SocialSecurityType"

class TextFieldType(UserProfileType):
    class Meta:
        verbose_name_plural = "Text Field Types"
        verbose_name = "TextFieldType"

class AddressType(UserProfileType):
    class Meta:
        verbose_name_plural = "Address Types"
        verbose_name = "AddressType"

class BooleanType(UserProfileType):
    class Meta:
        verbose_name_plural = "Boolean Types"
        verbose_name = "BooleanType"

def get_user_setting(user, prop):
    try:
        return UserSetting.objects.get(
            user=user,
            setting=UserSettingProperty.objects.get(name=prop)
        ).value
    except UserSetting.DoesNotExist:
        return None

def set_user_setting(user, prop, value):

    #usp = UserSettingProperty.objects.filter(name=prop),
    UserSetting.objects.update_or_create(
        user=user,
        setting=UserSettingProperty.objects.get(name=prop),
        defaults={'value': value}
    )

def get_deleted_repo():
    try:
        return UserSetting.objects.get(
            setting=UserSettingProperty.objects.get(name="deleted_repo")
        ).value
    except UserSetting.DoesNotExist:
        return None

def add_log(user, act, description):
    action = Action.objects.get(name=act)
    log = Log(user=user, action=action, description=description)
    log.save()
