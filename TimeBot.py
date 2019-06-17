#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime, date
from polybot import *


# In[2]:


class TimeBot(Answers):
    def answer_time(self, NER_dict):
        
        language = NER_dict['language']
        
        if language == 'EN':
            print("BOT: It's", datetime.now().strftime("%H:%M"))

        elif language == 'ES':
            print ("BOT: Son las", datetime.now().strftime("%H:%M"))

        elif language == 'IT':
            print("BOT: Sono le", datetime.now().strftime("%H:%M"))


# In[3]:


t = TimeBot()


# In[4]:


# keywords, kw_lang, answer, cutoff=0.43, boost=0, all_lang=None, bigrams=None,  
#bigram_lang=None, bigram_cutoff = 1.8, bigram_boost = 1, b2=None, b2_lang=None, b2_cutoff=1.8, b2_boost=1, outputlangs=None

timebot = PolyBot(['time', 'hours', 'late'],
                   'EN',
                    t.answer_time,
                    cutoff = 0.65,
                    boost = 0.4)

