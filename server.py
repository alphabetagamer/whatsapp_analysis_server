import re
from emoji import UNICODE_EMOJI
import emoji
import regex
# from symspellpy.symspellpy import SymSpell, Verbosity
import pkg_resources
# from nltk.tokenize import word_tokenize
# import nltk
# from allennlp.predictors.predictor import Predictor
# import allennlp_models.classification
import datetime
from flask import Flask
from flask import request
from werkzeug.utils import secure_filename

app = Flask(__name__)
stopwords=list(set(open("stopwords/stopwords.txt","r",encoding='utf8').readlines()))
stopwords=[re.sub("(\n)|(')","",i).lower() for i in stopwords]

def split_count(text):

    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI for char in word):
            emoji_list.append(word)

    return emoji_list
def preprocess(data):
    pattern = re.compile("(\d{1,2}\/\d{1,2}\/\d{2,4}, \d{1,2}:\d{1,2})")
    for line in range(len(data)-1,0,-1):
        if(not pattern.match(data[line])):
            data[line-1]=data[line-1]+" "+data[line]
            del data[line]
    pat_re = re.compile('( - \w+ created group )((".+")|(\'.+\'))')
    pat_add = re.compile('( - \w+ )((removed)|(added))((.+))')
    # if(" - Messages to this chat and calls are now secured with end-to-end encryption. Tap for more info.\n" in data[0]):
    #     data=data[1:]
    for line in range(len(data)-1,-1,-1):
        if("security code changed. Tap for more info.\n" in data[line] or pat_re.search(data[line].strip()) or pat_add.search(data[line].strip()) or " - Messages to this group are now secured with end-to-end encryption. Tap for more info." in data[line] or " - Messages to this chat and calls are now secured with end-to-end encryption. Tap for more info.\n" in data[line]):
            data.pop(line)
    sender=[]
    date=[]
    time=[]
    text=[]
    emoji_dict=[]
    is_deleted=[]
    is_media=[]
    weekday=[]
    username=[]
    for line in data:
        temp_emo={}
        temp=""
        temp_time=""
        date.append(line.split(" - ")[0].split(", ")[0])
        temp_weekd=line.split(" - ")[0].split(", ")[0].split("/")
        week_day=7
        try:
            week_day=datetime.datetime(int(temp_weekd[2]),int(temp_weekd[0]),int(temp_weekd[1])).weekday()
        except:
            week_day=7
        weekday.append(week_day)
        if("PM" in line.split(" - ")[0].split(", ")[1] and line.split(" - ")[0].split(", ")[1].split(":")[0]!="12"):
            temp_time=str(int(line.split(" - ")[0].split(", ")[1].split(":")[0])+12)+":"+"".join(line.split(" - ")[0].split(", ")[1].split(":")[1:])
        else:
            temp_time=str((line.split(" - ")[0].split(", ")[1]).replace("AM",""))
        temp_time=temp_time.replace("PM","").strip()
        temp_time=(int(temp_time.split(":")[0])*60+int(temp_time.split(":")[1]))
        time.append(temp_time)
        if(username):
            temp_flag=0
            for user in username:
                if(user == line.split(" - ")[1][:len(user)]):
                    sender.append(user)
                    temp=line.split(" - ")[1][len(user)+2:].replace("\n"," .")
                    temp_flag=1
                    break
            if(temp_flag != 1):
                sender.append(line.split(" - ")[1].split(": ")[0])
                temp=": ".join(line.split(" - ")[1].split(": ")[1:]).replace("\n"," .")
        else:
            sender.append(line.split(" - ")[1].split(": ")[0])
            temp=": ".join(line.split(" - ")[1].split(": ")[1:]).replace("\n"," .")
        text.append(emoji.demojize(temp))
        emo_list=split_count(temp)
        emo_set=set(emo_list)
        for emo in emo_set:
            temp_emo[emo]=emo_list.count(emo)
        emoji_dict.append(temp_emo)
        if(temp=="<Media omitted> ."):        
            is_media.append(True)
            is_deleted.append(False)
        elif(temp=="This message was deleted ." or temp=="You deleted this message ."):
            is_deleted.append(True)
            is_media.append(False)
        else:        
            is_media.append(False)
            is_deleted.append(False)
    data_super=[]

    for chat in range(0,len(sender)):
        data_super.append({'sender':sender[chat],"date":date[chat],"time":time[chat],"text":text[chat],"emoji_dict":emoji_dict[chat],"is_deleted":is_deleted[chat],"is_media":is_media[chat],"weekday":weekday[chat]})
    return data_super    
def clean(data_super):
    for chat in range(0,len(data_super)):
        temp=data_super[chat]['text']
        temp="".join([i if i.isalpha() or i==" " else " " for i in temp ]).strip()
        temp=" ".join([i if len(i)>1 else "" for i in temp.split()])
        temp=re.sub("(\s+)"," ",temp).strip()
        temp=[i.lower() for i in temp.split() if i.lower() not in stopwords]
        data_super[chat]["text_clean"]=" ".join(list(dict.fromkeys(temp)))
    return data_super
def collect_full(data_super):
    users=list(set([i['sender'] for i in data_super]))
    week_day_name=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","TimeformatError"]
    users_profile={}
    # "mention":{}, currently not able to get this data from 
    for user in users:
        users_profile[user]={"emoji":{},"active_time":{"morning":0,"afternoon":0,"evening":0,"night":0},"media":0,"delete":0,"active_day":{},"words":{}}
    for chat in data_super:
        if(chat['is_media']):
            users_profile[chat['sender']]["media"]=users_profile[chat['sender']]["media"]+1
        elif(chat['is_deleted']):
            users_profile[chat['sender']]["delete"]=users_profile[chat['sender']]["media"]+1
        if(chat['emoji_dict']):
            for emo in chat['emoji_dict'].keys():
                if(emo not in users_profile[chat['sender']]['emoji'].keys()):
                    users_profile[chat['sender']]['emoji'][emo]=chat['emoji_dict'][emo]
                else:
                    users_profile[chat['sender']]['emoji'][emo]=users_profile[chat['sender']]['emoji'][emo]+chat['emoji_dict'][emo]
        if(week_day_name[chat["weekday"]] in users_profile[chat['sender']]['active_day'].keys()):
            users_profile[chat['sender']]['active_day'][week_day_name[chat["weekday"]]]=users_profile[chat['sender']]['active_day'][week_day_name[chat["weekday"]]]+1
        else:
            users_profile[chat['sender']]['active_day'][week_day_name[chat["weekday"]]]=0
        if(chat["time"]<=360):
            users_profile[chat['sender']]['active_time']["night"]=users_profile[chat['sender']]['active_time']["night"]+1
        elif(chat["time"]<=720):
            users_profile[chat['sender']]['active_time']["morning"]=users_profile[chat['sender']]['active_time']["morning"]+1
        elif(chat["time"]<=1080):
            users_profile[chat['sender']]['active_time']["afternoon"]=users_profile[chat['sender']]['active_time']["afternoon"]+1
        else:
            users_profile[chat['sender']]['active_time']["evening"]=users_profile[chat['sender']]['active_time']["evening"]+1
        for word in chat['text_clean'].split():
            if(word in users_profile[chat['sender']]["words"].keys()):
                users_profile[chat['sender']]["words"][word]=users_profile[chat['sender']]["words"][word]+1
            else:
                users_profile[chat['sender']]["words"][word]=1
    return users_profile


@app.route('/data',methods=['POST'])
def recieve():
    if(secure_filename(request.files['input'].filename).split(".")[-1] in ["txt"]):
        try:
            file_re = request.files['input']
            data = file_re.readlines()
            data=[i.decode("utf-8") for i in data]
            data_super= preprocess(data)
            data_super= clean(data_super)
            final_res= collect_full(data_super)
            return final_res,200
        except:
            return "Error in this vast file",500
    else:
        return "Error Wrong file format",500
@app.route('/',methods=['GET'])
def wrongway():
    return "HEY IF YOURE LOOKING FOR THE WHATSAPP DATA USE https://whatsapp-analyze.herokuapp.com:5000/data with your file in forma-data with key input",200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)