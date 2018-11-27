import accountlockout.helper.attemps_helper
import accountlockout.helper.ip_helper
from .users import get_username_from_request

def check(request, login_unsuccessful,
                  get_username=get_username_from_request,
                  username=None):
    """ check the request, and process results"""
    ip_address = accountlockout.helper.ip_helper.__get(request)
    username = username or get_username(request)

    if not login_unsuccessful:
        # user logged in -- forget the failed attempts
        accountlockout.helper.attemps_helper.__reset_failed(ip_address=ip_address, username=username)
        return True
    else:
        # add a failed attempt for this user
        return accountlockout.helper.attemps_helper.__record_failed(request, ip_address, username)

