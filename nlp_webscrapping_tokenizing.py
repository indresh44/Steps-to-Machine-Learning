# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 19:00:16 2017

@author: Indresh
"""

from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.corpus import stopwords
from string import punctuation
from collections import defaultdict


# print(stopwords.words('english'))
class FrequencyCounter:
    
    def __init__(self,min_cut=0.1,max_cut=0.9):
        self.min_cut=min_cut
        self.max_cut=max_cut
        
        self._stopwords = set(stopwords.words('english')+list(punctuation)+['.',',',"'", '“', '”','’', '‘'])
        self._skips = ['.',',',"'", '“', '”','’', '‘']
    def _compute_frequency(self,word_sent):

        freq_dict = {}
        
        for sent in word_sent:
            for word in sent:
                if word not in self._stopwords:
                    c = freq_dict.get(word,0)
                    freq_dict[word]=c+1
    
        m = float(max(freq_dict.values()))
        
        # print(freq_dict)
        for w in list(freq_dict.keys()):
            freq_dict[w] = freq_dict[w]/m
            if freq_dict[w]<self.min_cut or freq_dict[w]>self.max_cut:
                del freq_dict[w]
                
        return freq_dict
    
    def extractFeatures(self,article,n):
        text = article[1]
        sentence = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentence]
        self._freq = self._compute_frequency(word_sent)
        print(self._freq)
        list1 = sorted(self._freq.keys(),key= lambda x:self._freq[x],reverse=True)
        return list1[:n]
        
    
    def summarize(self,text,n):
        sents = sent_tokenize(text)
        
        assert n <= len(sents)
        # assert is a way of making sure a condition holds true, else an exception is thrown. Used to do 
        # sanity checks like making sure the summary is shorter than the original article.
        
        word_sent = [word_tokenize(s.lower()) for s in sents]
        freq = self._compute_frequency(word_sent)
        print("\n\nfrequency->\n",freq,"\n\n")
        ranking = {}
        for i,sent in enumerate(word_sent):
            ranking[i]=0
            for word in sent:
                if word in freq:
                    ranking[i]+=freq[word]
                    
        sort_index = sorted(ranking.keys(),key=lambda x:ranking[x], reverse =True)
        top_n = [sents[j] for j in sort_index[:n]]
        return top_n
        
    
import urllib.request
from bs4 import BeautifulSoup
    
def get_only_text_from_url(url):
    page = urllib.request.urlopen(url).read().decode('utf8')
    
    soup1 = BeautifulSoup(page)
    text= ' '.join(map(lambda x:x.text,soup1.find_all('article')))
    
    soup2 = BeautifulSoup(text)
    text =' '.join(map(lambda x:x.text,soup2.find_all('p')))
    
    return soup1.title.text,text
    
text = "this is about calculating the frequency of is is is each each word. Most Important is to calculate the most frequent words."

test_url = "https://www.washingtonpost.com/investigations/eight-women-say-charlie-rose-sexually-harassed-them--with-nudity-groping-and-lewd-calls/2017/11/20/9b168de8-caec-11e7-8321-481fd63f174d_story.html?hpid=hp_hp-top-table-main_rose-450pm%3Ahomepage%2Fstory&utm_term=.604dbaf1a14d"
# x,y = get_only_text_from_url(test_url)
#print(y)
#sent = sent_tokenize(y)
#word_sent = [word_tokenize(s.lower()) for s in sent]
#fre1 = FrequencyCounter()
#print(fre1._compute_frequency(word_sent),'\n')

#print("\n\n",fre1.summarize(y,3))

################################################################################################
##---------------- Web Scrapping -------------------##
################################################################################################


def scrapeSite(url,scraperFunction,magicFrag = '2017',token = None):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    soup1 = BeautifulSoup(response)
    
    urldict = {}
    
    numerror = 0
    for a in soup1.findAll('a'):
        try:
            url=a.get('href')
#            if ((url not in urldict) and ((magicFrag is not None and magicFrag in url) or magicFrag is None)):
            if( (url not in urldict) and ((magicFrag is not None and magicFrag in url) or magicFrag is None)):
                body = scraperFunction(url)
#                print(body)                    
                if body and len(body)>0:
                    urldict[url] = body
#                print(url)
                
        except:
            numerror +=1
    return urldict

#scrapeSite("https://www.washingtonpost.com/sports",get_only_text_from_url,'2017','article')

urlWashingtonPostNonTech = "https://www.washingtonpost.com/sports"
urlWashingtonPostTech = "https://www.washingtonpost.com/business/technology"

washingtonPostTechArticles = scrapeSite(urlWashingtonPostTech,
                                         get_only_text_from_url,
                                         '2017',
                                         'article')
washingtonPostNonTechArticles = scrapeSite(urlWashingtonPostNonTech,
                                         get_only_text_from_url,
                                         '2017',
                                         'article')
#print(washingtonPostTechArticles)

articleSummaries = {}

for techUrlDictionary in [washingtonPostTechArticles]:
    for articleUrl in techUrlDictionary:
        if techUrlDictionary[articleUrl][1] is not None:
            if len(techUrlDictionary[articleUrl][1]) > 0:
                fs = FrequencyCounter()
                summary = fs.extractFeatures(techUrlDictionary[articleUrl],25)
                articleSummaries[articleUrl] = {'feature-vector': summary,
                                               'label': 'Tech'}
for techUrlDictionary in [washingtonPostNonTechArticles]:
    for articleUrl in techUrlDictionary:
        if techUrlDictionary[articleUrl][1] is not None:
            if len(techUrlDictionary[articleUrl][1]) > 0:
                fs = FrequencyCounter()
                summary = fs.extractFeatures(techUrlDictionary[articleUrl],25)
                articleSummaries[articleUrl] = {'feature-vector': summary,
                                               'label': 'Non-Tech'}
print("\n\n\n article summary-:\n\n",articleSummaries,"\n\n\n")

def getdoxydonkeytext(url):
    page = urllib.request.urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(page)
    mydivs = soup.findAll("div", {"class":'post-body'})
    text = ''.join(map(lambda p:p.text,mydivs))
    return soup.find('title').text,text

doxyurl = 'http://doxydonkey.blogspot.in'
testarticle = getdoxydonkeytext(doxyurl)

fs1 = FrequencyCounter()
doxysumm = fs1.extractFeatures(testarticle,25)

simmilarity = {}
for articleurl in articleSummaries:
    onearticlesumm = articleSummaries[articleurl]['feature-vector']
    simmilarity[articleurl]=len(set(doxysumm).intersection(set(onearticlesumm)))
    
print("\n\n summary-:\n",simmilarity)

labels = defaultdict(int)  
knn = sorted(simmilarity.keys(),key = lambda x:simmilarity[x],reverse = True)[:5]
print(knn)
for i in knn:
    labels[articleSummaries[i]['label']]+=1

print(labels)

def gethindustantimestext(url):
    page = urllib.request.urlopen(url).read().decode('utf8').encode('cp850','replace').decode('cp850')
    soup = BeautifulSoup(page)
    divs = soup.findAll('div',{'class':'story-details'})
    text = ''.join(map(lambda x:x.text,divs))
    return soup.find('title').text,text

hturl = 'http://www.hindustantimes.com/football/russia-ready-for-fifa-world-cup-draw-with-spain-the-team-to-avoid/story-hC9gA4kZAHGEG05mcMTtCL.html'
hturl_tech ="http://www.hindustantimes.com/tech/oneplus-5t-review-because-oneplus-couldn-t-settle-with-just-oneplus-5/story-EvcOy2dNklqZmjAzr2g4pK.html"
testarticle = gethindustantimestext(hturl_tech)
fs1 = FrequencyCounter()
doxysumm = fs1.extractFeatures(testarticle,25)

simmilarity1 = {}
for articleurl in articleSummaries:
    onearticlesumm = articleSummaries[articleurl]['feature-vector']
    simmilarity1[articleurl]=len(set(doxysumm).intersection(set(onearticlesumm)))
    
print("\n\n summary1-:\n",simmilarity1)

labels1 = defaultdict(int)  
knn = sorted(simmilarity1.keys(),key = lambda x:simmilarity1[x],reverse = True)[:5]
print(knn)
for i in knn:
    labels1[articleSummaries[i]['label']]+=1
print(labels1)