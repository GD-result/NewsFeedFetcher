
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
    db = sqlite3.connect('NewsFeedFetcher.db')
    cur = db.cursor()
    cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link)')
    db.commit()
    cur.execute('SELECT * FROM RSS')
    record = cur.fetchall()        
    j = len(parsed.entries) - 1;
    content = "";
    NamePage = "";
    while (j >= 0):     
        flag = False
        try:
            if (parsed.entries[j].updated > record[len(record)-1][1]):
                flag = True
        except:
            pass # non record
            flag = True        
        if flag:
            db.commit()  #glyanytb 4tob He picatb ID
            cur.execute('insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s\
            ","%s")' % (parsed.entries[j].updated,parsed.entries[j].title,parsed.entries[j].author,parsed.entries[j].link))
            
            NamePage = "News Feeds from gg " + str(parsed.entries[j].updated[:10])
            server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc')
            tokn = server.confluence1.login(WIKI_USER, WIKI_PASS)
            try:
                page = server.confluence1.getPage(tokn, SPACE, NamePage)
            except:
                if j < len(parsed.entries) - 1:
                    if parsed.entries[j].updated[:10] != parsed.entries[j+1].updated[:10]:
                            NameP = "News Feeds from gg " + str(parsed.entries[j+1].updated[:10])
                            request(content,NameP)
                            content = ""
                content += "|" + parsed.entries[j].updated + "|" + parsed.entries[j].title + "|" + parsed.entries[j].author +"| \n"
            else:
                print page['content'].count(str(parsed.entries[j].updated))
                if page['content'].count(str(parsed.entries[j].updated)) == 0:
                    content += "|" + parsed.entries[j].updated + "|" + parsed.entries[j].title + "|" + parsed.entries[j].author +"| \n"    
            db.commit()
        j -= 1
    request(content,NamePage);    
    db.close
db = sqlite3.connect('NewsFeedFetcher.db')    
c = db.cursor()
c.execute('SELECT * FROM RSS')
record = c.fetchall()
c.execute('SELECT * FROM RSS')
for row in c:
    print row
print
print record[1][1]
#add_to_base();
