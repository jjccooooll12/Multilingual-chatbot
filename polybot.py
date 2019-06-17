#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import packages
import operator
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import polyglot
from polyglot.downloader import downloader
from polyglot.text import Text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from googletrans import Translator
translator = Translator()


# In[13]:


class Vectors():
    def __init__(self, directory):
        self.directory = directory
    
    def make_vectors(self, directory):
        table = dict()
        with open(directory, 'r', encoding='utf-8', errors='ignore') as f:
            next(f)
            vectors = []
            for i, line in enumerate(f):
                word,vect = line.rstrip().split(" ",1)
                vect = np.fromstring(vect, sep=' ')
                table[word] = vect
        return table
    
    def paths (self):
        dict_tables = {}
        for v in self.directory:
            if v == 'wiki.multi.en.vec.txt':
                dict_tables['EN'] = self.make_vectors(v)
            elif v == 'wiki.multi.es.vec.txt':
                dict_tables['ES'] = self.make_vectors(v)
            elif v == 'wiki.multi.it.vec.txt':
                dict_tables['IT'] = self.make_vectors(v)
            elif v == 'wiki.multi.et.vec.txt':
                dict_tables['ET'] = self.make_vectors(v)
            elif v == 'wiki.multi.ru.vec.txt':
                dict_tables['RU'] = self.make_vectors(v)
            elif v == 'wiki.multi.de.vec.txt':
                dict_tables['DE'] = self.make_vectors(v)

        return dict_tables


# In[14]:


#  This can take a long time (5 minutes more or less) we upload and create the vectors
CLWEs = Vectors(['wiki.multi.en.vec.txt', 'wiki.multi.it.vec.txt', 'wiki.multi.es.vec.txt' ])
all_vectors = CLWEs.paths()


# In[15]:


def cos_sim (lang1, w1, lang2, w2):
    cos_sim = cosine_similarity(all_vectors[lang1][w1].reshape(1,300), all_vectors[lang2][w2].reshape(1,300))
    return cos_sim


# In[16]:


class Keywords():
    def __init__(self, keywords):
        self.keywords = keywords
        self.OOV = []
        
        
    def make_keywords(self, table_lang):
        
        key_dict = dict()
        try:
            for k in self.keywords:
                key_dict[k] = table_lang[k]
        except: 
            self.OOV.append(k)
        return key_dict
    
    def make_empty_dictionaries(self):
        similarities_lang = dict()
        for k in self.keywords:
            similarities_lang[k] = np.asarray([[0]])
        for oov in self.OOV:
            similarities_lang[oov] = np.asarray([[0]])
        return similarities_lang
    
    def empty_dictionaries(self, dict_table):
        similarities_per_language = dict()
        for k,v in dict_table.items():
            similarities_per_language[k] = (self.make_empty_dictionaries())
        return similarities_per_language


# In[24]:


class MakeBot():
   
    # Function that captures the highest similarity within the token and the keywords for a language
    def highest_similarity_for_keyword(self, empty_dictionaries, dict_multi_vectors, key, value):
        last_status = empty_dictionaries[key]
        similarity = cosine_similarity(dict_multi_vectors.reshape(1,300), value)
        if similarity > last_status:
            empty_dictionaries[key] = similarity
            
    # Function that compares the similarities between all languages and returns the highest one overall
    def highest_sim_over_language(self, empty_dictionaries, dict_multi_vectors, key, value, multibot_dict):
        
        try:
            self.highest_similarity_for_keyword(empty_dictionaries['EN'], dict_multi_vectors['EN'], key, value)
        except:
            pass
        
        try:
            #Sp
            self.highest_similarity_for_keyword(empty_dictionaries['ES'], dict_multi_vectors['ES'], key, value)
        except:
            pass

        try:
            #It
            self.highest_similarity_for_keyword(empty_dictionaries['IT'], dict_multi_vectors['IT'], key, value)
        except:
            pass

        try:
            #Rus
            self.highest_similarity_for_keyword(empty_dictionaries['RU'], dict_multi_vectors['RU'], key, value)
        except:
            pass

        try:
            #Est
            self.highest_similarity_for_keyword(empty_dictionaries['ET'], dict_multi_vectors['ET'], key, value)
        except:
            pass
        
        try:
            #Est
            self.highest_similarity_for_keyword(empty_dictionaries['DE'], dict_multi_vectors['DE'], key, value)
        except:
            pass

        # sort the keys by the highest cosine values of all languages
        sorted_results = dict()
        for k,v in empty_dictionaries.items():
            sorted_results[k] = sorted(v.items(), key=operator.itemgetter(1), reverse=True)
            list_key_value = [[k,v] for k, v in sorted_results.items()]
            
        for items in list_key_value:
            lang = items[0]
            pairs = items[1]
            multibot_dict[pairs[0][0], lang] = pairs[0][1]

        sorted_simil = sorted(multibot_dict.items(), key=operator.itemgetter(1), reverse=True)
        
        return sorted_simil
    

  
    def compute_highest_token(self, bot_dictionary, empty_dictionaries, cutoff,  dict_multi_vectors,
                              highest_token_dict, multibot_dict):
       
        #bot dictionary is the dictionary of the CLWEs for the keywords selected
        for key, value in bot_dictionary.items():
            value = value.reshape(1,300)
            # we keep in the dict the value that had the highest cosine similarity between key and CLWE
            sorted_simil = self.highest_sim_over_language(empty_dictionaries, dict_multi_vectors, key, value, multibot_dict)
        
        language = sorted_simil[0][0][1]
        # get the highest key-value pair
        if sorted_simil[0][1][0][0] > cutoff:
            highest_token_dict[sorted_simil[0][0][0]] = sorted_simil[0][1][0][0] 
        return language
    
    
    def compute_confidence(self, language, bot_dictionary,  dict_multi_vectors, multibot_dict, confidence, cutoff, boost):
        # sort the keys by the highest cosine values of all languages
        for key, value in bot_dictionary.items():
            value = value.reshape(1,300)
            similarity = cosine_similarity(dict_multi_vectors[language].reshape(1,300), value)
            if similarity[0][0] > cutoff:
                confidence.append(similarity[0][0] + boost)
                
    def token2multi_vectors(self, token):
        UNK = np.zeros((1, 300))
        dict_vect = dict()
        for k,v in all_vectors.items():
            try:
                dict_vect[k] = v[token].reshape(1,300)
            except:
                dict_vect[k] = UNK
        return dict_vect  


# In[18]:


class PolyBot():
    def __init__(self, keywords, kw_lang, answer, cutoff=0.43, boost=0, all_lang=None, bigrams=None, bigram_lang=None,
    bigram_cutoff = 1.8, bigram_boost = 1, b2=None, b2_lang=None, b2_cutoff=1.8, b2_boost=1, outputlangs=None, travel=False):
    
        self.keywords = keywords
        self.dict_CLWEs = all_vectors
        self.kw_lang = kw_lang
        self.answer = answer
        self.bigrams = bigrams
        self.bigram_lang = bigram_lang
        self.cutoff = cutoff
        self.boost = boost
        self.all_lang = all_lang
        self.bigram_cutoff = bigram_cutoff
        self.bigram_boost = bigram_boost
        self.b2 = b2
        self.b2_lang = b2_lang
        self.b2_cutoff = b2_cutoff
        self.b2_boost = b2_boost
        self.k = Keywords(self.keywords)
        self.m = MakeBot()
        self.outputlangs = outputlangs
        self.travel = travel
        
        if self.bigram_lang == None:
            self.bigram_lang = self.kw_lang
        if self.b2_lang == None:
            self.b2_lang == self.kw_lang
        if self.outputlangs == None:
            self.outputlangs = self.dict_CLWEs
        else:
            output_languages = dict()
            for i in range(len(self.outputlangs)):
                output_languages[self.outputlangs[i]] = self.dict_CLWEs[self.outputlangs[i]] 
            self.dict_CLWEs = output_languages

        
    def prepare_bot(self):
        empty_dictionaries = self.k.empty_dictionaries(self.dict_CLWEs)
        confidence = []
        multibot_dict = dict()
        highest_token = dict()
        return  empty_dictionaries, confidence, multibot_dict, highest_token
        
    def language_identifier (self, empty_dictionaries, dict_multi_vectors, highest_token_dict, multibot_dict):
        bot_dictionary= self.k.make_keywords(self.dict_CLWEs[self.kw_lang]) 
        
        language = self.m.compute_highest_token(bot_dictionary, empty_dictionaries, self.cutoff,
                                     dict_multi_vectors, highest_token_dict, multibot_dict)
        
        return language
    
    
    def get_confidence(self, dict_multivector, confidence, multibot_dict, language):
        bot_dictionary = self.k.make_keywords(self.dict_CLWEs[self.kw_lang])
        self.m.compute_confidence(language, bot_dictionary, dict_multivector, multibot_dict, confidence, self.cutoff,
                                  self.boost)
    
    def else_language(self, dict_multi_vectors, dict_next_multivector, bi_lang):
        source_lang = []
        else_lang = []
        next_source_lang = []
        next_else_lang = []
        
        for k, v in dict_multi_vectors.items():
            if k == bi_lang:
                source_lang.append([v, k])
            else:
                else_lang.append([v, k])
    
        for k, v in dict_next_multivector.items():
            if k ==  bi_lang:
                next_source_lang.append([v, k])
            else:
                next_else_lang.append([v, k])
        return source_lang, else_lang, next_source_lang, next_else_lang
    
    def score_bigrams(self, w1,w2, source_lang, else_lang, next_source_lang, next_else_lang, confidence, bi_lang, bi_cutoff, bi_boost):
        flag = False
        languages = []
        scores = []
        for i in range(len(source_lang)):
            if cosine_similarity(self.dict_CLWEs[bi_lang][str(w1)].reshape(1,300), source_lang[i][0]) + cosine_similarity(self.dict_CLWEs[bi_lang][str(w2)].reshape(1,300), next_source_lang[i][0]) > 1.6:
                confidence.append(bi_boost)
                lang = source_lang[i][1]
                score = cosine_similarity(self.dict_CLWEs[bi_lang][str(w1)].reshape(1,300), source_lang[i][0]) + cosine_similarity(self.dict_CLWEs[bi_lang][str(w2)].reshape(1,300), next_source_lang[i][0]) 
                scores.append(score)
                languages.append(lang)
                flag = True
        
       
        for ii in range(len(else_lang)):
            if cosine_similarity(self.dict_CLWEs[bi_lang][str(w1)].reshape(1,300), else_lang[ii][0]) + cosine_similarity(self.dict_CLWEs[self.bigram_lang][str(w2)].reshape(1,300), next_else_lang[ii][0]) > bi_cutoff:
                confidence.append(bi_boost)
                lang = else_lang[ii][1]
                languages.append(lang)
                score = cosine_similarity(self.dict_CLWEs[bi_lang][str(w1)].reshape(1,300), else_lang[ii][0]) + cosine_similarity(self.dict_CLWEs[self.bigram_lang][str(w2)].reshape(1,300), next_else_lang[ii][0])
                scores.append(score)
                flag = True
        
        if flag == True:
            return True, languages, scores
        else:
            return None, None, None
            
        
    def compute_bigrams(self, w1, w2, dict_multivector, dict_next_multivector, confidence, bi_lang, bi_cutoff, bi_boost):
        source_lang, else_lang, next_source_lang, next_else_lang = self.else_language(dict_multivector, dict_next_multivector, bi_lang)
        w, langs, scores = self.score_bigrams(w1,w2, source_lang, else_lang, next_source_lang, next_else_lang, confidence, bi_lang, bi_cutoff, bi_boost)
        return w, langs, scores
    
    


# In[19]:


class Answers():
    
    def check_bigram_city(self, CITY):
        if CITY != None:
            CITY = CITY.split()
            try:
                if CITY[1] != None:
                    CITY = CITY[0].capitalize() + " " + CITY[1].capitalize()
            except:
                CITY = "".join(CITY).capitalize()
                
        return CITY
    
    
     # Function to wikify the entity
    def selenium (self, url):
        chrome_options = Options() 
        chrome_options.add_argument("--headless") 
        driver = webdriver.Chrome(executable_path=r'/home/jcool12/Desktop/chatbot/chromedriver', options=chrome_options)
        driver.get(url)
        driver.find_element_by_link_text('English').click()
        name= driver.title
        LANGS = [
        'ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž',   # Czech
        'ÄäÖöÜüẞß',                         # German
        'ĄąĆćĘęŁłŃńÓóŚśŹźŻż',               # Polish
        'áéóíñü',                           # Spanish
        'àèòìù'                             #Italian
        ]
        pattern = r'[A-Z][a-z{langs}]+'.format(langs=''.join(LANGS))
        pattern = re.compile(pattern)
        match = pattern.findall(name)
        match = match[0:-1]
        try:
            if match [1] != None:
                return match[0] + " " + match[1]
        except:
            return match[0]
    
    
    def prep_city(self, from_phrase, parola, lang):
        self.table_lang = all_vectors['EN']
        prep = 0
        print('BOT:', from_phrase) 
        city = input('YOU: ')
        tok = city.lower().split()
        for i in range(len(tok)):
            vect_dict = self.m.token2multi_vectors(tok[i])
            for k,v in vect_dict.items():
                if lang == 'en':
                    if cosine_similarity(v, self.table_lang[parola].reshape(1,300)) > 0.8:
                        prep += 1
                else:
                    if cosine_similarity(v, self.table_lang[parola].reshape(1,300)) > 0.3:
                        prep += 1       
        if prep > 0: 
            try:
                if tok[2] != None:
                    CITY = tok[1].capitalize() + " " + tok[2].capitalize()      
            except:
                try:
                    CITY = tok[1].capitalize()
                except:
                    CITY = city.capitalize()
        else:
            CITY = city.capitalize()
            
        if lang != 'en':
            try:
                website = 'https://{}.wikipedia.org/wiki/{}'.format(lang, CITY)
                CITY = self.selenium(website)
            except:
                CITY = translator.translate(CITY, dest=lang).text
       
        return CITY 
    
    
    
    def when_def(self,when_dict, conf_value, vect_dict):
        sim_today = []
        for key, value in when_dict.items():
            value = value.reshape(1,300)
            for k,v in vect_dict.items():
                sim = cosine_similarity(v, value)
                if sim > conf_value:
                    sim_today.append(sim)
        return sum(sim_today)
    
    def find_TodayTomorrow(self, vect_dict):
        today = False
        today_key = {'today':all_vectors['EN']['today'], 'now':all_vectors['EN']['now']}
        oggi = self.when_def(today_key, 0.5, vect_dict)
        tomorrow = False
        tomorrow_key = {'tomorrow':all_vectors['EN']['tomorrow']}
        domani = self.when_def(tomorrow_key, 0.45, vect_dict)
        if oggi > 0 and oggi > domani:
            today = True
        if domani > 0 and domani > oggi:
            tomorrow = True
        return today, tomorrow


# In[29]:


class Conversation(PolyBot):
    
    def __init__(self, bots, baseline=False):
        self.m = MakeBot()
        self.bots = bots
        self.a = Answers()
        self.baseline = baseline

    
    def NER(self, human):
        PER = []
        LOC = []
        ORG = []
        try:
            text = Text(human)
            for sent in text.sentences:
                for e in sent.entities:
                    if e.tag == 'I-LOC':
                        LOC.append(e)
                    elif e.tag == 'I-PER':
                        PER.append(e)
                    elif e.tag == 'I-ORG':
                        ORG.append(e)            
        except:
            pass
        
        return PER, LOC, ORG
    
    def find_city(self, LOC):
        # Capture if a city is given in the input
         #Entities (cities, time, people)
        
        CITY = None
        try: 
            if LOC[0][0] != None:
                CITY = LOC[0][0]
            if LOC[0][1] != None:
                CITY = LOC[0][0] + " "+ LOC[0][1]
        except:
            pass
        if CITY != None:
            CITY = CITY.capitalize()

        CITY2 = None
        try: 
            if LOC[1][0] != None:
                CITY2 = LOC[1][0]
            if LOC[1][1] != None:
                CITY2 = LOC[1][0] + " "+ LOC[1][1]
        except:
            pass
        if CITY2 != None:
            CITY2 = CITY2.capitalize()
            
        return CITY,CITY2

    def find_people(self, PER):
        PERSON = None
        try: 
            if PER[0][0] != None:
                PERSON = PER[0][0]
            if PER[0][1] != None:
                PERSON = PER[0][0] + " "+ PER[0][1]
        except:
            pass
        if PERSON != None:
            return PERSON
    
    
    
    def travel_bigram (self, PREP, which_city, conf, dict_multi_vectors, dict_next_multivector, next_token, lang):
        
        if which_city != None:
            if lang == 'EN':
                for i in range(len(dict_multi_vectors['EN'])):
                    if cosine_similarity(all_vectors['EN'][str(PREP)].reshape(1,300), dict_multi_vectors['EN'][i].reshape(1,300)) > 0.8 and next_token.capitalize() == which_city:
                        c = which_city
                        return c
            else:
                
                for i in range(len(dict_multi_vectors[lang])):
                    if cosine_similarity(all_vectors['EN'][str(PREP)].reshape(1,300), dict_multi_vectors[lang][i].reshape(1,300)) > conf and next_token.capitalize() == which_city:
                        c = which_city
                        return c
                
    
    def travel_score(self, leaving, arriving, CITY, CITY2, dict_multi_vectors,dict_next_multivector, next_token, lang):
        if CITY2 != None:
            partenza = self.travel_bigram('from', CITY, 0.35, dict_multi_vectors, dict_next_multivector, next_token, lang)
            if partenza != None:
                leaving = partenza
  
            arrivo = self.travel_bigram('to', CITY2, 0.45, dict_multi_vectors, dict_next_multivector, next_token, lang)
            if arrivo != None:
                arriving = arrivo
                
            if arriving == None:
                arrivo2= self.travel_bigram('to', CITY, 0.45, dict_multi_vectors, dict_next_multivector, next_token, lang) 
                if arrivo2 !=None:
                    arriving = arrivo2
                    leaving = CITY2
            
            if leaving == None: 
                partenza2 = self.travel_bigram('from', CITY2, 0.35, dict_multi_vectors, dict_next_multivector, next_token, lang)
                if partenza2 != None:
                    leaving = partenza2
            
            if arriving != None and leaving == None:
                if CITY == arriving:
                    leaving = CITY2
                else:
                    leaving = CITY
     
        if CITY != None and CITY2 == None:
            partenza = self.travel_bigram('from', CITY, 0.35, dict_multi_vectors, dict_next_multivector, next_token, lang)
            if partenza != None:
                leaving = partenza

            arrivo = self.travel_bigram('to', CITY, 0.45, dict_multi_vectors, dict_next_multivector, next_token, lang)
            if arrivo != None:
                arriving = arrivo
            
            if arriving == leaving:
                leaving = None
                
        return leaving, arriving
        
       
    def talk(self):
        
        NER_dict = dict()
        while True:
            lang = None
            human = input('YOU: ')
            if human == 'bye':
                break
            
            if self.baseline == True:
                    # Language Detector
                    identif = translator.detect(human)
                    lang = identif.lang.upper()
                    if lang == 'ESPT':
                        lang = 'ES'
                    print(lang, 'IDENTIFIED LANGUAGE')
                    human = translator.translate(human, dest='en')
                    print(human.text, 'TRANSLATED INPUT')
                    human = human.text
            
            PER,LOC, ORG = self.NER(human)
            leaving = None
            arriving = None
            
            PERSON = self.find_people(PER)
            CITY, CITY2 = self.find_city(LOC)
            
            human = human.split()
            h = [re.sub(r'[^\w]', '', tok) for tok in human]
            hum = []

            for tok in human:
                hum.append(re.sub(r'[^\w]', '', tok))
            hum.append('EOS')
            
            NER_dict['people'] = PER
            NER_dict['cities'] = LOC
            NER_dict['organizations'] = ORG
            NER_dict['leaving'] = leaving
            NER_dict['arriving'] = arriving
            NER_dict['CITY'] = CITY
            NER_dict['CITY2'] = CITY2
            NER_dict['PERSON'] = PERSON
            NER_dict['input'] = h
            
            return hum, NER_dict, lang
        
        
    def talk2me (self):
        
        while True:
       
 #### CREATE DICTIONARIES ################################################################################################
            bots_dict = dict()
            for i, bot in enumerate(self.bots):
                empty_dictionaries, confidence, multi, highest_token = bot.prepare_bot()
                bots_dict['confidence'+str(i)] = confidence
                bots_dict['empty_dictionaries'+str(i)] = empty_dictionaries
                bots_dict['multi_dict'+str(i)] = multi
                bots_dict['highest_token'+str(i)] = highest_token
                bots_dict['answer'+str(i)] = bot.answer
                
        ### START CONVERSATION #######################################################################################################
            try:
                #NER
                hum, NER_dict, lang= self.talk()

            except:
                print('BOT: Have a nice day')
                break


            for i in range (len(hum)-1):
                # normalize the input
                token = hum[i].lower()
                next_token = hum[i+1].lower()
                
                # Assign the multilingual vectors to the input words
                vect_dict = self.m.token2multi_vectors(token)
                next_vect_dict= self.m.token2multi_vectors(next_token)
                today,tomorrow= self.a.find_TodayTomorrow(vect_dict)
                NER_dict['today'] =  today
                NER_dict['tomorrow'] =  tomorrow

                for i,bot in enumerate(self.bots):
                    empty_dictionaries = bots_dict['empty_dictionaries'+str(i)]
                    confidence =  bots_dict['confidence'+str(i)]
                    highest_token =  bots_dict['highest_token'+str(i)]
                    multi_dict = bots_dict['multi_dict'+str(i)]
                    language_bot = bot.language_identifier(empty_dictionaries, vect_dict, highest_token, multi_dict)
                    bots_dict['language_bot'+str(i)] = language_bot
                    if self.baseline == True:
                        bots_dict['language_bot'+str(i)] = lang
     
                    if bot.bigrams != None:
                        for ii in range(len(bot.bigrams)):
                            #  w1, w2, dict_multivector, dict_next_multivector, confidence
                            w1 = bot.bigrams[ii][0]
                            w2 = bot.bigrams[ii][1]
                            is_true, langs, scores= bot.compute_bigrams(w1,w2, vect_dict, next_vect_dict, confidence, 
                                                bot.bigram_lang, bot.bigram_cutoff, bot.bigram_boost)
                            
                            if is_true == True:
                                bots_dict[w1 + '_' + w2] = is_true
                                for iii in range(len(langs)):
                                    try:
                                        if scores[iii] >  bots_dict['bigram_score'+str(i)]:
                                            bots_dict['language_bigram'+str(i)] = langs[iii]
                                    except:
                                        bots_dict['bigram_score'+str(i)] = scores[iii]
                                        bots_dict['language_bigram'+str(i)] = langs[iii]
                                
                            
                    if bot.b2 != None:
                        for ii in range(len(bot.b2)):
                            w1 = bot.b2[ii][0]
                            w2 = bot.b2[ii][1]
                            is_true, langs, scores = bot.compute_bigrams(w1,w2, vect_dict, next_vect_dict, confidence,
                                                    bot.b2_lang, bot.b2_cutoff, bot.b2_boost)
                            
                            
                            if is_true == True:
                                bots_dict[w1 + '_' + w2] = is_true
                                for iii in range(len(langs)):
                                    try:
                                        if scores[iii] >  bots_dict['bigram_score'+str(i)]:
                                            bots_dict['language_bigram'+str(i)] = langs[iii]
                                    except:
                                        bots_dict['bigram_score'+str(i)] = scores[iii]
                                        bots_dict['language_bigram'+str(i)] = langs[iii]
                                        
                      
                    bot.get_confidence(vect_dict, confidence, multi_dict, bots_dict['language_bot'+str(i)])   

            all_confs = dict()
            for i, bot in enumerate(self.bots):
                confidence =  bots_dict['confidence'+str(i)]
                summed_conf = sum(confidence)
                all_confs['confidence'+str(i)] = summed_conf
                

            sorted_confs = sorted(all_confs.items(), key=operator.itemgetter(1), reverse=True)

            
            try:
                if sorted_confs[0][1] == sorted_confs[1][1]:
                    to_increase = sorted_confs[0][0]
                    for i, bot in enumerate(self.bots):
                        if 'confidence'+str(i) == to_increase:
                            bots_dict['confidence'+str(i)] = [bots_dict['confidence'+str(i)][0]+0.1]
            except:
                pass
                        
            OFF =[]
            for i, bot in enumerate(self.bots):
                confidence =  bots_dict['confidence'+str(i)]
                summed_conf = sum(confidence)
                answer = bots_dict['answer'+str(i)]
                self.travel = bot.travel
                
                if summed_conf + 0.1 == sorted_confs[0][1]+0.1 and summed_conf>0:
                    NER_dict['highest_token'] =  bots_dict['highest_token'+str(i)]
                    NER_dict['language'] = bots_dict['language_bot'+str(i)]
                    if self.baseline == False:
                        try:
                            NER_dict['language'] = bots_dict['language_bigram'+str(i)]
                        except:
                            pass
                    
                    NER_dict['highest_keywords'] = bots_dict['empty_dictionaries'+str(i)]
                    
                    if bot.bigrams != None:
                        for i in range(len(bot.bigrams)):
                            #  w1, w2, dict_multivector, dict_next_multivector, confidence
                            w1 = bot.bigrams[i][0]
                            w2 = bot.bigrams[i][1]
                            try:
                                NER_dict[w1 + '_' + w2] = bots_dict[w1 + '_' + w2] 
                            except:
                                NER_dict[w1 + '_' + w2] = None
                    
                    if bot.b2 != None:
                        for i in range(len(bot.b2)):
                            #  w1, w2, dict_multivector, dict_next_multivector, confidence
                            w1 = bot.b2[i][0]
                            w2 = bot.b2[i][1]
                            try:
                                NER_dict[w1 + '_' + w2] = bots_dict[w1 + '_' + w2]
                            except:
                                NER_dict[w1 + '_' + w2] = None
                        
                    
                    if self.travel == True:
                        for ii in range (len(hum)-1):
                            # normalize the input
                            token = hum[ii].lower()
                            next_token = hum[ii+1].lower()

                            # Assign the multilingual vectors to the input words
                            vect_dict = self.m.token2multi_vectors(token)
                            next_vect_dict= self.m.token2multi_vectors(next_token)
                            language_bot = NER_dict['language']
                            leaving =  NER_dict['leaving']
                            arriving = NER_dict['arriving']
                            CITY = NER_dict['CITY']
                            CITY2 = NER_dict['CITY2']
                            self.kw_lang = bot.kw_lang

                            leaving, arriving = self.travel_score(leaving, arriving, CITY, CITY2, 
                                            vect_dict, next_vect_dict, next_token, language_bot)

                            if leaving != None:
                                bots_dict['leaving'+str(i)] = leaving

                            if arriving != None:
                                bots_dict['arriving'+str(i)] = arriving 

                        try:   
                            NER_dict['leaving'] = bots_dict['leaving'+str(i)]
                        except:
                            pass

                        try:
                            NER_dict['arriving'] = bots_dict['arriving'+str(i)]
                        except:
                            pass
        
                    answer(NER_dict)
                    OFF.append('The end')
            try:  
                if OFF[0] == 'The end':
                    pass
            except:
                print("BOT: Sorry, I didn't understand, could you repeat in other words?")
                

