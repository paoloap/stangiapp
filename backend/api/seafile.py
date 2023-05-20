from django.conf import settings
import os
import requests
from .models import get_user_setting, set_user_setting, get_deleted_repo, add_log

login_url = settings.SF_API_URL + 'api2/auth-token/'
users_url = settings.SF_API_URL + 'api/v2.1/admin/users/'
repos_url = settings.SF_API_URL + 'api/v2.1/repos/'
share_url = settings.SF_API_URL + 'api/v2.1/admin/shares/'
upload_url = settings.SF_API_URL + 'api/v2.1/upload-links/'
update_pwd_template = settings.SF_API_URL + 'api/v2.1/admin/users/{}/'
files_template = repos_url + '{}/dir/'
file_req_template = repos_url + '{}/file/?p=/{}&reuse=1'
upload_template = upload_url + '{}/upload/'

# ----- PRIVATE FUNCTIONS ----- #

def get_super_token():
    """
    Get Seafile token for admin operations
    
    :type priority: string or None
    :return: the token
    :rtype: string
    """

    login_url = settings.SF_API_URL + 'api2/auth-token/'
    admin_email = settings.SF_API_ACC['username']
    admin_pwd = settings.SF_API_ACC['password']

    r = requests.post(
        login_url,
        data={'username': admin_email, 'password': admin_pwd}
    )
    return r.json()['token']

    try:
        return r.json()['token']
    except (ValueError, KeyError) as e:
        return None

def exists_in_sf(super_token, user):
    """
    Check if a user in Django is associated to an user on Seafile
    
    :param str super_token: The admin token
    :param User user: The user
    :type priority: boolean or None
    :return: True if the user exists in Seafile, False otherwise
    :rtype: boolean
    """
    users_url = settings.SF_API_URL + 'api/v2.1/admin/users/'
    email = user.email
    r = requests.get(
        users_url,
        headers={'Authorization': 'Token ' + super_token}
    )
    users_list = r.json()['data']
    for u in users_list:
        if u['email'] == email:
            return True
    return False

def create_sf_repo(super_token, user, key):
    """
    Create a repo of 'key' type for a user
    
    :param str super_token: The admin token
    :param User user: The user
    :param str key: The repo type, which will be used as prefix when defining its name
    :return: "OK" if everyting went ok, "KO - {error_msg}" if something wrong happened
    :rtype: string
    """
    act = "SFRepoCreate"
    email = user.email
    username = user.username
    share_url = settings.SF_API_URL + 'api/v2.1/admin/shares/'
    repos_url = settings.SF_API_URL + 'api/v2.1/repos/'
    create_repo_url = settings.SF_API_URL + 'api2/repos/'
    headers = {'Authorization': 'Token ' + super_token}
    error_tmpl = ""
    error_msg = ""

    create_repo_call = requests.post(
        create_repo_url,
        headers=headers,
        data={'name': key + '_' + username}
    )
    c_status = create_repo_call.status_code
    if c_status == 200:
        # now get the repo_id and then share the library with the user
        try:
            repo_id = create_repo_call.json()['repo_id']
        except(KeyError, ValueError) as e:
            error_tmpl = "can't get id for repo (key: {}, user: {}), but call returned 200"
            error_msg = error_tmpl.format(key, email)
            add_log(user, act, "KO - {}".format(error_msg))
            return "KO - {}".format(error_msg)
        permission = 'r'
        if key == 'up':
            permission = 'rw'
        add_log(user, act, "OK - repo name: {}_{}".format(key, username))
        act = 'SFRepoShare'
        share_lib_call = requests.post(
            share_url,
            headers=headers,
            data={
                'repo_id': repo_id,
                'share_type': 'user',
                'share_to': email,
                'permission': permission
            }
        )
        s_status = share_lib_call.status_code
        if s_status == 200:
            try:
                ret_data = share_lib_call.json()
                try:
                    success = ret_data['success']
                except KeyError:
                    try:
                        fail_msg = ret_data['error_msg']
                    except KeyError:
                        error_tmpl = "didn't get fail msg for share repo call ({} {})"
                        error_msg = error_tmpl.format(key, email)
                        add_log(user, act, "KO - {}".format(error_msg))
                        return "KO - {}".format(error_msg)
                    error_tmpl = "share repo call (key: {}, user: {} failed with reason {}"
                    error_msg = error_tmpl.format(key, email, fail_msg)
                    add_log(user, act, "KO - {}".format(error_msg))
                    return "KO - {}".format(error_msg)
                set_sf_repo_id(user, key, repo_id)
                add_log(user, act, "OK - repo name: {}_{}".format(key, username))
                return "OK"
            except(KeyError, ValueError) as e:
                error_tmpl = "no data from share repo call (key: {}, user: {}), but returned 200"
                error_msg = error_tmpl.format(key, email)
                add_log(user, act, "KO - {}".format(error_msg))
                return "KO - {}".format(error_msg)
        else:
            error_tmpl = "share repo call (key: {}, user: {}) returned {}"
            error_msg = error_tmpl.format(key, email, s_status)
            add_log(user, act, "KO - {}".format(error_msg))
            return "KO - {}".format(error_msg)
    else:
        error_tmpl = "create repo call (key: {}, user: {}) returned {}"
        error_msg = error_tmpl.format(key, email, c_status)
        add_log(user, act, "KO - {}".format(error_msg))
        return "KO - {}".format(error_msg)

def refresh_sf_token(super_token, user, password):
    """
    Refresh a Seafile token, save it on db and return it. Create the user if it doesn't exist
    
    :param str super_token: The admin token
    :param User user: The user
    :param str password: The Seafile password
    :return: "OK" if everyting went ok, "KO - {error_msg}" if something wrong happened
    :rtype: string
    """
    act = "SFLogin"
    email = user.email
    username = user.username
    login_url = settings.SF_API_URL + 'api2/auth-token/'
    update_pwd_template = settings.SF_API_URL + 'api/v2.1/admin/users/{}/'
    new_user = not exists_in_sf(super_token, user)
    if new_user:
        # we need to create the user (and its repos)
        act = "SFCreateUser"
        users_url = settings.SF_API_URL + 'api/v2.1/admin/users/'
        r = requests.post(
            users_url,
            headers={'Authorization': 'Token ' + super_token},
            data={
                'email': email,
                'password': password,
                'name': "{} {}".format(user.first_name, user.last_name)
            }
        )
        try:
            result = r.json()
        except ValueError:
            error_tmpl = "couldn't create the user {} on Seafile"
            error_msg = error_tmpl.format(email)
            add_log(user, act, "KO - {}".format(error_msg))
            return "KO - {}".format(error_msg)
        add_log(user, act, "OK - user: {}".format(email))
        up_repo_create_msg = create_sf_repo(super_token, user, 'up')
        down_repo_create_msg = create_sf_repo(super_token, user, 'down')
        if up_repo_create_msg != "OK" or down_repo_create_msg != "OK":
            error_tmpl = "error creating repos for user {}. returned messages:\n {}\n {}"
            error_msg = error_tmpl.format(email, up_repo_create_msg, down_repo_create_msg)
            add_log(user, act, "KO - {}".format(error_msg))
            return "KO - {}".format(error_msg)
    else:
        # TODO: Add check in case the user exists but doesn't have his repos created
        update_pwd_url = update_pwd_template.format(email)
        r = requests.put(
            update_pwd_url,
            headers={'Authorization': 'Token ' + super_token},
            data={'password': password}
        )
        try:
            result = r.json()
        except ValueError:
            error_tmpl = "couldn't update password for user {}  on Seafile"
            error_msg = error_tmpl.format(email)
            add_log(user, act, "KO - {}".format(email))
            return "KO - {}".format(error_msg)
    r = requests.post(
        login_url,
        data={'username': email, 'password': password}
    )
    try:
        new_token = r.json()['token']
    except (ValueError, KeyError) as e:
        error_tmpl = "coudn't extract token for user {} after refresh call"
        error_msg = error_tmpl.format(email)
        add_log(user, act, "KO - {}".format(email))
        return "KO - {}".format(error_msg)
    set_sf_token(user, new_token) 
    return "OK - user: {}".format(email)

# ----- PUBLIC FUNCTIONS ----- #

def init_sf_session(user, password):
    """
    Renew Seafile session for the user with the current password.
    To use when a user logins (to refresh his token), and when we change user's password
    
    :param User user: The user
    :param str password: User's password
    :return: "OK" if everyting went ok, "KO - {error_msg}" if something wrong happened
    :rtype: string
    """
    super_token = get_super_token()
    return refresh_sf_token(super_token, user, password)
    
def get_sf_repo(user, key):
    """
    Get the list of files for each reminder related to a repo, and the ones
    that are not connected to any reminder
    
    :param User user: The user
    :param str key: 'down' or 'up', depending on what repo we want
    :return:
        a dictionary set like the following samples
        {
            'result': 'OK',
            'file_list': {
                '0': ['file1.pdf', 'file2.doc'],
                '4': ['_4_file.xls],
                '15': ['_15_test.txt', '_15_file.pdf']
            }
        }
        {
            'result': 'KO',
            'msg': 'can't retrieve repo detail (key: 8, user: email@domain.com): Status code: 401'
        }
    :rtype: dictionary
    """
    email = user.email
    files_template = settings.SF_API_URL + 'api/v2.1/repos/{}/dir/'
    sf_token = get_sf_token(user)
    repo_id = get_sf_repo_id(user, key)
    url = files_template.format(repo_id)
    r = requests.get(
        url,
        headers={'Authorization': 'Token ' + sf_token}
    )
    r_status = r.status_code
    if r.status_code == 200:
        try:
            files = r.json()
        except ValueError:
            error_tmpl = "can't retrieve repo detail (key: {}, user: {}) but status code 200"
            error_msg = error_tmpl.format(key, email)
            z = "a" + 3
            return {
                "result": "KO",
                "msg": error_msg
            }
        repo_list = {}
        for f in files['dirent_list']:
            file_name = f['name']
            splitted_name = file_name.split('_', 3)
            reminder_id = str((splitted_name[0] == "" and splitted_name[1]) or "0")
            try:
                already_into = repo_list[reminder_id]
            except KeyError:
                repo_list[reminder_id] = []
            repo_list[reminder_id].append(file_name)
        return {
            "result": "OK",
            "file_list": repo_list
        }
    else:
        error_tmpl = "can't retrieve repo detail (key: {}, user: {}). Status code: {}"
        error_msg = error_tmpl.format(key, email, r.status_code)
        return {
            "result": "KO",
            "msg": error_msg
        }
        
def download_from_sf(user, repo_type, file_name):
    """
    Downloads a file from user's download repository and puts it into 
    settings.DOWNLOAD_PATH directory, so tht it can be taken and sent to the user.
    
    :param User user: The user
    :param str file_name: The file name
    :return: "OK" if everyting went ok, "KO - {error_msg}" if something wrong happened
    :rtype: string
    """
    sf_token = get_sf_token(user)
    repo_id = get_sf_repo_id(user, repo_type)
    api_url = settings.SF_API_URL
    file_req_template = api_url + 'api2/repos/{}/file/?p=/{}&reuse=1'
    work_path = settings.DOWNLOAD_PATH
    file_req_url = file_req_template.format(repo_id, file_name)
    file_req = requests.get(
        file_req_url,
        headers={'Authorization': 'Token ' + sf_token}
    )
    try:
        file_link = file_req.json()
    except ValueError:
        error_tmpl = "can't get file link for download (user: {}, file_name: {})"
        error_msg = error_tmpl.format(user.email, file_name)
        return "KO - {}".format(error_msg)
    if not file_link.startswith(settings.SF_API_URL):
        splitted = file_link.split('/', 4)
        wrong_domain = "{0}//{1}/".format(splitted[0], splitted[2])
        file_link = file_link.replace(wrong_domain, settings.SF_API_URL)
    r = requests.get(
        file_link,
        stream=True
    )
    if r.ok:
        with open(work_path / file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        return "OK"
    else:  # HTTP status code 4XX/5XX
        error_tmpl = "file link request failed with status {} (user: {}, file_name: {})"
        error_msg = error_tmpl.format(r.status_code, user.email, file_name)
        return "KO - {}".format(error_msg)

def get_file_info_from_sf(user, file_name, repo_type):
    """
    Downloads a file from user's download repository and puts it into 
    settings.DOWNLOAD_PATH directory, so tht it can be taken and sent to the user.
    
    :param User user: The user
    :param str file_name: The file name
    :return: "OK" if everyting went ok, "KO - {error_msg}" if something wrong happened
    :rtype: string
    """
    sf_token = get_sf_token(user)
    repo_id = get_sf_repo_id(user, repo_type)
    #api_url = settings.SF_API_URL
    #file_req_template = api_url + 'api2/repos/{}/file/?p=/{}&reuse=1'
    #work_path = settings.DOWNLOAD_PATH
    #file_req_url = file_req_template.format(repo_id, file_name)
    #file_req = requests.get(
    #    file_req_url,
    #    headers={'Authorization': 'Token ' + sf_token}
    #)
    #try:
    #    file_link = file_req.json()
    #except ValueError:
    #    error_tmpl = "can't get file link for download (user: {}, file_name: {})"
    #    error_msg = error_tmpl.format(user.email, file_name)
    #    return "KO - {}".format(error_msg)
    #dl_link = "{0}?dl=1".format(file_link)
    file_info_url = f"{settings.SF_API_URL}api2/repos/{repo_id}/file/detail/?p=/{file_name}"
    file_info_response = requests.get(
        file_info_url,
        headers={'Authorization': 'Token ' + sf_token}
    )
    try:
        file_info = file_info_response.json()
    except ValueError:
        error_tmpl = "can't get file info (user: {}, file_name: {})"
        error_msg = error_tmpl.format(user.email, file_name)
        return "KO - {}".format(error_msg)
    return {
        "size": file_info["size"],
        "date_time": file_info["last_modified"]
    }
        
    #return file_link + "?dl=1"
    #r = requests.get(
    #    file_link,
    #    stream=True
    #)
    #if r.ok:
    #    with open(work_path / file_name, 'wb') as f:
    #        for chunk in r.iter_content(chunk_size=1024 * 8):
    #            if chunk:
    #                f.write(chunk)
    #                f.flush()
    #                os.fsync(f.fileno())
    #    return "OK"
    #else:  # HTTP status code 4XX/5XX
    #    error_tmpl = "file link request failed with status {} (user: {}, file_name: {})"
    #    error_msg = error_tmpl.format(r.status_code, user.email, file_name)
    #    return "KO - {}".format(error_msg)

def upload_to_sf(user, file_name):
    """
    Uploads a file already present into settings.UPLOAD_PATH directory to user's upload repository.
    
    :param User user: The user
    :param str file_name: The file name
    :return: "OK" if everyting went ok, "KO - {error_msg}" if something wrong happened
    :rtype: string
    """
    upload_url = settings.SF_API_URL + 'api/v2.1/upload-links/'
    sf_token = get_sf_token(user)
    repo_id = get_sf_repo_id(user, 'up')
    work_path = settings.UPLOAD_PATH
    file_path = work_path / file_name
    headers = {'Authorization': 'Token ' + sf_token}
    # Generate upload link
    up_link_req = requests.post(
        upload_url,
        headers=headers,
        data={'repo_id': repo_id, 'path': '/'}
    )
    if up_link_req.status_code == 200:
        # Upload the file
        upload_template = settings.SF_API_URL + 'api/v2.1/upload-links/{}/upload/'
        try:
            up_token = up_link_req.json()['token']
        except (ValueError, KeyError) as e:
            error_tmpl = "coudn't get upload_token (user: {}, file_name: {})"
            error_msg = error_tmpl.format(user.email, file_name)
            return "KO - {}".format(error_msg)
        up_req = requests.get(
            upload_template.format(up_token),
            headers=headers
        )
        if up_req.status_code == 200:
            try:
                remote_path = up_req.json()['upload_link']
            except (ValueError, KeyError) as e:
                error_tmpl = "coudn't get remote upload link (user: {}, file_name: {})"
                error_msg = error_tmpl.format(user.email, file_name)
                return "KO - {}".format(error_msg)
            file_to_go = open(file_path,'rb')
            if not remote_path.startswith(settings.SF_API_URL):
                splitted = remote_path.split('/', 4)
                wrong_domain = "{0}//{1}/".format(splitted[0], splitted[2])
                remote_path = remote_path.replace(wrong_domain, settings.SF_API_URL)
            go_upload = requests.post(
                remote_path,
                params={'ret-json': '1'},
                files={'file': file_to_go, 'filename': file_name, 'parent_dir': '/', 'replace': '1' }
            )
            if go_upload.status_code == 200:
                os.remove(file_path)
                return "OK"
            else:
                error_tmpl = "file upload failed with status {} (user: {}, file_name: {})"
                error_msg = error_tmpl.format(go_upload.status_code, user.email, file_name)
                return "KO - {}".format(error_msg)
        else:
            error_tmpl = "upload link request failed with status {} (user: {}, file_name: {})"
            error_msg = error_tmpl.format(up_req.status_code, user.email, file_name)
            return "KO - {}".format(error_msg)
    else:
        error_tmpl = "upload link generation request failed with status {} (user: {}, file_name: {})"
        error_msg = error_tmpl.format(up_link_req.status_code, user.email, file_name)
        return "KO - {}".format(error_msg)

def delete_file(user, file_name):
    up_repo_id = get_sf_repo_id(user, "up")
    sf_token = get_sf_token(user)
    headers = {'Authorization': 'Token ' + sf_token}
    delete_file_url = f"{settings.SF_API_URL}api2/repos/{up_repo_id}/file/?p={file_name}"
    delete_file_response = requests.delete(
        delete_file_url,
        headers=headers
    )
    try:
        response = delete_file_response.json()
    except ValueError:
        return False
    if response == "success":
        return True
    return False

def get_sf_token(user):
    """
    Get a user's Seafile token
    
    :param User user: The user
    :type priority: string or None
    :return: User's token
    :rtype: string
    """
    return get_user_setting(user, 'sf_token')

def set_sf_token(user, sf_token):
    """
    Store a user's Seafile token on db
    
    :param User user: The user
    :param str sf_token: The token
    """
    set_user_setting(user, 'sf_token', sf_token)

def get_sf_repo_id(user, key):
    return get_user_setting(user, key + '_repo_id')

def set_sf_repo_id(user, key, repo_id):
    set_user_setting(user, key + '_repo_id', repo_id)

