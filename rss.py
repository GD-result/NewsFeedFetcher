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
def bbb():
    return add_to_base.cur    

def update(parsed,j,id_n):
    add_to_base.cur.execute("""insert into RSS (id,Date,Title,Author,Link) VALUES \
    (NULL,"%s","%s","%s","%s")""" % (parsed.entries[j].updated, parsed.entries[j].title, parsed.entries[j].author, parsed.entries[j].link))                           
    add_to_base.content += "|" + str(id_n) + "|" + parsed.entries[j].updated + "|" + parsed.entries[j].title + "|" + parsed.entries[j].author + "| \n"
    return add_to_base.content


def add_to_base():
    parsed = feedparser.parse("https://github.com/organizations/"\
 + org_name + "/" + user_name + ".private.atom?token=" + token)
    db = sqlite3.connect('NewsFeedFetcher.db')
    add_to_base.cur = db.cursor()
    add_to_base.cur.execute("""create table if not exists RSS (id INTEGER PRIMARY KEY 
    AUTOINCREMENT,Date,Title,Author,Link)""")
    j = len(parsed.entries) - 25
    add_to_base.content = ""
    NamePage = ""
    one = True
    new = False
    while (j >= 0):
        db.commit()
        add_to_base.cur.execute('SELECT * FROM RSS')
        record = add_to_base.cur.fetchall()
        flag = False
        try:
            if (parsed.entries[j].updated >= record[len(record) - 1][1]):
                id_n = record[len(record)-1][0] + 1
                flag = True
        except:
            flag = True
            id_n = 1
        if flag:          
            NamePage = "News Feeds from github1233333 " + str(parsed.entries[j].updated[:10])
            try:
                if (parsed.entries[j].updated[:10] != parsed.entries[j - 1].updated[:10]) or (one):
                    page = server.confluence1.getPage(wiki_token, SPACE, NamePage)
                    new = True                   
            except:    
                    update(parsed,j,id_n)      
                    if not one:
                        request(add_to_base.content, NamePage)
                        add_to_base.content = ""
                    one = False    
            else:
                if not new:                   
                    update(parsed,j,id_n)
                    one = False
                else:    
                    new = False
                    one = False
                    if page['content'].count(str(parsed.entries[j].updated)) == 0:
                        update(parsed,j,id_n)
            db.commit()
        j -= 1
    request(add_to_base.content, NamePage)
    db.close
add_to_base()

db = sqlite3.connect('NewsFeedFetcher.db')    

c = db.cursor()

c.execute('SELECT * FROM RSS')

record = c.fetchall()

c.execute('SELECT * FROM RSS')

for row in c:

    print row

print
parsed = feedparser.parse("https://github.com/organizations/"\
 + org_name + "/" + user_name + ".private.atom?token=" + token)
i = 1
for e in parsed.entries:
    print i,e
    i +=1

print record[len(record)-1][0]