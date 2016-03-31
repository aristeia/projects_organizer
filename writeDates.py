import json
from sys import argv

# This file will write a 'dates.json' (or other file name, if specified in first cmd arg)
#   for projects.py to read in via the -D parameter
#
# The purpose of a dates.json is to weight how much work you want to do on certain types
#   of dates differently, based on either (1) the day of the week or (2) the date.
# If a specific date is found in this json file, projects.py will use that date's weight,
#   otherwise, if the date's weekday is found, projects.py will use that weekday's weight,
#   otherwise use 1 by default.
#
# Keys for weekdays are the integer 0-6 representing Monday-Sunday (just like date.weekday())
# Keys for dates are YYYYMMDD for year, month, and day
# Values are rational numbers GREATER THAN ZERO, such that, for a value X, you will work X 
#   times more than usual for a usual workload, hence, make this number less than 1 for 
#   days where you'd like to work less than usual, and greater than 1 for more than usual
# For now, if you don't want to work on a day, use a very small positive weight like 0.01

dates = { #fill these in with your own values

  0:0.875,          # work a little less on Mondays
  1:1,              # work standard load on Tuesdays
  2:1.2,            # work extra on Wednesdays
  3:1.5,            # work like a weekend on Thursdays
  4:1.25,           # work a little extra Fridays
  5:1.5,            # work all day erryday Saturdays
  6:1.5,            # no sabbath for Sims Sundays
  20160408:0.1,     # Taking the day off
  20160409:0.333,   # Taking the day mostly off
  20160504:0.1,     # 21st birthday...
  20160505:0.1,     # Schoolwide music festival in Vantage, Washington
  20160506:1.375,   # Getting ready for finals
  20160507:1.75,    # Getting REALLY ready for finals
  20160508:1.75,    # Getting REALLY ready for finals
  20160509:1.75,    # Getting REALLY ready for finals
  20160510:1.75,    # Getting REALLY ready for finals
  20160511:1.75,    # Getting REALLY ready for finals
  20160512:1.75,    # Getting REALLY ready for finals
}

with open('dates.json' if len(argv)==1 else argv[1], 'w') as f:
  json.dump(dates,f) 