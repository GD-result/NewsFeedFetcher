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

server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc')
wiki_token = server.confluence1.login(WIKI_USER, WIKI_PASS)


def request(content, NamePage):
    try:
        page = server.confluence1.getPage(wiki_token, SPACE, NamePage)
    except:
        parent = server.confluence1.getPage(wiki_token, SPACE, TOP_PAGE)
        table_headers = "h1. News Feed (UTC) \n||id||date||title||author||\n"
        page = {
              'parentId': parent['id'],
              'space': SPACE,
              'title': NamePage,
              'content': table_headers + content
              }
        server.confluence1.storePage(wiki_token, page)
    else:
        page['content'] += content
        server.confluence1.updatePage(wiki_token, page, {'versionComment': '', \
                                                         'minorEdit': 1})


def add_to_base():
    parsed = feedparser.parse("https://github.com/organizations/"\
 + org_name + "/" + user_name + ".private.atom?token=" + token)
    db = sqlite3.connect('NewsFeedFetcher.db')
    cur = db.cursor()
    cur.execute("""create table if not exists RSS (id INTEGER PRIMARY KEY 
    AUTOINCREMENT,Date,Title,Author,Link)""")
    j = len(parsed.entries) - 1
    content = ""
    NamePage = ""
    one = True
    new = False
    while (j >= 0):
        db.commit()
        cur.execute('SELECT * FROM RSS')
        record = cur.fetchall()
        flag = False
        try:
            if (parsed.entries[j].updated >= record[len(record) - 1][1]):
                id = record[len(record)-1][0] + 1
                flag = True
        except:
            flag = True
            id = 1
        if flag:          
            NamePage = "News Feeds from githubbb " + str(parsed.entries[j].updated[:10])
            try:
                if (parsed.entries[j].updated[:10] != parsed.entries[j - 1].updated[:10]) or (one):
                    page = server.confluence1.getPage(wiki_token, SPACE, NamePage)
                    new = True                   
            except:    
                    db.commit()  
                    cur.execute("""insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s","%s")""" % (parsed.entries[j].updated, parsed.entries[j].title, parsed.entries[j].author, parsed.entries[j].link))                           
                    content += "|" + str(id) + "|" + parsed.entries[j].updated + "|" +\
                          parsed.entries[j].title + "|" + parsed.entries[j].author + "| \n"      
                    if not one: #
                        request(content, NamePage)
                        content = ""
                    one = False    
            else:
                if not new:                   
                    db.commit()  
                    cur.execute("""insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s","%s")""" % (parsed.entries[j].updated, parsed.entries[j].title, parsed.entries[j].author, parsed.entries[j].link))                       
                    content += "|" + str(id) + "|" + parsed.entries[j].updated + "|" + \
                        parsed.entries[j].title + "|" + parsed.entries[j].author + "| \n"
                else:    
                    new = False
                    if page['content'].count(str(parsed.entries[j].updated)) == 0:
                        db.commit()  
                        cur.execute("""insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s","%s")""" % (parsed.entries[j].updated, parsed.entries[j].title, parsed.entries[j].author, parsed.entries[j].link))            
                        content += "|" + str(id) + "|" + parsed.entries[j].updated + "|" + \
                                parsed.entries[j].title + "|" + parsed.entries[j].author + "| \n"
            db.commit()
        j -= 1
    request(content, NamePage)
    db.close
add_to_base()
