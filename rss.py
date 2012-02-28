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
from conf import title


class bot:
    wiki_server = xmlrpclib.ServerProxy('https://wiki.griddynamics.net/rpc/xmlrpc')
    wiki_token = wiki_server.confluence1.login(WIKI_USER, WIKI_PASS)
    def request(self, content, name_page, wiki_token, wiki_server):
        """
        request(content, name_page, wiki_token, wiki_server)
        
        This function sends the content to the specified wiki page 
        and create a new page, if this page does not exist
        Input:
            content - Required unicode
            name_page - Required unicode
            wiki_token - Required string
            wiki_server - Required instance
        """ 
        try:
            page = wiki_server.confluence1.getPage(wiki_token, SPACE, name_page)
        except:
            parent = wiki_server.confluence1.getPage(wiki_token, SPACE, TOP_PAGE)
            table_headers = "h1. News Feed (UTC) \n ||id||date||title||author||\n" 
            page={
                  'parentId': parent['id'],
                  'space': SPACE,
                  'title': name_page,
                  'content': table_headers + content
                  }
            wiki_server.confluence1.storePage(wiki_token, page)
        else:
            page['content'] += content
            wiki_server.confluence1.updatePage(wiki_token, page,{'versionComment':'','minorEdit':1})
    def get_last_page(self,wiki_token, wiki_server):
        """
        get_last_page(wiki_token,wiki_server)
        
        This function returns the last added page from wiki or null if the page does not exists
        Input:
            wiki_token - Required string
            wiki_server - Required instance
        """
        try:
            geted_page = wiki_server.confluence1.search(wiki_token,title,{"modified" : "LASTWEEK"},100)
            i = 1
            number = 0
            value = geted_page[0]['id']
            while i < len(geted_page):
                if geted_page[i]['id'] > value:
                    number = i
                    value = geted_page[i]['id'] 
                i += 1
            LastDate = geted_page[number]['title'][len(title) + 1:]  # get Date in name_page
            name_page = title + " " + LastDate
            page = wiki_server.confluence1.getPage(wiki_token, SPACE, name_page)
            return str(page)
        except:
            return "NULL"
    def add_news(self):
        """
        add_news()
        
        This function parse the news and forms the data base. The main function.
        """
        parsed = feedparser.parse("https://github.com/organizations/" + org_name + "/" + user_name +".private.atom?token=" + token)
        db = sqlite3.connect('NewsFeedFetcher.db')
        cur = db.cursor()
        cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link)')
        cur.execute('SELECT max(id),Date FROM RSS')
        record = cur.fetchall()
        cur.fetchall()
        j = len(parsed.entries) - 1
        k = j
        last_date_from_db = ""
        id_from_db = 0
        if  (record[0][0] == None): 
            position = 0
            page_to_string = self.get_last_page(self.wiki_token, self.wiki_server)
            #print page_to_string 
            if (page_to_string != "NULL"):
                while (k >= 0): 
                    if (page_to_string.count(parsed.entries[k].updated) != 0):
                        position = k
                    k -= 1
                if (position > 0):
                    k = position - 1
                else:
                    k = -1
            else:
                k = j
        else:
            last_date_from_db = record[0][1]
            id_from_db = record[0][0]                          
        content = ""
        name_page = ""    
        while (j >= 0):  
            if (parsed.entries[j].updated > last_date_from_db):
                cur.execute('insert into RSS (id,Date,Title,Author,Link) VALUES (NULL,"%s","%s","%s","%s")'\
                 % (parsed.entries[j].updated,parsed.entries[j].title,parsed.entries[j].author,parsed.entries[j].link))    
                db.commit()   
                if (k >= 0):
                    name_page = title + " " + parsed.entries[k].updated[:10]  # [:10] Date without time YYYY-MM-DD
                    id_from_db += 1
                    if (parsed.entries[k].updated[:10] == parsed.entries[k-1].updated[:10] and k > 0):  # [:10] Date without time YYYY-MM-DD
                        content += "|" + str(id_from_db) + "|" + parsed.entries[k].updated + "|" \
                        + parsed.entries[k].title + "|" + parsed.entries[k].author +"| \n"
                    else:
                        content += "|" + str(id_from_db) + "|" + parsed.entries[k].updated + "|" \
                        + parsed.entries[k].title + "|" + parsed.entries[k].author +"| \n"
                        self.request(content,name_page,self.wiki_token, self.wiki_server)
                        content = ""
            j -= 1
            k -= 1
        db.close
    def print_base(self):
        """
        print base()
        
        Use this function to print all data base in console
        """  
        db = sqlite3.connect('NewsFeedFetcher.db')
        cur = db.cursor()
        cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT,Date,Title,Author,Link)')
        cur.execute('SELECT * FROM RSS')
        db.commit()
        db.close
        for elem in cur:
            print elem
        

bot = bot()
#print bot.get_last_page(bot.wiki_token, bot.wiki_server)
#bot.add_news()
#bot.print_base()
