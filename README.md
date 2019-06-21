# Multilingual-chatbot

Cross-lingual chatbot creation platform. The input requests are matched to keywords using MUSE (https://github.com/facebookresearch/MUSE), so the input can be given in any language and the patterns/keywords can also be written in any language for which there are MUSE cross-lingual embeddings available.

## Features:
* multiple "bots" (topics) supported via estimated confidence
* unigram and bigram keywords
* keyword weighting
* "grabbing initiative" in each bot/module

## Dependencies:
* polyglot (for multilingual NER)
* googletrans (for translating the response)
* sklearn, numpy, icu, pycld2, morfessor, selenium (required by polyglot)


## Usage demo:
    import polybot
    from TimeBot import timebot
    from WikiBot import wikibot
    
    bots = [timebot, wikibot]                # insert the bots in the list 
    
    c = polybot.Conversation(bots)           # call the Conversation object
    c.talk2me()                              # talk with the bots!



## Adding a new bot:
    import polybot
    from datetime import datetime
    
    # define the answer of the bot. The answer requires a NER dictionary as an argument
    def answer_time(NER_dict):
    
        language = NER_dict['language']            # 'language' refers to the input language identified by the bot
        
        responses = { "EN": "It's {0}", "ES": "Son las {0}", "IT": "Sono le {0}", "DE": "Es ist {0}" }
        
        if language in responses:
            print("BOT: " + responses[language].format(datetime.now().strftime("%H:%M")))        
    
    # call the Polybot object                    REQUIRED ARGUMENTS
    timebot = PolyBot(['time', 'hours', 'late'], # unigram keywords -> list of str
                   'EN',                         # keywords' language  -> str
                    answer_time,                 # answer of the bot  -> function
                                                 DEFAULT ARGUMENTS
                    cutoff = 0.65,               # threshold for the keyword matching -> int, default = 0.43
                    boost = 0,                   # boost (add additional weights to a bot confidence) -> int, default = 0
                    bigrams = [('wie', 'spät')], # bigrams keywords -> list of str, default = None
                    bigram_lang = 'DE',          # bigrams keywords' language -> str, default = keywords' language
                    bigram_cutoff = 1.8,         # bigrams threshold -> int, default = 1.8
                    bigram_boost = 1,            # bigrams boost -> int, default = 1
                    b2 = [('che', 'ore')],       # additional bigrams keywords (for a 2nd languge) -> list of str
                    b2_lang  = 'IT',             # additional bigrams keywords' language -> str, default = keywords' language
                    b2_cutoff = 0.8,             # additinoal bigrams threshold -> int, default = 1.8   
                    b2_boost=1,                  # additional bigrams boost -> int, default = 1
                    outputlangs= 
                    ['EN','ES','IT','DE'],       #languages in which we expect a response -> list of str, default = all languages
                    travel = False)          # captures if the user wants to travel from a place to another one -> bool, default = False  
                    


