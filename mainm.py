# Cleaning the jokes
cleaned_jokes = []

import re, csv
from profanity_check import predict, predict_prob # https://github.com/dimitrismistriotis/alt-profanity-check


threshold = 0.6
blacklist = ['naan', 'bukkake', 'tampon', 'cock', 'dildo', 'penis', 'lesbian', 'rectum', 'viagra', 'pleasuring', 'sex', 'squirt', 'porn', 'sperm', 'breast', 'anal', 'nipple', 'condom', 'masturbat', 'horny', 'virgin', 'ejaculat', 'tits', 'prostitut', 'blowjob', 'blow job']

myFile = open('g4g.csv', 'r')
reader = csv.DictReader(myFile)
gjlist = list(reader)
print(len(gjlist))


for i, entry in enumerate(gjlist):
  if i%100 ==0 : print(i, ' jokes done')
  title = entry['title'].strip()
  content = entry['selftext'].strip()

  if 'Reposts' in title or 'school shooting jokes' in title or len(title) == 0 or title[-1] == '?' or len(content) == 0 or content[-1] == '?' or len(content) > 1600: pass

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
    
    if any(x == y[:len(x)].lower() for y in titlelist for x in blacklist) or any(x == y[:len(x)] for y in contentlist for x in blacklist) or any([x > threshold for x in predict_prob(re.split(r'[.?!;]', content))]) or any([x > threshold for x in predict_prob(re.split(r'[.?!;]', title))]) or  content.count(' ') < 20: pass
    else: 
      cleaned_jokes.append(title + '\n' + content)
      print(len(cleaned_jokes))
      
file = open('cl.csv', 'w')

with file:
    # identifying header 
    header = ['text']
    writer = csv.DictWriter(file, fieldnames = header)

    # writing data row-wise into the csv file
    writer.writeheader()
    for j in cleaned_jokes: 
      dj = {'text':j}
      writer.writerow(dj)
