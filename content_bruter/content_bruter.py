import urllib2
import threading
import Queue
import urllib

threads = 50
target_url = "http://www.glodon.com"
wordlist_file = './svndigger-all.txt'
resume = None
user_agent = "Mozilla/5.0(X11; Linux x86_64; rv:19.0) Gecko/20100101Firefox/19.0"

def build_worldlist(wordlist_file):
    fd = open(wordlist_file, "rb")
    raw_input = fd.readlines()
    fd.close
    
    found_resume = False
    words = Queue.Queue()
    
    for word in raw_input:
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from : %s" % resume
        else:
            words.put(word)
    return words
def dir_bruter(word_queue, extensions = None):
    while not word_queue.empty():
        attemp = word_queue.get()
        attemp_list = []
        
        if "." in attemp:
            attemp_list.append("/%s/" % attemp)
        else:
            attemp_list.append("/%s" % attemp)
        
        if extensions:
            for extension in extensions:
                attemp_list.append("/%s/" % attemp)
        
        for brute in attemp_list:
            url = "%s%s" % (target_url, urllib.quote(brute))
            try:
                request = urllib2.Request(url)
                request.add_header("User-Agent", user_agent)
                response = urllib2.urlopen(request)
                if len(response.read()) and response.code == 200:
                    print "[%d] => %s" %(response.code, url)
            except urllib2.URLError, e:
                #if hasattr(e, 'code') and e.code != 404:
                    #print "!!! %d => %s" %(e.code, url)
                pass
word_queue = build_worldlist(wordlist_file)
extensions = ['.php', '.bak', '.orig', '.inc']

for i in range(threads):
    t = threading.Thread(target = dir_bruter, args = (word_queue, extensions,))
    t.start()