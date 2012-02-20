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

#server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc');
#git_token = server.confluence1.login(WIKI_USER, WIKI_PASS);

def request(content, NamePage):
    #server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc');
    serv = getattr(add_to_base,"server")
    git_token = serv.confluence1.login(WIKI_USER, WIKI_PASS);
    tok = git_token
    print tok, serv
    try:
        page = serv.confluence1.getPage(tok, SPACE, NamePage);
    except:
        parent = serv.confluence1.getPage(tok, SPACE, TOP_PAGE);
        table_headers = "h1. News Feed (UTC) \n ||date||title||author||\n" 
        page = {
              'parentId': parent['id'],
              'space': SPACE,
              'title': NamePage,
              'content': table_headers + content
              }
        serv.confluence1.storePage(tok, page);
    else:
        page['content'] += content;
        serv.confluence1.updatePage(tok, page,{'versionComment':'','minorEdit':1});


def add_to_base():
    add_to_base.server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc')
    add_to_base.git_token = add_to_base.server.confluence1.login(WIKI_USER, WIKI_PASS)
    print add_to_base.git_token, add_to_base.server
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
    while (j >= 0):     
        #i = 0;
        flag = False
        ######while (i < len(record)):
        try:
            if (parsed.entries[j].updated > record[len(record)-1][1]):
                flag = True
        except:
            pass # non record
            flag = True        
        ####     #       break;
        ####   # i += 1;
        if flag:
            db.commit()  #glyanytb 4tob He picatb ID
            cur.execute('insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s","%s")' % (parsed.entries[j].updated,parsed.entries[j].title,parsed.entries[j].author,parsed.entries[j].link))
            
            NamePage = "News Feeds from ggg " + str(parsed.entries[j].updated[:10])
            #server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc')
            #git_token = server.confluence1.login(WIKI_USER, WIKI_PASS)
            try:
                page = add_to_base.server.confluence1.getPage(git_token, SPACE, NamePage)
            except:
                if j < len(parsed.entries) - 1:
                    if parsed.entries[j].updated[:10] != parsed.entries[j + 1].updated[:10]:
                            NameP = "News Feeds from ggg " + str(parsed.entries[j + 1].updated[:10])
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
add_to_base()
