#!/usr/bin/env python
# coding: utf-8

# In[1]:


from polybot import*


# In[2]:


class TravelBot(Answers):
    
    def __init__(self):
        self.m = MakeBot()
    
    def answer_travel(self, CITY, CITY2, leaving, arriving, today, tomorrow, lang,
                  destination_phrase, from_city_phrase, sorry_phrase, when_phrase, oggi, domani):

        CITY = self.check_bigram_city(CITY)
        CITY2 = self.check_bigram_city(CITY2)

        if CITY2 !=None:
            if leaving == arriving:
                print(destination_phrase)
                tok = input('YOU: ').lower().capitalize().split()
                try:
                    if tok[1] != None:
                        tok = tok[0].capitalize() + " " + tok[1].capitalize()  
                except:
                    tok = tok[0].capitalize()  
                if tok[:3] == CITY[:3]:
                    arriving = CITY
                    leaving = CITY2
                else:
                    arriving = CITY2
                    leaving = CITY

            if leaving != None:
                leaving = leaving
            else:
                where2start = self.prep_city(from_city_phrase, 'from', lang)
                # we just confront the first 3 letters of the 2 cities (in case of languages wt different suffixies)
                if where2start[:3] == CITY2[:3]:
                    arriving = CITY
                    leaving = CITY2
                elif where2start[:3] == CITY[:3]:
                    arriving = CITY2
                    leaving = CITY
                else:
                    print(sorry_phrase)
                    today = True

            if leaving != None and arriving == None:
                if leaving == CITY:
                    arriving = CITY2
                elif leaving ==CITY2:
                    arriving = CITY
                else:
                    print(destination_phrase)
                    arriving = input('YOU: ').lower().capitalize().split()
                    try:
                        if arriving[1] != None:
                            arriving = arriving[0].capitalize() + " " + arriving[1].capitalize()  
                    except:
                        arriving = arriving[0].capitalize() 

            if arriving != None and leaving == None:
                if arriving == CITY:
                    leaving = CITY2
                elif arriving == CITY:
                    leaving = CITY
                else:
                    leaving = self.prep_city(from_city_phrase, 'from', lang)

        if CITY != None and CITY2 == None:     
            if arriving != None:
                arriving = CITY
                leaving = self.prep_city(from_city_phrase, 'from', lang)
            elif leaving != None:
                leaving = CITY
                print(destination_phrase)
                arriving = input('YOU: ').lower().capitalize().split()
                try:
                    if arriving[1] != None:
                        arriving = arriving[0].capitalize() + " " + arriving[1].capitalize()  
                except:
                    arriving = arriving[0].capitalize()
            else:
                where2start = self.prep_city(from_city_phrase, 'from', lang)
                # we just confront the first 3 letters of the 2 cities (in case of languages wt different suffixies)
                if where2start[:3] == CITY[:3]:
                    leaving = CITY
                    arriving = input('YOU: ').lower().capitalize().split()
                    try:
                        if arriving[1] != None:
                            arriving = arriving[0].capitalize() + " " + arriving[1].capitalize()  
                    except:
                        arriving = arriving[0].capitalize()

                else:
                    arriving = CITY
                    leaving = where2start

        if CITY == None:
            leaving =self.prep_city(from_city_phrase, 'from', lang)
            print(destination_phrase)
            arriving = input('YOU: ').lower().capitalize().split()
            try:
                if arriving[1] != None:
                    arriving = arriving[0].capitalize() + " " + arriving[1].capitalize()  
            except:
                arriving = arriving[0].capitalize()

        if today == False and tomorrow == False:
            print(when_phrase)
            day = input('YOU: ').lower()
            for i in range(len(day)):
                vect_dict = self.m.token2multi_vectors(day[i])
                today,tomorrow= self.find_TodayTomorrow(vect_dict)
            if today == True:
                day = oggi
            elif tomorrow == True:
                day = domani

        else:
            if today == True:
                day = oggi
            elif tomorrow == True:
                day = domani

        if lang != 'en':
            if lang == 'ru':
                print("BOT: Я нахожу лучший путь от {} до {} {}".format(leaving, arriving, day))
            else:
                print("BOT:", translator.translate("I am Finding the best way to go from {} to {} {}".format(leaving, arriving, day), dest=lang).text)

        else:
            print("BOT: Finding the best way to go from {} to {} {}".format(leaving, arriving, day))

    
    def Answer_Travel(self, NER_dict):
        
        CITY = NER_dict['CITY']
        CITY2 = NER_dict['CITY2']
        leaving = NER_dict['leaving']
        arriving = NER_dict['arriving']
        today = NER_dict['today']
        tomorrow = NER_dict['tomorrow']
        language_travel = NER_dict['language']
        
        if language_travel == 'EN':
            self.answer_travel(CITY, CITY2, leaving, arriving, today, tomorrow, 'en', "BOT: Which is your destination?", 
            "From which city would you like to leave?", "BOT: I am sorry, the city you inserted doesn't coincide with the one you told me earlier",
            "BOT: When?", "today", "tomorrow")
        elif language_travel == 'ES':
            self.answer_travel(CITY, CITY2, leaving, arriving, today, tomorrow, 'es', "BOT: ¿Cuál es tu destino?",
            "¿De qué ciudad te gustaría irte?", "BOT: Lo siento, la ciudad insertada no coincide con la que me dijiste antes",
             "BOT: Cuando?", "hoy", "mañana")
        elif language_travel == 'IT':
            self.answer_travel(CITY, CITY2, leaving, arriving, today, tomorrow, 'it', "BOT: Qual è la tua destinazione?", 
             "Da quale città ti piacerebbe partire?", "BOT: Mi dispiace, la città che hai digitato non corrisponde a quella inserita in precedenza",
            "BOT: Quando?", "oggi", "domani")


# In[3]:


tbot = TravelBot()


# In[4]:


travelbot = PolyBot(['travel', 'trip', 'ride', 'fly', 'go', 'drive', 'bus', 'plane', 'taxi', 'ferry', 'car', 'train', 'cruise'],
                    'EN',
                    tbot.Answer_Travel,
                     boost = 2,
                     travel=True)

