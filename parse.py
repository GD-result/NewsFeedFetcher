import requests
import json
import sqlite3
import base64

from conf import github_login
from conf import github_pass
from conf import org_name
from conf import use_token
from conf import oauth_token
from conf import db_name


def get_news():
    """
    get_news()
    
    This function get news from github and send it to add_news() function
    """
    events_url = "https://api.github.com/users/%s/events/orgs/%s" % (github_login, org_name)
    auth_type = ""
    if use_token:
        events_url += "?access_token=" + oauth_token
    else:
        auth_type = (github_login, github_pass)
    r = requests.get(url = events_url, auth = auth_type)
    return r
    
    
def add_news():
    """
    add_news()
    
    This function get news array and forms the data base. The main function.
    """
    r = get_news()
    if (r.status_code == requests.codes.OK):
        news = json.loads(r.content)
    else:
        print r.headers
        return -1    
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT, Date, Author, EventType, Summary TEXT)')
    cur.execute('SELECT max(id),Date FROM RSS')
    record = cur.fetchall()
    cur.fetchall()
    if  (not record[0][0]): 
        last_date_from_db = ""
    else:
        last_date_from_db = record[0][1]
    count = 0
    #print news[0]
    while (count < len(news) and news[count]['created_at'] > last_date_from_db):
        count += 1
        #print "ololo"
    count -= 1
    while (count >= 0):
        summary = json.dumps(news[count])
        #print news[count]
        cur.execute('insert into RSS (id, Date, Author, EventType, Summary) VALUES (NULL,"%s","%s","%s","%s")'\
        % (news[count]['created_at'], news[count]['actor']['login'], news[count]['type'], base64.b64encode(summary)))
        db.commit()  
        count -= 1
    db.close 

    
def print_base():
    """
    print base()
    
    Use this function to print all data base in console
    Test function (example)
    """  
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link,Summary)')
    cur.execute('SELECT * FROM RSS')
    db.commit()
    db.close
    rec = cur.fetchall()
    for i in range(len(rec)):
        n = base64.b64decode(rec[i][4])
        print rec[i][0], rec[i][1], rec[i][2], rec[i][3], n
        #print json.loads(n)
#    for elem in cur:
#        print elem
        

add_news()
print_base()      