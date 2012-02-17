'''
Created on 15.02.2012

@author: ninja
'''

import feedparser
import sqlite3
import xmlrpclib

from conf import SPACE
from conf import TOP_PAGE
from conf import WIKI_USER
from conf import WIKI_PASS
from conf import token
from conf import org_name
from conf import user_name

def request(content,NamePage):
    server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc');
    token = server.confluence1.login(WIKI_USER, WIKI_PASS);
    try:
        page = server.confluence1.getPage(token, SPACE, NamePage);
    except:
        parent = server.confluence1.getPage(token, SPACE, TOP_PAGE);
        table_headers = "h1. News Feed \n ||date||title||author||\n" 
        page={
              'parentId': parent['id'],
              'space': SPACE,
              'title': NamePage,
              'content': table_headers + content
              }
        server.confluence1.storePage(token, page);
    else:
        page['content'] += content;
        server.confluence1.updatePage(token, page,{'versionComment':'','minorEdit':1});


def add_to_base():
    parsed = feedparser.parse("https://github.com/organizations/" + org_name + "/" + user_name +".private.atom?token=" + token);
    #print parsed.entries[-1];
    db = sqlite3.connect('NewsFeedFetcher.db')
    cur = db.cursor()
    cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link)')
    db.commit()
    cur.execute('SELECT * FROM RSS')
    record = cur.fetchall()        
    #print parsed.entries[0].updated;
    j = len(parsed.entries) - 1;
    content = "";
    NamePage = "";
    print
    while (j >= 0):     
        i = 0;
        flag = True;
        while (i < len(record)):
            if (parsed.entries[j].updated == record[i][1]):
                    flag = False;
                    break;
            i += 1;
        if flag:
            db.commit()  #glyanytb 4tob He picatb ID
            cur.execute('insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s","%s")' % (parsed.entries[j].updated,parsed.entries[j].title,parsed.entries[j].author,parsed.entries[j].link))
            NamePage = "News Feeds from github " + parsed.entries[j].updated[:10];    
            db.commit()
            if (parsed.entries[j].updated[:10] == parsed.entries[j-1].updated[:10] and j > 0):
                content += "|" + parsed.entries[j].updated + "|" + parsed.entries[j].title + "|" + parsed.entries[j].author +"| \n"
            else:
                request(content,NamePage);
                content = "";
        j -= 1;
    db.close;
    return content

#add_to_base();

k = 
request("gogi","first")
