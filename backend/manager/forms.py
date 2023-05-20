import re
from django import forms
from django.contrib.auth import get_user_model
from api.models import UserProfile, Reminder, Country, State, Town, Address, UserProfileProperty

def get_field_type(prop, initial):
    ctype = prop.content_type
    label = prop.name
    mod_name = (ctype and ctype.name) or "String"
    if mod_name.endswith("Type"):
        field_elements = ctype.model_class().objects.all()
        default = field_elements[0]
        if initial != "":
            default = field_elements.get(name=initial)
        return forms.ModelChoiceField(queryset=field_elements, initial=default, label=label)
    else:
        return forms.CharField(max_length=200, initial=initial, label=label)

# If there's something to do before saving (i.e. save something on an external model)
# this is the function that does it
def manage_before_save(value, ctype):
    mod_name = (ctype and ctype.name) or "String"
    if mod_name == "address":
        addr_array = re.split(" *, *", value)
        country = Country.objects.get_or_create(
            code=addr_array[0]
        )[0]
        state = State.objects.get_or_create(
            code=addr_array[1],
            country=country
        )[0]
        town = Town.objects.get_or_create(
            name=addr_array[2],
            state=state
        )[0]
        extra = (len(addr_array) == 7 and addr_array[6]) or ""
        address = Address.objects.get_or_create(
            raw=value,
            town=town,
            postal_code=addr_array[3],
            street=addr_array[4],
            num=addr_array[5],
            extra=extra
        )
    return True

def get_user_profile_forms(user, data):
    fields = []
    user_profile_props = UserProfileProperty.objects.order_by('order', 'pk')
    for upp in user_profile_props:
        pname = upp.name
        ptype = upp.content_type
        field = {'name': pname}
        instance = UserProfile.objects.filter(user=user, prop=upp).first()
        initial = {}
        if not instance:
            instance = UserProfile(user=user, prop=upp, value="")
        if not data:
            up_form = UserProfileForm(prefix=pname, initial=initial, instance=instance)
        else:
            up_form = UserProfileForm(data, prefix=pname, instance=instance)
        field['form'] = up_form
        fields.append(field)
        if data:
            up_form.save()
    return fields

class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email"]
        labels = {
            "first_name": "Nome",
            "last_name": "Cognome"
        }
    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        password = get_user_model().objects.make_random_password()
        user.set_password(password)
        user.is_active = False
        if commit:
            user.save()
        return user

class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name"]
        labels = {
            "first_name": "Nome",
            "last_name": "Cognome"
        }
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        instance = kwargs.pop('instance', None)
        self.username = (instance and instance.username) or None
        self.email = (instance and instance.email) or None
        self.fields['username'] = forms.CharField(disabled=True, initial=self.username)
        self.fields['email'] = forms.CharField(disabled=True, initial=self.email)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['value']
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        self.prop = instance.prop
        self.user = instance.user
        self.value = instance.value
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['value'] = get_field_type(self.prop, instance.value)
    def save(self, commit=True):
        up = super(UserProfileForm, self).save(commit=False)
        up.user = self.user
        up.prop = self.prop
        if commit:
            ready_to_save = manage_before_save(up.value, up.prop.content_type)
            up = UserProfile.objects.update_or_create(
                user=up.user,
                prop=up.prop,
                defaults={"value": up.value}
            )
            #up.save()
            #self.save_m2m()
        return up

class ReminderForm(forms.ModelForm):
    description = forms.CharField(label="Descrizione", widget=forms.Textarea())
    class Meta:
        model = Reminder
        fields = ['user', 'rtype', 'expire_date', 'status', 'title', 'description']
        labels = {
            "user": "Utente",
            "rtype": "Tipo",
            "expire_date": "Data di scadenza",
            "status": "Stato",
            "titolo": "Titolo",
            "description": "Descrizione",
        }
        widgets = {
            'expire_date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'class':'form-control',
                    'placeholder':'Seleziona una data',
                    'type':'date',
                #    'value': ''
                }
            ),
        }

class ReminderEditForm(forms.ModelForm):
    description = forms.CharField(label="Descrizione", widget=forms.Textarea())
    class Meta:
        model = Reminder
        fields = ['rtype', 'expire_date', 'status', 'title', 'description']
        labels = {
            "rtype": "Tipo",
            "expire_date": "Data di scadenza",
            "status": "Stato",
            "titolo": "Titolo",
            "description": "Descrizione",
        }
        widgets = {
            'expire_date': forms.DateInput(
                format=('%d/%m/%Y'),
                attrs={
                    'class':'form-control',
                    'placeholder':'Seleziona una data',
                    'type':'date',
                #    'value': ''
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super(ReminderEditForm, self).__init__(*args, **kwargs)
        instance = kwargs.pop('instance', None)
        self.id = (instance and instance.id) or None
        self.user = (instance and instance.user) or None

