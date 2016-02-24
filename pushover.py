import httplib, urllib

class pushover_connection:
    def __init__(self,apptoken,userkey):
        self.apptoken = apptoken
        self.userkey = userkey

    def send_message(self,message):
        # Create https connection to Pushover
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        # Send message to Pushover
        conn.request("POST","/1/messages.json",
                     urllib.urlencode({
                         'token': self.apptoken,
                         'user': self.userkey,
                         'message': message}),
                     { 'Content-type': "application/x-www-form-urlencoded"})
