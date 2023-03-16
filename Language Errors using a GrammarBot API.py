#!/usr/bin/env python
# coding: utf-8

# In[1]:


#importing the required libraries
import requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re as re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


# In[2]:


#initialise the web driver
browser = webdriver.Chrome(ChromeDriverManager().install())


# In[19]:


#API Token Setup
url = "https://grammarbot.p.rapidapi.com/check"
headers = {
    "content-type": "application/x-www-form-urlencoded",
    "X-RapidAPI-Key": "a4aa62e190mshd78fa7329fec47bp1cbb9ejsnd7dcc93af818",
    "X-RapidAPI-Host": "grammarbot.p.rapidapi.com"
}


# In[4]:


#importing the input file
scorebuddy = pd.read_csv(r"/Users/rajkupekar/Desktop/Scorebuddy_UniqueBlogs.csv")
blog_urls=scorebuddy["Blog_URLs"].tolist()


# In[5]:


# Lists that we will iterate to
Blog_Texts = []


# In[6]:


for url in range(len(blog_urls)):
    browser.get(blog_urls[url])
    time.sleep(2)
    
    try:
        blog_text=browser.find_element(By.XPATH,"//span[@id='hs_cos_wrapper_post_body']").text.strip()
        Blog_Texts.append(blog_text)
    except:
        Blog_Texts.append("error")
    print(blog_text)


# In[7]:


scorebuddy["Blog_Text"]=Blog_Texts


# In[8]:


scorebuddy.head(30)


# In[9]:


replacers = {
'KPIs': 'Key Performance Indicators',
'KPI': 'Key Performance Indicator',
'CSAT' : 'Customer Satisfaction Score',
'ASA': 'Average Speed of Answering',
"AIT" : "Average Idle Time",
"CES" : "Customer Effort Score",
"AAR" : "Average Abandonment Rate",
"QA" : "Quality Analyst",
"CX" : "Customer's Experience"}


# In[10]:


def cleantext(x):
    text=re.sub("\n"," ",x)
    text=text.split()
    text=" ".join(text)
    return(text)


# In[11]:


def replace_all(word, dic):
    for i, j in dic.items():
        word = word.replace(i, j)
    return word


# In[12]:


scorebuddy["Blog_Text"]=scorebuddy["Blog_Text"].apply(lambda x : cleantext(x))


# In[13]:


scorebuddy["Blog_Text"]=scorebuddy["Blog_Text"].apply(lambda x : replace_all(x,replacers))


# In[14]:


scorebuddy["Blog_Text"]=scorebuddy["Blog_Text"].apply(lambda x : f"text= {x}")


# In[ ]:


#scorebuddy["Blog_Text"]=scorebuddy["Blog_Text"].apply(lambda x : f"{x}&language=en-US")


# In[15]:


scorebuddy["Blog_Text"][0]


# In[ ]:


"""def cleantext(x):
    text=re.sub("http[s]?://\S+","links",x)
    text=re.sub("#([a-zA-Z0-9_]{1,50})","hashtags",text)
    text=re.sub("Â","",text)
    text=re.sub("â\S+"," ",text)
    text=re.sub("www.\S+"," ",text)
    text=re.sub("[.()?/\,+]|[0-9]"," ",text)
    text=text.split()
    text=" ".join(text)
    return(text)"""


# In[16]:


Total_Errors=[]
Grammar_Errors=[]
Spelling_Errors=[]
URL_ID=[]
Other_Errors=[]
ID=1


# In[17]:


Body_Texts=scorebuddy["Blog_Text"]


# In[20]:


for text in Body_Texts:
    payload=text
    response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)
    response_text=response.text
    response_dictionary = json.loads(response_text)
    total_errors=len(response_dictionary['matches'])
    grammar_errors=0
    spell_errors=0
    other_errors=0
    try:
        for i in range(total_errors):
            error_type=response_dictionary["matches"][i]["rule"]['issueType']
            if error_type=="grammar":
                grammar_errors= grammar_errors+1
            elif error_type=="misspelling":
                spell_errors=spell_errors+1
            else:
                other_errors= other_errors+1
    except:
        pass
    total_content_error= grammar_errors+spell_errors
    Total_Errors.append(total_content_error)
    URL_ID.append(ID)
    Grammar_Errors.append(grammar_errors)
    Spelling_Errors.append(spell_errors)
    Other_Errors.append(other_errors)
    ID+=1
    print('Total Error',total_content_error)
    
    


# In[ ]:


Body_Texts[4]


# In[21]:


data = {
    "URL ID":URL_ID,
    "Total Errors": Total_Errors,
    "Grammar Errors": Grammar_Errors,
    "Spelling Errors": Spelling_Errors,
    "Other Errors": Other_Errors
}

df = pd.DataFrame(data)


# In[29]:


scorebuddy.head(30)


# In[30]:


scorebuddy.to_csv(r'/Users/rajkupekar/Desktop/Python Outputs/scorebuddy_final_2.csv', index=False)


# In[24]:


scorebuddy["URL ID"]=URL_ID


# In[25]:


scorebuddy["Total Errors"]=Total_Errors


# In[26]:


scorebuddy["Grammar Errors"]=Grammar_Errors


# In[27]:


scorebuddy["Spelling Errors"]=Spelling_Errors


# In[28]:


scorebuddy["Other Errors"]=Other_Errors

