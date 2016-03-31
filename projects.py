import sys,os,json
from numpy import inf, float128
from datetime import date, time
from dateutil import relativedelta
from functools import reduce
from time import time as now
from random import shuffle
from copy import deepcopy
from statistics import pvariance, pstdev, mean
from bisect import insort



best_workdays = {
  "quality": inf,
  "workdays": {}
}
events = {}
original_workdays = {}
workdays = {}
args = {
  '-h': ['-h','--help'],
  '-a': ['-a','--attempts'],
  '-d': ['-d','--start-day'],
  '-q': ['-q','--quality'],
  '-D': ['-D','--day-amplifier']
}
date_amplifiers = [
  {"default": 1},
  {"default": 1},
  {"default": 1},
  {"default": 1},
  {"default": 1},
  {"default": 1},
  {"default": 1}]

def getDateAmplifier(d):
  return (date_amplifiers[d.weekday()][str(d)]
    if str(d) in date_amplifiers[d.weekday()]
    else date_amplifiers[d.weekday()]['default'])
  

def getArgIndex(arg):
  if any([a in args[arg] for a in sys.argv]):
    for a in args[arg]:
      if a in sys.argv:
        return sys.argv.index(a)
  return -1

#inverse proportion of density of average number of hours worked per day
'''

daterange for event x by sum of average hours per event till that date:

11-1 11-2 11-3 11-4 11-5 11-6 11-7 
15   12   13   11   10   6    5  sum=72

daterange for event x by average hours for x till that date:

11-1 11-2 11-3 11-4 11-5 11-6 11-7 
2    2    2    2    2    2    2  sum=14

proportioned according to above density inverted:

daterange for event x by average hours for x till that date:

11-1 11-2 11-3 11-4 11-5 11-6 11-7 
14*15/72=2.9 14*12/72= NONONONNONO invert it !!!!!



2 + 1 + 1 + 1/2 + 3 + 1 + 1


'''
def populate_days(start, nDays):
  return [start+relativedelta.relativedelta(days=d) 
          for d in range(nDays)]

def populate_hours(days,current_event):
  return [ 
    sum(
      [ y[1] 
      for key,y in workdays[x.toordinal()].items() 
      if key!=current_event]) / getDateAmplifier(x)
    for x in days]

def hour_sorted(lst, hours):
  temp = [x
          for x in sorted(
            zip(hours,lst),
            reverse=True)]
  return [x[0] for x in temp], [x[1] for x in temp]

def process_event(clas,work,event,nDays):
  days = populate_days(event[3],nDays)
  hours = populate_hours(days,clas+"_"+work)
  # print(hours,clas,work,event,nDays)
  minHours, maxHours = min(hours), max(hours)
  hoursToFill = (len(days)*maxHours)-sum(hours)
  i = 0
  extraDaysI = 0
  hours, days = hour_sorted(days,hours)
  while hoursToFill > event[1] and i!=len(days)-1:
    diff = (hours[i]-hours[i+1])
    i+=1
    maxHours=hours[i]
    hoursToFill-=(len(days)-i)*diff
    extraDaysI = i
  if i==len(days)-1 and hoursToFill > 0.01:
    workdays[days[len(days)-1].toordinal()][clas+"_"+work][1] = float(event[1])
    for d in range(len(days)-1):
      workdays[days[d].toordinal()][clas+"_"+work][1] = 0.0
  else:
    dayAmplifiers = [ getDateAmplifier(days[d]) for d in range(len(days)) if d>=extraDaysI]
    dayAmplifier = mean(dayAmplifiers)
    dayHours = (event[1]-hoursToFill)/float(len(days)-extraDaysI)
    newHours = []
    s,s1,s2 = 0,0,0
    for d in range(len(days)):
      hour = (
        ( dayHours if d>=extraDaysI else 0.0)*getDateAmplifier(days[d])/dayAmplifier +
        ( maxHours-hours[d] if maxHours>hours[d] else 0.0))
      workdays[days[d].toordinal()][clas+"_"+work][1] = hour
      if hour>0:
        s+=hour
        s1+=dayHours if d>=extraDaysI else 0.0
        s2+=maxHours-hours[d] if maxHours>hours[d] else 0.0
        insort(newHours,[workdays[days[d].toordinal()][clas+"_"+work][1],d])
    if all([1==a for a in dayAmplifiers]):
      def prevent_inane_workdays(prev_sorted=False, mult=3):
        if not prev_sorted:
          newHours.sort()
        i=0
        maxtol = min(max(0.125*mult,event[1]*0.05*mult),0.25*mult)
        mintol = 0.1625*mult
        while i<len(newHours)-1:
          if (newHours[i+1][0]<maxtol and newHours[i+1][0]>newHours[i][0]) or newHours[i][0]<mintol:
            workdays[days[newHours[i][1]].toordinal()][clas+"_"+work][1] = min(newHours[i][0]+newHours[i+1][0],maxtol)
            workdays[days[newHours[i+1][1]].toordinal()][clas+"_"+work][1] = newHours[i][0]+newHours[i+1][0] - workdays[days[newHours[i][1]].toordinal()][clas+"_"+work][1]
            newHours[i][0] = workdays[days[newHours[i][1]].toordinal()][clas+"_"+work][1]
            newHours[i+1][0] = workdays[days[newHours[i+1][1]].toordinal()][clas+"_"+work][1]
          i+=1
        prevent_inane_workdays(True,2)
        # prevent_inane_workdays(2)
        # prevent_inane_workdays(2)
        # prevent_inane_workdays(1)
        prevent_inane_workdays(1)


def assess_event(clas,work,event):
  nDays = (event[0]-event[3]).days
  if nDays==1 or work=='today':
    workdays[(event[0]-relativedelta.relativedelta(days=1)).toordinal()][clas+"_"+work][1] = event[1]
  else:
    process_event(clas,work,event,nDays)

def clean_events():
  old_variance = calc_variance()
  eventsTemp = list(events.items())
  shuffle(eventsTemp)
  for clas,works in eventsTemp:
    worksTemp = list(works.items())
    shuffle(worksTemp)
    for work, asmts in worksTemp:
      for event in asmts:
        assess_event(clas,work,event)
  return abs(old_variance-calc_variance())/old_variance

def calc_variance():
  hours = [
    sum([
      hour[1] 
      for hour in works.values()])
    / getDateAmplifier(date.fromordinal(day)) 
    for day,works in workdays.items()]
  return float128(pvariance(hours))


def print_days():
  workedSoFar = {}
  for day in sorted(iter(workdays)):
    work = workdays[day]
    print(str(date.fromordinal(day))+": ")
    dayTot = 0.0
    strs = []
    for asmt,event in sorted(work.items(), key=(lambda z:z[0])):
      if event[1]>0.02:
        asmtArr = asmt.split('_')
        dayTot+=event[1]
        m=str(int((event[1]*60)%60))
        if len(m)==1:
          m='0'+m
        key = hash(asmt+'_'+str(event[0]))
        if key not in workedSoFar:
          workedSoFar[key] = 0.0
        workedSoFar[key] += event[1]
        p = round(100.0*workedSoFar[key]/events[asmtArr[0]][asmtArr[1]][event[0]][1])
        insort(strs,(asmt,event[1],"  "+str(int(event[1]))+':'+m+"\t"+'('+str(p)+'% done)'+'\t'+asmtArr[0]+" "+asmtArr[1]+" "+events[asmtArr[0]][asmtArr[1]][event[0]][2]))
    for s in strs:
      print(s[-1])
    m=str(int((dayTot*60)%60))
    if len(m)==1:
      m='0'+m
    print("Daily total hours of work at "+str(int(dayTot))+':'+m+'\n')

if any([arg in ['-h','--help'] for arg in sys.argv]):
  print('''Usage: 
    \n  python projects.py projects.csv
    \n  python projects.py [-]
    \n\nArgs:
    \n  filename.csv: csv file of projects to work on. Optional; can also use stdin instead (with or without the dash). See below for csv format.
    \n  -h, --help: Display this help message.
    \n  -a, --attempts number: Set the number of scheduling attempts (an integer) to perform before termination.
    \n  -d, --start-day YYYYMMDD: Set the start day to the Gregorian date.
    \n  -q, --quality variance min_hours: Set the scalar multiplier values for the two quality factors. More detailed quality factors comming soon.
    \n  -D, --day-amplifier dayfile.json: Set certain dates or days of the week to different amplifiers than 1.
    \n\nCSV file format: (object_type::description)
    \n  float::hours_estimate,int::month,int::day,string::class,string::project,string::assignment
    \n\nFor each class, for each 'project' for that class, you will have one assignment for that project being assigned to work on at any one time, so that no two assignments within one project type are being worked on at once, and that you only work on the one due most soon at any time.
    \n\ndayfile.json file format: { key:value,... } where each key is a YYYYMMDD or n (0-6 monday-sunday) and val is amplifier.
    \nComing soon: 
    \n  optional year parameter,
    \n  optional parameter multiple assignments per project to be worked on at once, so that a set of assignments can be finished before the next set of assignments is to be done. 
    \n  cleaned-up code,
    \n  better command-line arg for quality function customization,
    \n  *Comments demarcated by "#" at beginning of line, while block-comments are enclosed by /* ... */. Block comments will cause the entire line on which their start/end characters to be commented ''')
  exit(0)

i = getArgIndex('-a')+1
if i>0:
  maxAttempts = int(sys.argv[i])
else:
  maxAttempts = 32
i = getArgIndex('-q')+1
if i>0:
  varianceMultiplier = float(sys.argv[i])
  min_hoursMultiplier = float(sys.argv[i+1])
else:
  varianceMultiplier = 1.75
  min_hoursMultiplier = 1.0
i = getArgIndex('-d')+1
if i>0:
  y,m,d = int(sys.argv[i][:4]), int(sys.argv[i][4:6]), int(sys.argv[i][6:8])
  today = date(y,m,d)
else:
  today = date.today()
i = getArgIndex('-D')+1
if i>0:
  try:
    with open(sys.argv[i]) as data_file:    
        for key, value in json.load(data_file).items():
          if len(key)==1 and key.isdigit() and int(key)>=0 and int(key)<=6:
            date_amplifiers[int(key)]['default'] = float(value)
          elif len(key)==8 and key.isdigit():
            y,m,d = int(key[:4]), int(key[4:6]), int(key[6:8])
            aday = date(y,m,d)
            date_amplifiers[aday.weekday()][str(aday)] = float(value)
  except Exception as e:
    print(e, file=sys.stderr)

lines = [[y.strip().replace('_','') for y in x.split(',')] for x in sys.stdin.readlines() if len(x)>1 and x[0]!='#']
com = '/*'
for line in lines[:]:
  for thing in line:
    if com in thing:
      com = com[::-1]
  if com == '*/':
    lines.remove(line)
breaks = [[today,today]]

lines.sort(key=(lambda x: int(x[1])+(float(x[2])/30)))
for line in lines[:]:
  year = today.year if today.month<=int(line[1]) else (today+relativedelta.relativedelta(days=365)).year
  eventday = date(year, int(line[1]), int(line[2]))
  if eventday <= today:
    lines.remove(line)
  elif line[3] == 'break':
    if line[5] == 'start':
      breaks.append([eventday,None])
    else:
      breaks[-1][-1] = eventday
    lines.remove(line)
  else:
    if line[3] not in events:
      events[line[3]] = {}
    if line[4] not in events[line[3]]:
      events[line[3]][line[4]] = []
    events[line[3]][line[4]].append([
      eventday,
      float(line[0]) if line[0].strip('xde')==line[0] else line[0], 
      line[5]])
if breaks[-1][-1] is None:
  breaks.pop()
for line in lines:
  eventday = date(year, int(line[1]), int(line[2]))
  eventI = [i for i in range(len(events[line[3]][line[4]])) if events[line[3]][line[4]][i][2]==line[5]][0]
  minStartDay = max([e for s,e in breaks if e<eventday])
  startDay = (date(year,int(line[6]),int(line[7])) if len(line)>7 
    else (events[line[3]][line[4]][eventI-1][0]
    if eventI!=0 and line[4]!='today' 
    else (today if line[4]!='today' 
    else eventday-relativedelta.relativedelta(days=1))))
  if startDay < minStartDay:
    startDay = minStartDay
  days = populate_days(startDay,(eventday-startDay).days)
  dayAmplifier = mean([ getDateAmplifier(d) for d in days])
  for day in days:
    if day.toordinal() not in original_workdays:
      original_workdays[day.toordinal()] = {}
    original_workdays[day.toordinal()][line[3]+"_"+line[4]] = [
        eventI,
       float(line[0]) * getDateAmplifier(day) / float((eventday-startDay).days) / dayAmplifier]
  events[line[3]][line[4]][eventI].append(startDay)
attempts = 0
workdays_quality = inf
total_its=0
total_time = 0
while attempts<maxAttempts:
  attempts+=1
  workdays = deepcopy(original_workdays)
  its=0
  startTime = now()
  variance_loss=inf
  while its<max(5,maxAttempts/25) and now()-startTime<5 and variance_loss>10**(-4):
    variance_loss = clean_events()
    its+=1
  workdays_quality = (varianceMultiplier*calc_variance()
    -min_hoursMultiplier*min([min([v[1] for v in w.values() if v[1]>0]+[24]) for w in workdays.values()]))
  if best_workdays['quality']>workdays_quality:
    best_workdays['quality'] = workdays_quality
    best_workdays['last_variance_loss'] = variance_loss
    best_workdays['workdays'] = deepcopy(workdays)
  total_time+=now()-startTime
  total_its+=its
variance_loss = best_workdays['last_variance_loss']
workdays = best_workdays['workdays']
temp = sorted([sum([v[1] for v in w.values()]) for w in workdays.values()])
minM=str(int((temp[0]*60)%60))
if len(minM)==1:
  minM='0'+minM
maxM=str(int((temp[-1]*60)%60))
if len(maxM)==1:
  maxM='0'+maxM
pmeanT = sum(temp) / float(len(temp))
meanT = str(int((pmeanT*60)%60))
if len(meanT)==1:
  meanT='0'+meanT
pstdiv = pstdev(temp)
pminT = min([
  min([v[1] for v in w.values() if v[1]>0]+[24]) 
  for w in workdays.values()])
stddiv = str(int((pstdiv*60)%60))
minT = str(int(pminT*60)%60)
if len(minT)==1:
  minT='0'+minT  
if len(stddiv)==1:
  stddiv='0'+stddiv
print("Performed "+
  str(attempts)+
  " attempts totaling "+
  str(total_its)+
  " iterations over "+
  str(round(total_time,3))+" seconds")
if variance_loss>=10**(-2):
  print("Maxed out the number of iterations trying to converge.\nFor a more-optimal schedule, increase max iterations and runtime params.")
print("Min hours of "+
  str(int(temp[0]))+':'+minM+
  ", Max hours of "+
  str(int(temp[-1]))+':'+maxM+
  ", Mean hours of "+
  str(int(pmeanT))+':'+meanT+
  ",\nStandard Deviation of "+
  str(int(pstdiv))+':'+stddiv+
  ", Min time spent per thing of "+
  str(int(pminT))+':'+minT+'\n')
  
print_days()