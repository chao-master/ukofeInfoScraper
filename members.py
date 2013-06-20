import urllib2 as urllib
import HTMLParser
import datetime
import pprint

class postOverviewParser(HTMLParser.HTMLParser):
    
    def reset(self):
        self.stage = "doc"
        self.current = {"poster":""}
        self.returns = []
        self.possibleNext = None
        self.next = None
        HTMLParser.HTMLParser.reset(self)
    
    def handle_starttag(self,tag,attrs):
        if tag == "nav" and self.stage == "doc":
            self.stage = "nav"
        for a,v in attrs:
            if a == "class":
                if self.stage == "doc":
                    if v == "meta":
                        self.stage = "meta"
                        return
                    elif v == "snippet":
                        self.stage = "snippet"
                        return
            elif self.stage == "meta":
                if a == "data-time":
                    self.current["time"] = datetime.datetime.fromtimestamp(int(v))
                    self.stage = "inMeta"
                    return
                elif a == "title":
                    frags = v.split(" ")
                    frags[0] = frags[0].rjust(2,"0")
                    frags[1] = frags[1][:3]
                    frags[4] = frags[4].rjust(5,"0")
                    self.current["time"] = datetime.datetime.strptime(' '.join(frags),"%d %b %Y at %I:%M %p")
                    self.stage = "inMeta"
                    return
                elif a == "href":
                    if v.startswith("forums"):
                        self.current["section"] = int(v.split(".")[-1][:-1])
                        self.stage = "inMeta"
                        return
                    elif v.startswith("members"):
                        self.stage = "inMeta"
                        if not self.current["poster"]:
                            self.current["poster"] = int(v.split(".")[-1][:-1])
                        return
            elif self.stage == "nav" and a == "href":
                self.possibleNext = v
    
    def handle_endtag(self,tag):
        if self.stage == "meta":
            self.returns.append(self.current)
            self.current = {"poster":""}
            self.stage = "doc"
        elif self.stage == "snippet" and tag == "blockquote":
            self.stage = "doc"
        elif self.stage == "nav" and tag == "nav":
            self.stage = "doc"
        elif self.stage == "inMeta":
            self.stage = "meta"
    
    def handle_data(self,data):
        if data.strip() and self.stage == "snippet":
            self.current[self.stage] = data
        elif self.stage == "nav" and data[:4] == "Next":
            self.next = self.possibleNext

class member():
    def __init__(self,ID):
        self.ID = ID
        self.name = None
        self.join = None
        self.posts = None
        self.postHours = None
        self.postSections = None
        self.likes = None
        self.points = None
        self.followers = None
        self.follers = None
        self.lastUpdated = (None,None,None)
        self.posts = []
        
    def getPostData(self):
        url = "http://ukofequestria.co.uk/search/member?user_id={ID}".format(ID=self.ID)
        self.posts = []
        self.postHours = [0]*24
        self.postSections = {}
        while url:
            parser = postOverviewParser()
            #print "Loading",url,"..."
            page = urllib.urlopen(url)
            parser.feed(page.read())
            parser.close()
            page.close()
            posts,url = parser.returns,parser.next
            
            for p in posts:
                self.postHours[p["time"].hour] += 1
                try:
                    self.postSections[p["section"]] = self.postSections.get(p["section"],0) + 1
                except KeyError:
                    self.postSections["profile"] = self.postSections.get("profile",0) + 1
            
            self.posts.extend(posts)
            if url: url = "http://ukofequestria.co.uk/"+url
    
    def getBaseData(self):
        
        
ripp_ = member(17)
ripp_.getPostData()
pprint.pprint(ripp_.posts)
print ripp_.postHours
print ripp_.postSections
print sum(ripp_.postHours)