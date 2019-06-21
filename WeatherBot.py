#!/usr/bin/env python
# coding: utf-8

# In[2]:


from polybot import *
import requests
from bs4 import BeautifulSoup


# In[6]:


class WeatherBot(Answers):
    
    def __init__(self):
        self.m = MakeBot()
    
    def weatherAPI(self, CITY, sorry_answer, DAY, lang, true_day):
        BOT = 'BOT:'
        try:
            url = "https://openweathermap.org/data/2.5/weather?q={}&appid=b6907d289e10d714a6e88b30761fae22".format(CITY)
            res = requests.get(url)
            data = res.json()
            temp = data['main']['temp']
            sky = data['weather'][0]['description']
            if lang != 'en':
                if true_day == True:
                    print(BOT, translator.translate("There is {} and there are {} degrees in {} {}".format(sky,
                    temp,  CITY, DAY), dest=lang).text)
                else:
                    print(BOT, translator.translate("In this day there is {} and there are {} degrees in {}".format(sky, temp, 
                        CITY), dest=lang).text)

            else:
                if true_day == True:
                    print(BOT, "There is {} and there are {} degrees in {} {}".format(sky, temp,CITY, DAY))
                else:
                    print(BOT, "In this day there is {} and there are {} degrees in {}".format(sky, temp,  CITY))

        except:
            print(BOT,sorry_answer, CITY, DAY)
            

    def answer_weather(self, today, tomorrow, phrase_locality, phrase_when,  TODAY, TOMORROW, CITY, sorry_answer, lang):
        BOT = 'BOT:'
        if CITY == None:
            CITY = self.prep_city(phrase_locality, 'in', lang)      
        else:
            CITY = self.check_bigram_city(CITY)


        if today == False and tomorrow == False:
            print(BOT, phrase_when)
            when = input('YOU: ').lower().split()
            for i in range(len(when)):
                vect_dict = self.m.token2multi_vectors(when[i])
                today,tomorrow= self.find_TodayTomorrow(vect_dict)

            if today == True:
                today = TODAY
                self.weatherAPI(CITY, sorry_answer, today, lang, true_day=True)

            elif tomorrow == True:
                tomorrow = TOMORROW
                self.weatherAPI(CITY, sorry_answer, tomorrow, lang, true_day=True)

            else:
                self.weatherAPI(CITY, sorry_answer, tomorrow, lang, true_day=False)

        elif today == True and tomorrow == False:
            today = TODAY
            self.weatherAPI(CITY, sorry_answer, today, lang, true_day=True)

        elif tomorrow == True:
            tomorrow = TOMORROW
            self.weatherAPI(CITY, sorry_answer, tomorrow, lang, true_day=True)



    def Answer_Weather(self,  NER_dict):

        language_weather = NER_dict['language']
        today = NER_dict['today']
        tomorrow = NER_dict['tomorrow']
        CITY = NER_dict['CITY']
        
        
        if language_weather == 'EN':

            #phrase_locality, phrase_when, asnwer_1, answer_2, TODAY, TOMORROW, sorry_answer
            temp= self.answer_weather(today, tomorrow, "In which location?", "When?", "today", "tomorrow",CITY,
                           "I am sorry, we don't have information about this location", 'en')

        elif language_weather == 'ES':
            try:
                CITY = "_".join(CITY.split())
                website = 'https://es.wikipedia.org/wiki/'+CITY
                CITY = self.selenium (website)
                self.answer_weather(today,tomorrow, "En cual ciudad?", "Cuando?",  "hoy", "mañana", CITY,
                                      "Lo siento, no tenemos información sobre esta ciudad", 'es')
            except:
                if CITY != None:
                    CITY = translator.translate(CITY, dest='en').text
                    self.answer_weather(today,tomorrow,  "En cual ciudad?", "Cuando?",  "hoy", "mañana", CITY,
                                      "Lo siento, no tenemos información sobre esta ciudad", 'es')

                else:
                    self.answer_weather(today,tomorrow,  "En cual ciudad?", "Cuando?",  "hoy", "mañana", CITY,
                                      "Lo siento, no tenemos información sobre esta ciudad", 'es')

        elif language_weather == 'IT':
            try:
                CITY = "_".join(CITY.split())
                website = 'https://it.wikipedia.org/wiki/'+CITY
                CITY = self.selenium (website)
                self.answer_weather(today,tomorrow,"In quale citta'?", 'Quando?', "oggi", "domani", CITY,
                           "Mi dispiace, non disponiamo di informazioni riguardo a questa citta'", 'it')   
            except:
                if CITY != None:
                    CITY = translator.translate(CITY, dest='en').text
                    self.answer_weather(today,tomorrow, "In quale citta'?", 'Quando?', "oggi", "domani", CITY,
                           "Mi dispiace, non disponiamo di informazioni riguardo a questa citta'", "it")
                else:
                    self.answer_weather(today,tomorrow, "In quale citta'?", 'Quando?', "oggi", "domani", CITY,
                           "Mi dispiace, non disponiamo di informazioni riguardo a questa citta'", 'it')


# In[4]:


weatbot = WeatherBot()


# In[5]:


weatherbot = PolyBot(['rain', 'sun', 'snow', 'weather', 'sun', 'hailstorm', 'fog', 'temperature', 'degrees', 'cold', 'hot', 'warm', 'humidity'],
                 'EN',
                weatbot.Answer_Weather,
                 bigrams=[('che', 'tempo')],
                     boost =2,
                bigram_lang='IT',
                 bigram_cutoff = 1.3,
                bigram_boost = 2)

