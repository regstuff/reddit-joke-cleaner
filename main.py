import feedparser, re, os, sys, json, requests, urllib.parse
from requests.structures import CaseInsensitiveDict
from datetime import datetime
import time
from profanity_check import predict, predict_prob # https://github.com/dimitrismistriotis/alt-profanity-check
import smtplib, ssl # For emailer
from email.message import EmailMessage

rjokes = 'https://www.reddit.com/r/jokes/.rss'
finalmsg = ''
threshold = 0.6
token = os.environ['TOKEN']
owner = os.environ['OWNER']
count = 0
accepted = 0
blacklist = ['plethora', 'blew a seal', 'erotic', 'blew chunks', 'I can get a haircut?', 'punchline', 'testicles', 'panties', 'naan', 'bukkake', 'tampon', 'cock', 'orgasm', 'dildo', 'whore', 'made love', 'make love', 'making love',  'penis', 'lesbian', 'rectum', 'viagra', 'pleasuring', 'sex', 'squirt', 'porn', 'sperm', 'breast', 'anal', 'nipple', 'condom', 'masturbat', 'horny', 'virgin', 'ejaculat', 'tits', 'prostitut', 'blowjob', 'blow job', 'jerking']

headers = CaseInsensitiveDict()
headers["Accept"] = "application/vnd.github+json"
headers["Authorization"] = "token " + token

receiverid = os.environ['receiverid']
senderid = os.environ['senderid']
mailpassword = os.environ['mailpass']

clientid = os.environ['clientid']
clientpass = os.environ['clientpass']
rusername = os.environ['rusername']
ruserpass = os.environ['ruserpass']

client_auth = requests.auth.HTTPBasicAuth(clientid, clientpass)
post_data = {"grant_type": "password", "username": rusername, "password": ruserpass}
rheaders = {"User-Agent": "personalscript/0.1 by regstuff"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=rheaders)
toke = response.json()
rheaders = {"Authorization": f"bearer {toke['access_token']}", "User-Agent": "personalscript/0.1 by regstuff"}
response = requests.get("https://oauth.reddit.com/r/jokes/top", headers=rheaders)
entries = response.json()['data']['children']

for entry in entries:
  count += 1
  title = entry['data']['title'].strip()
  content = entry['data']['selftext'].strip()
  created = entry['data']['created']
  print(content)

  if 'Reposts' in title or 'school shooting jokes' in title or title[-1] == '?' or content[-1] == '?' or len(content) > 1600 or time.time()-created>86400: pass

  else:
    title = title.replace('...', '.').replace('"', '\'').replace('\n', ' ').strip() # Replace ellipsis to create easy sentence breaks, and " so JSON doesn't fail.
    title = re.sub(r'[^\w -.?,\'\"!;:&\(\)]','',title)
    #title = bytes(title,'utf-8').decode('utf-8', 'ignore')
    content = content.replace('...', '.').replace('"', '\'').split('&#32;')[0].strip() # Split on open quote. After that is all metadata
    content = re.sub(r'<.*?>','',content)
    content = re.sub('&[a-z]*;','',content)
    content = re.sub(r'[^\w -.?,\'\"!;:&\(\)]','',content)
    #content = bytes(content,'utf-8').decode('utf-8', 'ignore')
    #link = entry.links[0].href
    titlelist = re.split(r'[.?!; \'\"]', title)
    contentlist = re.split(r'[.?!; \'\"]', content)
    
    if any(x.lower() in content.lower() for x in blacklist) or any(x.lower() in title.lower() for x in blacklist) or any(x == y[:len(x)].lower() for y in titlelist for x in blacklist) or any(x == y[:len(x)] for y in contentlist for x in blacklist) or any([x > threshold for x in predict_prob(re.split(r'[.?!;]', content))]) or any([x > threshold for x in predict_prob(re.split(r'[.?!;]', title))]) or  content.count(' ') < 20: pass
    else: 
      print(title)
      print(predict_prob(re.split(r'[.?!;]', content)), predict_prob(re.split(r'[.?!;]', title)))
      accepted += 1
      finalmsg += f"=============\\n<strong>{title}</strong>\\n{content}\\n\\n"
      
with open('jokes.txt', 'w') as f:
  f.write(finalmsg)

print(accepted, 'jokes sent of', count, 'total jokes.')
#print(finalmsg)

open_api_url = f"https://api.github.com/repos/{owner}/reddit-joke-cleaner/issues" # Close the issue
#data = '{"title":"today","body":'+'finalmsg'+'}'
data = '{"title":"' + datetime.today().strftime("%Y%m%d") + '","body":"' + finalmsg + '"}'
print(data)
resp = requests.post(open_api_url, headers=headers, data=data)
if resp.status_code == 201: 
  #print(issue_number)
  issue_number = resp.json()["number"]
  print(f'Issue {issue_number} was opened.')

  close_api_url = f"https://api.github.com/repos/{owner}/reddit-joke-cleaner/issues/{issue_number}" # Close the issue
  data = '{"state":"closed"}'
  resp = requests.patch(close_api_url, headers=headers, data=data)
  if resp.status_code == 200: print(f'Issue {resp.json()["number"]} was closed.')
  else: print(f'Issue {resp.json()["number"]} closing failed with status {resp.status_code}, and reason {resp.reason}')

else: print(resp.status_code, resp.text)

def sendmail(mailmessage):
  if mailmessage != '':
    context = ssl.create_default_context()
    msg = EmailMessage()
    msg['Subject'] = 'Reddit Jokes Update'
    msg['To'] = receiverid 
    msg['From'] = senderid
    msg.set_content(mailmessage)
    print(mailmessage)
    #for receiverid in receiverids: # Send mail to all receiver ids
    print('Sending email')
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(senderid, mailpassword)
        server.send_message(msg)
        
    print('Email sent')
