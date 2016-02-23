import httplib, urllib

class pushover_connection:
    def __init__(self,apptoken,userkey):
        self.apptoken = apptoken
        self.userkey = userkey

    def send_message(self,message):
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST","/1/messages.json",
                     urllib.urlencode({
                         'token': self.apptoken,
                         'user': self.userkey,
                         'message': message}),
                     { 'Content-type': "application/x-www-form-urlencoded"})
