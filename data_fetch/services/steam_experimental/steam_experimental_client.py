import requests # make http requests
import json # make sense of what the requests return
import pickle # save our data to our computer

import pandas as pd # structure out data
import numpy as np # do a bit of math
import scipy.stats as sci # do a bit more math

from datetime import datetime # make working with dates 1000x easier 
import time # become time lords
import random # create random numbers (probably not needed)
from enum import Enum
from steamcrawl import Request
import threading

STEAMLOGIN_KEY="76561198302329848%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MDAwNF8yNjNBRjUyRF80NDAzOCIsICJzdWIiOiAiNzY1NjExOTgzMDIzMjk4NDgiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3NDYyMzg5NzIsICJuYmYiOiAxNzM3NTEyNTQ3LCAiaWF0IjogMTc0NjE1MjU0NywgImp0aSI6ICIwMDE1XzI2M0FGNTNEXzVEREM1IiwgIm9hdCI6IDE3NDYwNTg1NjQsICJydF9leHAiOiAxNzY0MDAxNTY4LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiOTkuMTgzLjEzNC4xNSIsICJpcF9jb25maXJtZXIiOiAiOTkuMTgzLjEzNC4xNSIgfQ.dlPaB0OuVh2ZfqHPP2uVUagPib3eB2LtYQDMUwUy0uh-Ts5rFAgZNMr6yHiIWLnJlAV2XV2j7d5QUqZo9zXUAA"

Games = {
    "CS2": 730,
    "RUST": 252490,
    "PUBG": 578080
}

_FIVE_MINUTES = 300

class SteamExperimentalClient:
    def __init__(self):
        self.cookie = {'steamLoginSecure': STEAMLOGIN_KEY}
        self._order_ladder_cache = {}
        self._refresh_threads = {}
        self._request_sessions = {}  # Store persistent Request objects

    def get_item_data(self, item_name: str):
        pass

    def get_order_ladder(self, item_name: str, refresh_interval: int = None) -> pd.DataFrame:
        if refresh_interval is not None:
            # Start background refresh if not already running
            if item_name not in self._refresh_threads:
                thread = threading.Thread(
                    target=self._background_refresh,
                    args=(item_name, refresh_interval),
                    daemon=True
                )
                self._refresh_threads[item_name] = thread
                thread.start()
            # Return cached value if available
            if item_name in self._order_ladder_cache:
                return self._order_ladder_cache[item_name]
        # Fallback: fetch immediately
        return self._fetch_order_ladder(item_name)

    def _get_request_session(self, item_name: str):
        # Only create a new Request object if one doesn't exist
        if item_name not in self._request_sessions:
            self._request_sessions[item_name] = Request(steamLoginSecure=self.cookie['steamLoginSecure'])
        return self._request_sessions[item_name]

    def _fetch_order_ladder(self, item_name: str) -> pd.DataFrame:
        req = self._get_request_session(item_name)
        out: pd.DataFrame = req.get_buysell_orders(
            appid=str(Games['CS2']),
            item_name=item_name,
        )
        return out

    def _background_refresh(self, item_name: str, refresh_interval: int):
        req = self._get_request_session(item_name)
        while True:
            try:
                self._order_ladder_cache[item_name] = req.get_buysell_orders(
                    appid=str(Games['CS2']),
                    item_name=item_name,
                )
            except Exception as e:
                print(f"Error refreshing order ladder for {item_name}: {e}")
            time.sleep(refresh_interval)

    # Only gets ran once
    def _get_all_items(self, game: int):
        # initialize
        allItemNames = [];
        
        # find total number items
        try:
            allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid='+ str(game) +'&norender=1&count=100', cookies=self.cookie); # get page
            print("GOT CODE: "+str(allItemsGet.status_code))
            
            # Handle rate limiting
            if allItemsGet.status_code == 429:
                retry_after = allItemsGet.headers.get('Retry-After')
                wait_time = int(retry_after) if retry_after else _FIVE_MINUTES
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                # Retry the request
                allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid='+ str(game) +'&norender=1&count=100', cookies=self.cookie)
                print("Retry code: "+str(allItemsGet.status_code))
            
            allItems = allItemsGet.content; # get page content
            allItems = json.loads(allItems); # convert to JSON
            totalItems = allItems['total_count']; # get total count\
        except:
            print("Error getting total items")
            return

        # you can only get 100 items at a time (despite putting in count= >100)
        # so we have to loop through in batches of 100 to get every single item name by specifying the start position
        for currPos in range(0, totalItems + 50, 50): # loop through all items
            time.sleep(random.uniform(0.5, 2.5)) # you cant make requests too quickly or steam gets mad
            
            # get item name of each
            allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?start='+str(currPos)+'&count=100&search_descriptions=0&sort_column=default&sort_dir=desc&appid='+ str(game) +'&norender=1&count=5000', cookies=self.cookie);
            print('Items '+str(currPos)+' out of '+str(totalItems)+' code: '+str(allItemsGet.status_code)) # reassure us the code is running and we are getting good returns (code 200)
            
            # Handle rate limiting for each batch request
            if allItemsGet.status_code == 429:
                retry_after = allItemsGet.headers.get('Retry-After')
                wait_time = int(retry_after) if retry_after else _FIVE_MINUTES
                print(f"Rate limited at position {currPos}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                # Retry the request
                allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?start='+str(currPos)+'&count=100&search_descriptions=0&sort_column=default&sort_dir=desc&appid='+ str(game) +'&norender=1&count=5000', cookies=self.cookie)
                print('Retry code: '+str(allItemsGet.status_code))
            
            allItems = allItemsGet.content;
            allItems = json.loads(allItems);
            allItems = allItems['results'];
            for currItem in allItems: 
                allItemNames.append(currItem['hash_name']) # save the names

        allItemNames = list(set(allItemNames))
        # Save all the name so we don't have to do this step anymore
        # use pickle to save all the names so i dont have to keep running above code
        with open(str(game) + '_ITEMNAMES.txt', "wb") as file: # change the text file name to whatever you want
            pickle.dump(allItemNames, file)
    