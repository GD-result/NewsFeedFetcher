import xmlrpclib
import sqlite3

from conf import SPACE
from conf import TOP_PAGE
from conf import WIKI_USER
from conf import WIKI_PASS
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
            table_headers = "h1. News Feed (UTC) \n ||id||Date||Author||Event Type||\n"
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
            self.last_date = geted_page[number]['title'][len(title) + 1:] # get Date in name_page
            name_page = title + " " + self.last_date
            page = wiki_server.confluence1.getPage(wiki_token, SPACE, name_page)
            return str(page)
        except:
            return None
    def add_news(self):
        """
        add_news()
        The main function. 
        """
        db = sqlite3.connect('NewsFeed.db')
        cur = db.cursor()
        cur.execute('create table if not exists RSS (id INTEGER PRIMARY KEY AUTOINCREMENT, Date, Author, EventType, Summary TEXT)')
        page_to_string = self.get_last_page(self.wiki_token, self.wiki_server)
        if not page_to_string:
            last_id = 0
        else:
            page_to_string = page_to_string.split("|")
            last_id = int(page_to_string[len(page_to_string) - 5])  # Search last id in table from wiki page
        cur.execute('SELECT * FROM RSS WHERE id > %d'%last_id)
        news = cur.fetchall()
        if not news == []:
            content = ""
            name_page = ""
            for i, item in enumerate(news):
                if not item[1][:10] == news[i - 1][1][:10]: # [:10] Date without time YYYY-MM-DD
                    self.request(content, name_page, self.wiki_token, self.wiki_server)
                    content = ""
                name_page = title + " " + item[1][:10] # [:10] Date without time YYYY-MM-DD
                last_id += 1
                content += "|" + str(last_id) + "|" + item[1] + "|" + item[2] + "|" + item[3] + "| \n"
            self.request(content, name_page, self.wiki_token, self.wiki_server)
        db.close       

bot = bot()
bot.add_news()