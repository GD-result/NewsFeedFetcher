import requests
import json
import sqlite3

from conf import github_login
from conf import github_pass
from conf import org_name
from conf import use_token
from conf import oauth_token


def get_news():
    events_url = "https://api.github.com/users/%s/events/orgs/%s" % (github_login, org_name)
    auth_type = ""
    if use_token:
        events_url += "?access_token=" + oauth_token
    else:
        auth_type = (github_login, github_pass)
    r = requests.get(url = events_url, auth = auth_type)
    return r
    
    
def add_news():
    r = get_news()
    if (r.status_code == requests.codes.OK):
        news = json.loads(r.content)
    else:
        print r.headers
        return -1    
    db = sqlite3.connect('NewsFeed.db')
    cur = db.cursor()
    cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT, Date, Author, EventType, Summary TEXT)')
    cur.execute('SELECT max(id),Date FROM RSS')
    record = cur.fetchall()
    cur.fetchall()
    if  (record[0][0] == None): 
        last_date_from_db = ""
    else:
        last_date_from_db = record[0][1]
    #print last_date_from_db, count
    count = 0
    #print news[0]
    while (count < len(news) and news[count]['created_at'] > last_date_from_db):
        count += 1
        #print "ololo"
    count -= 1
    #summary = ""
    #summary = json.dumps("iplllllllllllllllllllllllllllllllllllllllllllllm")
    #cur.execute('insert into RSS (id, Date, Author, EventType, Summary) VALUES (NULL,"%s","%s","%s","%s")'\
    #    % (news[count]['created_at'], news[count]['actor']['login'], news[count]['type'], summary))
    while (count >= 0):
        summary = json.dumps(news[count])
        cur.execute('insert into RSS (id, Date, Author, EventType, Summary) VALUES (NULL,"%s","%s","%s","%s")'\
        % (news[count]['created_at'], news[count]['actor']['login'], news[count]['type'], summary))
        db.commit()   
        count -= 1
    db.close
    #print "iiiiii"
    #print summary
    #print type(json.dumps("shgg")) 

    
def print_base():
    """
    print base()
    
    Use this function to print all data base in console
    """  
    db = sqlite3.connect('NewsFeed.db')
    cur = db.cursor()
    cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link,Summary)')
    cur.execute('SELECT max(id), Summary FROM RSS')
    db.commit()
    db.close
    rec = cur.fetchall
    n = json.loads(rec[0][1])
    print n
#    for elem in cur:
#        print elem
        

add_news()
#print_base()      