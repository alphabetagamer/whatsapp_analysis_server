# whatsapp_analysis_server
Whatsapp chat information and summary 

To set up 
1. Install requirements.txt 
2. run : python server.py

# Send POST request to 
```
localhost:5000/data
```
with your whatsapp chat export as form-data with key as "input"
# Structure:

A dictionary of users with the username as key :

Each user keys has the following data : 

"Active_day" : a dictionary with keys as days of the week and the number of messages sent on the corresponding day 

"Active_time" : a dictionary with keys afternoon,night, morning, evening and the corresponding messages sent 

"Delete": the number of messages deleted by the user 

"Emoji" a dictionary with emoji used as key and number of times used as value 

"Words" : a dictionary with the word as key and it's number of use as value


# How to get chat data?
Step 1: <img src="/images/step1.png" width="300" height="300">


Step 2: <img src="/images/step2.png" width="300" height="450">


Step 3: <img src="/images/step3.png" width="300" height="300">
