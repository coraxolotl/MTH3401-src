import requests
from bs4 import BeautifulSoup
import string
import json

import re


def split_into_sentences(text):
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|edu|me)"
    digits = "([0-9])"

    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def remove_text_inside_brackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else: # character is not a [balanced] bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)

#get a dictionary of words removing brackets and punctuation keying them to h3 headings from given url
def get_dict_from_url(pageurl):
    numbering = 0
    response = requests.get(
        url=pageurl, #https://en.wikipedia.org/wiki/Crimean_War
    )
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find(id="firstHeading")
    #print(title.string)

    all = soup.find_all(["h3", "p"])
    #allp = soup.find_all("p")
    diction = dict()
    collateP = ""
    if title.string==None:
        tempHead = ""
        article = ""
    else:
        tempHead = title.string
        article = title.string
    count = 0
    for item in all:
        #if count==0 or count==1 or count==2:
         #   count+=1
          #  continue
        if item.name == "p":
            collateP+=(item.getText() + " ")
        elif item.name == "h3":
            #split into list of sentences sentences
            sentences = split_into_sentences(collateP)
            
            #for sentence in sentences: do the stuff below
            for sentence in sentences:
                collatePbetter = remove_text_inside_brackets(sentence).replace("\n", "").replace("\t","").replace("\xa0","").translate(str.maketrans('', '', string.punctuation))
                numbering+=1
                bodyActual = article + "_" + tempHead + "_" + str(numbering)
                diction[bodyActual] = collatePbetter
                


            #\xa0 seems to be quotes so maybe remove between aswell
            
            #numbering+=1
            
            #print(bodyActual)
            
            collateP=""
            tempHead=item.find("span").getText()
            if tempHead==("Notes" or "Citations"):
                break
            elif tempHead==None:
                tempHead=""
    return diction


#print(get_dict_from_url("https://en.wikipedia.org/wiki/Crimean_War"))
#in list url
#    in 0-9h3 ul   
#        get each url
#            in tbody 
#                3rd tr to end 
#                    3 td
#                        get 1 url

def get_list_of_links(pageurl):
    response = requests.get(
            url=pageurl #"https://en.wikipedia.org/wiki/List_of_wars:_before_1000",
        )

    soup = BeautifulSoup(response.content, 'html.parser')
    suffixes = []
    all_lists = soup.find_all("tr")
    for item in all_lists:
        try:
            for link in item.find_all_next("td")[2]:  #if is tag then pass (might be nicer syntax)
                if not link.name: continue
                try:
                    suffixes.append(link['href'])
                except:
                    continue
        except IndexError:
            break
    suffixes = list(dict.fromkeys(suffixes))
    return suffixes

links=get_list_of_links("https://en.wikipedia.org/wiki/List_of_wars:_before_1000")
for link in get_list_of_links("https://en.wikipedia.org/wiki/List_of_wars:_1000-1499"):
    links.append(link)
for link in get_list_of_links("https://en.wikipedia.org/wiki/List_of_wars:_1500-1799"):
    links.append(link)
for link in get_list_of_links("https://en.wikipedia.org/wiki/List_of_wars:_1800-1899"):
    links.append(link)
for link in get_list_of_links("https://en.wikipedia.org/wiki/List_of_wars:_1900-1944"):
    links.append(link)
for link in get_list_of_links("https://en.wikipedia.org/wiki/List_of_wars:_1945-1989"):
    links.append(link)
for link in get_list_of_links("https://en.wikipedia.org/wiki/List_of_wars:_1990-2002"):
    links.append(link)

#print(links)
#exit(-1)
full_dict={}
#print(links)
for link in links:
    #print(link)
    if link[:5] != "/wiki":
        #print(link)
        continue
    #print(type(link))
    
    #if type(link) != str:
        #print("link passed")
        #continue
    full_dict.update(get_dict_from_url("https://en.wikipedia.org" + link))
#print(full_dict)

counter = 0
#print(full_dict)
with open('wordsbody.json', 'a', encoding='utf8') as f:
    #json.dump(full_dict, f)
    for a,b in full_dict.items():
        if b == "":
            continue
        #print(a + " - " + b[:20])
        #json.dump({a: b}, f)
        json.dump({"body": b}, f)
        f.write('\n')

with open('wordslabelled.json', 'a', encoding='utf8') as f:
    #json.dump(full_dict, f)
    for a,b in full_dict.items():
        if b == "":
            continue
        #print(a + " - " + b[:20])
        json.dump({a: b}, f)
        #json.dump({"body": b}, f)
        f.write('\n')
        

#words = list(full_dict.values())
#with open('wordswordswords.txt', 'a', encoding='utf8') as f:
#    f.write(' '.join(words))

