'''
Created on 22.02.2012

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

class bot:
    wiki_server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc');
    token_from_wiki = wiki_server.confluence1.login(WIKI_USER, WIKI_PASS);
    def request(self,content,NamePage,token,server):
        try:
            page = server.confluence1.getPage(token, SPACE, NamePage);
        except:
            parent = server.confluence1.getPage(token, SPACE, TOP_PAGE);
            table_headers = "h1. News Feed \n ||id||date||title||author||\n" 
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
    def get_last_page(self,token,server):
        try:
            geted_page = server.confluence1.search(token,"News Feedsss from github",{"modified" : "LASTWEEK"},100)
            i = 1;
            number = 0;
            value = geted_page[0]['id'];
            while i < len(geted_page):
                if geted_page[i]['id'] > value:
                    number = i;
                    value = geted_page[i]['id']; 
                i += 1;
            LastDate = geted_page[number]['title'][25:];
            NamePage = "News Feedsss from github " + LastDate;
            page = server.confluence1.getPage(token, SPACE, NamePage);
            return str(page);
        except:
            return "NULL"
    def add_news(self):
        parsed = feedparser.parse("https://github.com/organizations/" + org_name + "/" + user_name +".private.atom?token=" + token);
        db = sqlite3.connect('NewsFeedFetcher.db')
        cur = db.cursor()
        cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link)')
        cur.execute('SELECT * FROM RSS')
        record = cur.fetchall();      
        j = len(parsed.entries) - 1;
        k = j;
        last_date_from_bd = "";
        id_from_base = 0;
        if  (record == []): 
            position = 0;
            page_to_string = self.get_last_page(self.token_from_wiki, self.wiki_server); 
            if (page_to_string != "NULL"):
                while (k >= 0): 
                    print page_to_string.count(parsed.entries[k].updated);
                    if (page_to_string.count(parsed.entries[k].updated) != 0):
                        position = k;
                    k -= 1;
                if (position > 0):
                    k = position-1;
                else:
                    k = -1;  
            else:
                k = j;
        else:
            last_date_from_bd = record[-1][1]; 
            id_from_base = record[-1][0];                              
        content = "";
        NamePage = "";    
        while (j >= 0):     
            if (parsed.entries[j].updated > last_date_from_bd):
                cur.execute('insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s","%s")' % (parsed.entries[j].updated,parsed.entries[j].title,parsed.entries[j].author,parsed.entries[j].link))    
                db.commit()   
                if (k >= 0):
                    NamePage = "News Feedsss from github " + parsed.entries[k].updated[:10];
                    id_from_base += 1;
                    if (parsed.entries[k].updated[:10] == parsed.entries[k-1].updated[:10] and k > 0):
                        content += "|" + str(id_from_base) + "|" + parsed.entries[k].updated + "|" + parsed.entries[k].title + "|" + parsed.entries[k].author +"| \n"
                    else:
                        content += "|" + str(id_from_base) + "|" + parsed.entries[k].updated + "|" + parsed.entries[k].title + "|" + parsed.entries[k].author +"| \n"
                        self.request(content,NamePage,self.token_from_wiki, self.wiki_server);
                        content = "";
            j -= 1;
            k -= 1;
        db.close;
    def print_base(self):   
        db = sqlite3.connect('NewsFeedFetcher.db')
        cur = db.cursor()
        cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link)')
        cur.execute('SELECT * FROM RSS')
        record = cur.fetchall();
        db.commit();
        db.close;
        for k in record:
            print k
        

bot = bot();
bot.print_base();
print bot.get_last_page(bot.token_from_wiki, bot.wiki_server)