from MoinMoin.auth import BaseAuth

# This is included in case you want to create a log file during testing
import time
def writeLog(*args):
    '''Write an entry in a log file with a timestamp and all of the args.'''
    s = time.strftime('%Y-%m-%d %H:%M:%S ',time.localtime())
    for a in args:
        s = '%s %s;' % (s,a)
    log = open('/tmp/cookie.log', 'a') # +++ location for log file
    log.write('\n' + s + '\n')
    log.close()
    return

class DjangoAuth(BaseAuth):
    
    name = 'DjangoAuth'
    # +++ The next 2 lines may be useful if you are overriding the username method in your themes.
    # +++  If commented out, wiki pages will not have login or logout hyperlinks
    #login_inputs = ['username', 'password'] # +++ required to get a login hyperlink in wiki navigation area
    #logout_possible = True # +++ required to get a logout hyperlink in wiki navigation area
    #login_inputs = ['username', 'password'] # +++ required to get a login hyperlink in wiki navigation area
    logout_possible = False # +++ required to get a logout hyperlink in wiki navigation area
    
    def __init__(self, autocreate=False):
        self.autocreate = autocreate
        BaseAuth.__init__(self)

    def get_profile(self, user_id):
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False, {}
        try:
            self.user_profile = {}
            self.user_profile['username'] = user.username
            self.user_profile['name'] = user.first_name + ' ' + user.last_name
            self.user_profile['email'] = user.email
        except:
            return False, {}
        return True


    def get_session(self, session_id):
        from django.contrib.sessions.models import Session
        try:
            session = Session.objects.get(session_key=session_id)
        except Session.DoesNotExist:
            return False, ''
        try:
            from datetime import datetime
            #Has the session expired?
            if session.expire_date < datetime.now():
                return False, ''
            return True, session #session.session_data
        except:
            return False, ''

    def request(self, request, user_obj, **kw):
        """Return (user-obj,False) if user is authenticated, else return (None,True). """
        # login = kw.get('login') # +++ example does not use this; login is expected in other application
        # user_obj = kw.get('user_obj')  # +++ example does not use this
        # username = kw.get('name') # +++ example does not use this
        # logout = kw.get('logout') # +++ example does not use this; logout is expected in other application
        import Cookie
        user = None  # user is not authenticated
        try_next = True  # if True, moin tries the next auth method in auth list
        otherAppCookie = "sessionid" # +++ username, email,useralias, session ID separated by #
        try:
            #cookie = Cookie.SimpleCookie(request.saved_cookie)
            cookie = Cookie.SimpleCookie(request.cookies)
        except Cookie.CookieError:
            cookie = None # ignore invalid cookies        

        if cookie and otherAppCookie in cookie: # having this cookie means user auth has already been done in other application
            #writeLog('cookie value:', cookie[otherAppCookie].value)
            result, session = self.get_session(cookie[otherAppCookie].value)
            #writeLog('result, session:', [result, session])
            if not result:
                return user, try_next
            session_decoded = session.get_decoded()
            #writeLog('Session Decoded', session_decoded)
            
            try:            
                result = self.get_profile(session_decoded['_auth_user_id'])
            except KeyError:
                writeLog('Could not find user id in decoded cookie')
                return user, try_next
                
            #writeLog('got user profile', self.user_profile)
            
            if not result:
                return user, try_next
                
            from MoinMoin.user import User
            # giving auth_username to User constructor means that authentication has already been done.
            user = User(request, name=self.user_profile['username'], auth_username=self.user_profile['username'], auth_method=self.name)
            changed = False
            if self.user_profile['email'] != user.email: # was the email addr externally updated?
                user.email = self.user_profile['email'];
                changed = True # yes -> update user profile
            if self.user_profile['name'] != user.aliasname: # +++ was the aliasname externally updated?
                user.aliasname = self.user_profile['name'] ;
                changed = True # yes -> update user profile
            
            if user:
                user.create_or_update(changed)
            if user and user.valid:
                try_next = False # have valid user; stop processing auth method list
                #writeLog(str(user), try_next)
        return user, try_next

    def get_django_groups(self, group_list):
        from django.contrib.auth.models import Group, User
        output = {}
        for g_name in group_list:
            output[g_name] = [u.username for u in User.objects.filter(groups__name=g_name)]
        return output
            
