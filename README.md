# Multilingual-chatbot

There are two files: one is the chatbot implemented through the MUSE cross lingual embeddings for all the languages supported, the other one is a baseline approach that translates through Google translate the input language into English.

For both of them it's important to have Polyglot installed and a webdriver for Selenium. All the required packages are visible at the beginning of the file.

The embeddings can be found at https://github.com/facebookresearch/MUSE under the paagraph that says:
Multilingual word Embeddings
We release fastText Wikipedia supervised word embeddings for 30 languages, aligned in a single vector space.

The embeddings we need to donwload are Spanish, Italian, Estonian, Russian and English. 

On the Multilingual chatbot file, there is an commented part of code that manually sets the confidence for the word "weather" translated in other languages. By uncommenting it, the NLU for the WeatherBot will work better, however the purpose of the thesis is to have zero hard coding for the NLU part, this is why they are commented. You can uncomment it to see the difference or performance in Spanish, Italian, Russian.

To run both the baseline and the multilingual chatbot, just run cell after cell in the corrispetive files. 
If you want to shut the talk with the chatbot, just write "bye" no matter the language you are typing.

The chatbot only answers questions related to the bots included (weather, travel, wikipedia, time), if you will input basic chat sequences like 'hi' or 'thank you' it will retrieve you a message error or it will fire one of the bots implemented as stop-words mantain a high cosine similarity with the keywords.


