#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# The above encoding declaration is required and the file must be saved as UTF-8

from textblob import TextBlob
from textblob.exceptions import NotTranslated
import sys, glob
import pandas as pd
import numpy as np
import time, datetime
import pickle
from joblib import Parallel, delayed
import multiprocessing


'''
The aim of this code is to process and clean the data so I can
later use it to plot the map, let's hope this works.
'''

#Data directory location
data_directory = "./CrisisLexT26"

#The disasters we want to compute
disasters = ["2012_Colorado_wildfires", "2012_Costa_Rica_earthquake", "2012_Guatemala_earthquake", "2012_Italy_earthquakes",
             "2012_Philipinnes_floods", "2012_Typhoon_Pablo", "2012_Venezuela_refinery", "2013_Alberta_floods", 
             "2013_Australia_bushfire", "2013_Bohol_earthquake", "2013_Boston_bombings", "2013_Brazil_nightclub_fire"
             "2013_Colorado_floods", "2013_Glasgow_helicopter_crash", "2013_LA_airport_shootings", "2013_Lac_Megantic_train_crash",
             "2013_Manila_floods", "2013_NY_train_crash", "2013_Queensland_floods", "2013_Russia_meteor", "2013_Sardinia_floods",
             "2013_Savar_building_collapse", "2013_Singapore_haze", "2013_Spain_train_crash", "2013_Typhoon_Yolanda",
             "2013_West_Texas_explosion"]


#Disasters that are in english and do not require translation
in_english = [True, False, False, False,
              False, False, False, True,
              True, False, True, False,
              True, True, True, True,
              False, True, True, False, False,
              False, False, False, False,
              True]

#The minimum length of the tweet after decoding to be processed
minimum_length = 5

def process_disaster(d_index, disaster):

    print "Processing", disaster, " it might take a while"
    
    #Read and merge the datasets
    ids_location = glob.glob(data_directory + '/' + disaster + '/*tweetids_entire_period.csv')[0]
    data_location = glob.glob(data_directory + '/' + disaster + '/*tweets_labeled.csv')[0]

    ids = pd.read_csv(ids_location)
    data = pd.read_csv(data_location)

    #Join both CSVs, it would be easier if the columnames actually matched
    df = pd.merge(ids, data, how='right', left_on=[' Tweet-ID'], right_on=['Tweet ID'])

    #Only keep the important columns
    df = df[['Timestamp', ' Tweet Text']].copy()

    #Create a new column for the POSIX time
    df["POSIX Timestamp"] = ''

    #Create a new column that will have the sentiment value for every
    #tweet
    df["Sentiment"] = 0.0

    #Do the processing
    for index, row in df.iterrows():

        print "Processing tweet", index, "of", df.shape[0]

        #Update the POSIX column with the actual data
        time_string = row["Timestamp"]

        #This magic string will transform the time on our tweets to POSIX
        #BUT in Python 2.7 apparently the %z directive is not yet implementer
        #so this time is unaware of locales, which makes it not exact when visualizing :(
        time_posix = time.mktime(datetime.datetime.strptime(time_string, "%a %b %d %H:%M:%S +0000 %Y").timetuple())

        df = df.set_value(index, "POSIX Timestamp", time_posix)
              
        #Now we have a beautiful dataset with only the time when it was created, its string and the text
        #What a time to be alive, let's add the sentiment
    
        #This library definitely doesn't like non ascii characters
        tweet = row[' Tweet Text'].decode('ascii', errors="ignore")
    
        #If we do not have text, continue to the next tweet
        if len(tweet) < minimum_length:
            continue
    
        #Create the object
        blob = TextBlob(tweet)
    
        #Do we need to translate those?
        if not in_english[d_index]:
            try:
                blob = blob.translate(to="en")
        
            #If the tweet is already on english, just continue
            except NotTranslated:
                print "Not translated"
                pass
        
            #Any other exception makes us go to the next tweet
            except Exception as e:
                print "ERROR", e
                continue
        
        
        #Because there might be more than one sentence on the tweet
        #we just normalize it
        polarity = 0.0
    
        for sentence in blob.sentences:
            polarity += sentence.sentiment.polarity
    
        polarity /= len(blob.sentences)

        print "The polarity of this tweet is", polarity

        #Complete the Dataframe
        df = df.set_value(index, "Sentiment", polarity)
        
    #Store the results on disk so I do not have to do this ever again
    #To load: df.read_pickle(disaster + ' .p')
    df.to_pickle(disaster + ' .p')

#Parallelize, as many processes as cores
num_cores = multiprocessing.cpu_count()

#Actually run the code
Parallel(n_jobs=num_cores)(delayed(process_disaster)(index, disaster) for index, disaster in enumerate(disasters))