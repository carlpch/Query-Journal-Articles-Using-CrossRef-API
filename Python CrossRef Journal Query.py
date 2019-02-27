#!/usr/bin/env python
# coding: utf-8
''' Python CrossRef Journal Query
# 
# Carl Pi-Cheng Huang (2019-02-25)
# ## Motivation 
# Are there ways to get regular updates from a journal other than using a headless browser? This short note seeks to try out one python package: 
# Fabio Batalha's <a href="https://github.com/fabiobatalha/crossrefapi">CrossRef API</a>. 
# For R users, the <a href="https://github.com/ropensci/rcrossref">rcrossref</a> (R interface to various CrossRef APIs) seems neat. I will try to stick to Python because I might need  to pass the results to my Mediawiki later. 
# https://qiita.com/ina111/items/bbdecf9c711cc0bc54d5
# I will be primarily dealing with `Works`, as this refers to the journal articles (or books).'''

### Loading packages and journal ISSN information:
from crossref.restful import Works
works = Works()
from crossref.restful import Journals
journals = Journals()
from pandas import DataFrame

### Function1: Make a Query to CrossRef
  # Take:  (i) journal name (2) keyword
  # Return A list of dictionary with info of specific work(s)

def journalQuery(jname, keyword):
    jdata = {'AJPS':'00925853', 
             'APSR':'00030554', 
             'CMPS':'0738-8942', 
             'IS':'0162-2889', 
             'IO':'0020-8183', 
             'IMR':'1747-7379'}
    return [i for i in journals.works(jdata[jname]).query(keyword).select(['author','title','issued','container-title','DOI'])]

'''     Function2: Formatting Table
Take:   A list of dictionary with CrossRef API format (typically should be from Function 1)
Return: A Pandas DataFrame with the same information after some tidying up'''

def Query2Data(query):
    df = DataFrame(columns=['Last Name', 'First Name', 'Author Title', 'Journal', 'Year', 'Month', 'Title', 'DOI'])
    for item in query: 
        if ('author' not in item):
            item['Last Name'] = ""
            item['First Name'] = ""
            item['Author Title']=""
        else:
            item['Last Name'] = item['author'][0]['family']
            item['First Name'] = item['author'][0]['given']
            if len(item['author'][0]['affiliation'])==0:
                item['Author Title'] = ""
            else:
                item['Author Title'] = item['author'][0]['affiliation'][0]['name']
        item['Journal'] =  item['container-title'][0]
        item['Year'] =  str(item['issued']['date-parts'][0][0])
        item['Month'] = str(item['issued']['date-parts'][0][1])
        item['Title'] = item['title'][0]
        
        item={i:item[i] for i in ['Last Name', 'First Name', 'Author Title', 'Journal', 'Year', 'Month', 'Title', 'DOI']}
        df=df.append(item, ignore_index=True)
    return df

### Function3: Build Wikitable
  # Take:  A Pandas DataFrame with valid column name
  # Return:Print out codes to compile a Wikitable in MediaWiki

def wikitable(df):
    print('{|class="wikitable sortable"')
    for column_name in df.columns:
        print('!', column_name)
    print('|-')
    for i in range(len(df)):
        for j in range(len(df.columns)):
            print('|', df.ix[i,j])
        if i+1<len(df):
            print("|-")
        else:
            print("|}")

### Function4: Write MediaWiki
  # Take:   'Wikitext', the title of an MediaWiki article, login information of WikiBot
  # Return: An url showing that everything is neat and tidy!

##########################################################################################
# Look at "Sample Code" "edit.py" for more information. It's very well-written
# https://www.mediawiki.org/wiki/API:Edit#API_documentation

def add_to_bobohome(page_name, new_section, section_title, text):
    import requests
    S = requests.Session()
    URL = "http://bobo.home/w/api.php"
    section = 'new'
    if new_section != 1:
        section = 0
    
    # (1/4) Retrieve login token first
    PARAMS_1 = {
    'action':"query",
    'meta':"tokens",
    'type':"login",
    'format':"json"
    }

    R = S.get(url=URL, params=PARAMS_1)
    DATA = R.json()
    LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
    #print(LOGIN_TOKEN)

    # Send a post request to login. Using the main account for login is not
    # supported. Obtain credentials via Special:BotPasswords
    # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
    
    lgname = input("Please enter your username: ") 
    lgpassword = input("Please enter your password: ")
    
    PARAMS_2 = {
        'action':"login",
        'lgname':lgname,
        'lgpassword':lgpassword,
        'lgtoken':LOGIN_TOKEN,
        'format':"json"
    }
    
    R = S.post(URL, data=PARAMS_2)
    
    # Step 3: While logged in, retrieve a CSRF token
    PARAMS_3 = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }
    
    R = S.get(url=URL, params=PARAMS_3)
    DATA = R.json()
    CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]

    # Step 4: Edit
    PARAMS_4 = {
      'action' : 'edit',
      'title' : page_name,
      'section': section,
      'sectiontitle': section_title,
      'prependtext': text + '<br>',
      'token' : CSRF_TOKEN
    }
    
    R = S.post(URL, data=PARAMS_4)
    #DATA = R.json()
    #print(DATA)
    return


    