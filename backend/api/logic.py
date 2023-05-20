from django.conf import settings
from django.db import IntegrityError
import requests
#import re
#import json
import os
import tarfile
import datetime
import logging

#from address.models import Address
from .models import *
from .seafile import init_sf_session, get_sf_repo, download_from_sf, get_file_info_from_sf

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# ----- VIEWS ----- #

def get_user_profile(user):
    # Take all 'UserProfile' rows related to the user that made the request
    profile_list = UserProfile.objects.filter(user=user)
    # Take all the 'UserProfileProperty' rows, ordered by 'order' column
    user_profile_props = UserProfileProperty.objects.order_by('order','pk')
    result = []
    for prop in user_profile_props:
        try:
            elem = UserProfile.objects.filter(prop=prop).get(user=user)
        except UserProfile.DoesNotExist:
            elem = None
        try:
            ptype = prop.content_type.name
        except AttributeError:
            ptype = ""
        if elem:
            if ptype == "address":
                addr = Address.objects.get(raw=elem.value)
                result.append({
                    'label' : prop.name,
                    'value' : {
                        'street' : addr.street,
                        'num' : addr.num,
                        'extra' : addr.extra,
                        'locality' : addr.town.name,
                        'state' : addr.town.state.code,
                        'code' : addr.postal_code,
                        'country' : addr.town.state.country.code
                    }
                })
            else:
                result.append({
                    'label' : prop.name,
                    'value' : elem.value
                })
        else:
            result.append({
                'label' : prop.name,
            })
    return result

def get_user_reminders_with_links(user):
    #user_repo = get_user_repo(user)
    down_repo = get_sf_repo(user, 'down')
    up_repo = get_sf_repo(user, 'up')
    try:
        down_repo_list = down_repo['file_list']
        up_repo_list = up_repo['file_list']
    except KeyError:
        return "KO - couldn't retrieve repos"
    reminder_list = Reminder.objects.filter(user=user)
    result = []
    for elem in reminder_list:
        try:
            down_list = down_repo_list[str(elem.id)]
            down_table = []
            for file_name in down_list:
                file_info = get_file_info_from_sf(user, file_name, "down")
                down_table.append({
                    'name': file_name,
                    "size": file_info["size"]
                })
        except KeyError:
            down_table = []
        try:
            up_list = up_repo_list[str(elem.id)]
            up_table = []
            for file_name in up_list:
                file_info = get_file_info_from_sf(user, file_name, "up")
                up_table.append({
                    "name": file_name,
                    "size": file_info["size"],
                    "date_time": file_info["date_time"]
                })
        except KeyError:
            up_table = []
        result.append({
            'id': elem.id,
            'type': elem.rtype.name,
            'expire_date': elem.expire_date,
            'title': elem.title,
            'description': elem.description,
            'status': elem.status.name,
            'down' : down_table,
            'up' : up_table
        })
    return result

def get_global_attachments(user):
    down_repo = get_sf_repo(user, 'down')
    try:
        result = {}
        file_list = down_repo['file_list']["0"]
    except KeyError:
        result["file_list"] = []
        result["error"] = False
        return result
    try:
        result["file_list"] = []
        for file_name in file_list:
            file_info = get_file_info_from_sf(user, file_name, "down")
            result["file_list"].append({
                'name': file_name,
                'link': file_info["link"],
                "size": file_info["size"]
            })
        result["error"] = False

    except KeyError:
        result["error"] = True
        result["file_list"] = []
    return result

def get_user_reminders(user):
    #user_repo = get_user_repo(user)
    down_repo = get_sf_repo(user, 'down')
    up_repo = get_sf_repo(user, 'up')
    try:
        down_repo_list = down_repo['file_list']
        up_repo_list = up_repo['file_list']
    except KeyError:
        return "KO - couldn't retrieve repos"
    reminder_list = Reminder.objects.filter(user=user)
    result = []
    for elem in reminder_list:
        try:
            down_list = down_repo_list[str(elem.id)]
        except KeyError:
            down_list = []
        try:
            up_list = up_repo_list[str(elem.id)]
        except KeyError:
            up_list = []
        result.append({
            'id': elem.id,
            'type': elem.rtype.name,
            'expire_date': elem.expire_date,
            'title': elem.title,
            'description': elem.description,
            'status': elem.status.name,
            'down' : down_list,
            'up' : up_list
        })
    return result

def get_attachment(user, reminder_id, repo_type, file_name):
    uid = user.id
    reminder = Reminder.objects.get(id=reminder_id, user=user)
    if not file_name.startswith(f"_{reminder_id}_"):
        return {
            "result": "ko",
            "error_type": "client",
            "error_msg": "file_not_from_reminder"
        }
    if not reminder:
        return {
            "result": "ko",
            "error_type": "client",
            "error_msg": "reminder_not_found"
        }
    down_result = download_from_sf(user, repo_type, file_name)
    if down_result == 'OK':
        return {
            "result": "ok",
        }
    else:
        return {
            "result": "ko",
            "error_type": "server",
            "error_msg": down_result
        }

def attach_file(user, reminder_id, f):
    rename_tmpl = '_{}_{}'
    rename = rename_tmpl.format(reminder_id, f.name)
    with open(settings.UPLOAD_PATH / rename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    result = upload_to_sf(user, rename)
    if result == 'OK':
        return {'result': 'OK'}
    else:
        return {'result': 'ERROR', 'msg': result}

def set_reminder_status(user, reminder_id, status, is_admin):
    try:
        reminder = Reminder.objects.get(id=reminder_id)
        if not reminder:
            return {
                "result": "ko",
                "error_type": "client",
                "error_msg": "no_reminder"
            }
        if not reminder.user == user:
            return {
                "result": "ko",
                "error_type": "client",
                "error_msg": "no_reminder"
            }
        reminder_status = ReminderStatus.objects.get(name=status)
        if not reminder_status:
            return {
                "result": "ko",
                "error_type": "client",
                "error_msg": "status_not_found"
            }
        if not is_admin and status == "Approvato":
            return {
                "result": "ko",
                "error_type": "client",
                "error_msg": "forbidden_status"
            }
        if reminder_status == reminder.status:
            return {
                "result": "ko",
                "error_type": "client",
                "error_msg": "same_status"
            }

        reminder.status = reminder_status
        reminder.save()
        add_log(user, "ChangeReminderStatus", "OK - new status for reminder {}: {}".format(reminder_id, status))
        return {
            "result": "ok",
            "old_status": reminder_status.name,
            "new_status": status
        }
    except Exception as e:
        logger.error(f"change_reminder_status {user.username}, {reminder_id}, {status}, {is_admin}: {e}")
        return {
            "result": "ko",
            "error_type": "server",
            "error_msg": f"{e}"
        }


# ----- ACCESS TO CLOUD ----- #

def init_cloud(user, password):
    return init_sf_session(user, password)

# ----- SUPPORT TO DEPLOY ----- #

def generate_default_db_data():
    try:
        user_types = []
        user_types.append(UserType(name="Soggetto Privato"))
        user_types.append(UserType(name="Impresa Individuale"))
        user_types.append(UserType(name="Professionista"))
        user_types.append(UserType(name="Società di Persone"))
        user_types.append(UserType(name="Società di Capitali"))

        fiscal_types = []
        fiscal_types.append(FiscalType(name="Semplificata"))
        fiscal_types.append(FiscalType(name="Ordinaria"))
        fiscal_types.append(FiscalType(name="Forfettaria"))

        social_security = []
        social_security.append(SocialSecurityType(name="Gestione Separata INPS"))
        social_security.append(SocialSecurityType(name="Cassa Professionale"))
        social_security.append(SocialSecurityType(name="Nessuna"))

        booleans = []
        booleans.append(BooleanType(name="Sì"))
        booleans.append(BooleanType(name="No"))

        profile_props = []
        profile_props.append(UserProfileProperty(order=1, name='Tipo Soggetto', content_type=ContentType.objects.get(app_label='api', model='usertype')))
        profile_props.append(UserProfileProperty(order=2, name='Codice Ateco', content_type=None))
        profile_props.append(UserProfileProperty(order=3, name='Descrizione', content_type=None))
        profile_props.append(UserProfileProperty(order=4, name='Codice Fiscale', content_type=None))
        profile_props.append(UserProfileProperty(order=5, name='Partita IVA', content_type=None))
        profile_props.append(UserProfileProperty(order=6, name='Indirizzo', content_type=ContentType.objects.get(app_label='api', model='address')))
        profile_props.append(UserProfileProperty(order=7, name='Pec', content_type=None))
        profile_props.append(UserProfileProperty(order=8, name='Telefono', content_type=None))
        profile_props.append(UserProfileProperty(order=9, name='Cellulare', content_type=None))
        profile_props.append(UserProfileProperty(order=10, name='Gestione Fiscale', content_type=ContentType.objects.get(app_label='api', model='fiscaltype')))
        profile_props.append(UserProfileProperty(order=11, name='Gestione Previdenziale', content_type=ContentType.objects.get(app_label='api', model='socialsecuritytype')))
        profile_props.append(UserProfileProperty(order=12, name='Inail', content_type=ContentType.objects.get(app_label='api', model='booleantype')))
        profile_props.append(UserProfileProperty(order=13, name='Matricola Inps', content_type=None))

        setting_props = []
        setting_props.append(UserSettingProperty(name="sf_token"))
        setting_props.append(UserSettingProperty(name="up_repo_id"))
        setting_props.append(UserSettingProperty(name="down_repo_id"))

        actions = []
        actions.append(Action(name="SFRepoShare"))
        actions.append(Action(name="SFRepoCreate"))
        actions.append(Action(name="SFLogin"))
        actions.append(Action(name="SFCreateUser"))
        actions.append(Action(name="PasswordReset"))
        actions.append(Action(name="PasswordChange"))
        actions.append(Action(name="Logout"))
        actions.append(Action(name="Login"))
        actions.append(Action(name="FileUpload"))
        actions.append(Action(name="FileDownload"))
        actions.append(Action(name="ListReminders"))
        actions.append(Action(name="OpenReminder"))
        actions.append(Action(name="ChangeReminderStatus"))

        reminder_status = []
        reminder_status.append(ReminderStatus(name="Attivo"))
        reminder_status.append(ReminderStatus(name="Ignorato"))
        reminder_status.append(ReminderStatus(name="Archiviato"))
        reminder_status.append(ReminderStatus(name="Approvato"))

        reminder_types = []
        reminder_types.append(ReminderType(name="Tassa"))
        reminder_types.append(ReminderType(name="Altro"))

        for ut in user_types:
            ut.save()
        for ft in fiscal_types:
            ft.save()
        for ss in social_security:
            ss.save()
        for bo in booleans:
            bo.save()
        for upp in profile_props:
            upp.save()
        for sp in setting_props:
            sp.save()
        for ac in actions:
            ac.save()
        for rs in reminder_status:
            rs.save()
        for rt in reminder_types:
            rt.save()
        return "generated now"
    except IntegrityError:
        return "already generated (or error)"

