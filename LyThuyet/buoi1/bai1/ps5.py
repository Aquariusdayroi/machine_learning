# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    
    feed = feedparser.parse(url)
    entries = feed.entries
    
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1

# TODO: NewsStory
class NewsStory ():
    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid
    
    def get_title(self):
        return self. title
    
    def get_description(self):
        return self.description
    
    def get_link(self):
        return self.link
    
    def get_pubdate(self):
        return self.pubdate

        


#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS

# Problem 2
# TODO: PhraseTrigger
class PhraseTrigger(Trigger):

    def __init__(self, phrase):
        self.phrase = phrase
        
    def is_phrase_in(self, text):
        
        text_clean = "".join(" " if c in string.punctuation else c for c in text.lower())
        text_clean = " ".join(text_clean.split()) + " "

        phrase_clean = "".join(" " if c in string.punctuation else c for c in self.phrase.lower())
        phrase_clean = " ".join(phrase_clean.split()) + " "
    
        if  text_clean.find(phrase_clean) != -1:
            return True
        return False

# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_title())
# Problem 4
# TODO: DescriptionTrigger
class DescriptionTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_description())
# TIME TRIGGERS

# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.
class TimeTrigger(Trigger):
    def __init__(self, time_data):
        format_data =  "%d %b %Y %H:%M:%S"

        time = datetime.strptime(time_data, format_data)
        self.time = time
        
# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def evaluate(self, story):
        try:
            return story.get_pubdate() < self.time
        except:
            self.time = self.time.replace(tzinfo=pytz.timezone("EST"))
            return story.get_pubdate() < self.time
    
class AfterTrigger(TimeTrigger):
    def evaluate(self, story):
        try:
            return story.get_pubdate() > self.time
        except:
            self.time = self.time.replace(tzinfo=pytz.timezone("EST"))
            return story.get_pubdate() > self.time

# COMPOSITE TRIGGERS

# Problem 7
# TODO: NotTrigger
class NotTrigger(Trigger):
    def __init__(self, T):
        self.T = T

    def evaluate(self, x):
        return not self.T.evaluate(x)
        
# Problem 8
# TODO: AndTrigger
class AndTrigger(Trigger):
    def __init__(self, F, S):
        self.F = F
        self.S = S
    
    def evaluate(self, story):
        return self.F.evaluate(story) and self.S.evaluate(story)
# Problem 9
# TODO: OrTrigger
class OrTrigger(Trigger):
    def __init__(self, F, S):
        self.F = F
        self.S = S
    
    def evaluate(self, story):
        return self.F.evaluate(story) or self.S.evaluate(story)

#======================
# Filtering
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    # This is a placeholder
    # (we're just returning all the stories, with no filtering)
    a = []
    for storie in stories:
        for trigger in  triggerlist:
            if trigger.evaluate(storie):
                a.append(storie)
    return a



#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    # TODO: Problem 11
    # 'lines' is the list of lines that you need to parse and for which you need
    # to build triggers

    # Initialize trigger mapping dictionary
    t_map = {"TITLE": TitleTrigger,
            "DESCRIPTION": DescriptionTrigger,
            "AFTER": AfterTrigger,
            "BEFORE": BeforeTrigger,
            "NOT": NotTrigger,
            "AND": AndTrigger,
            "OR": OrTrigger
            }
    
    trigger_dict = {}
    trigger_list = [] 

    def line_reader(line):
        data = line.split(',')
        if data[0] != "ADD":
            if data[1] == "OR" or data[1] == "AND":
                trigger_dict[data[0]] = t_map[data[1]](trigger_dict[data[2]],
                        trigger_dict[data[3]])
            else:
                trigger_dict[data[0]] = t_map[data[1]](data[2])
        else: 
            trigger_list[:] += [trigger_dict[t] for t in data[1:]]

    for line in lines:
        line_reader(line)
    
    return trigger_list   

    print(lines) # for now, print it so you see what it contains!



SLEEPTIME = 10 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("election")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Clinton")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]

        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line 
        triggerlist = read_trigger_config('triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            # print("helo")
            # stories.extend(process("http://news.yahoo.com/rss/topstories"))
         
            
            stories = filter_stories(stories, triggerlist)
            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

