# projects_organizer
An organizer program that optimizes your work time

Usage: 
    
  python projects.py projects.csv
    
  python projects.py [-]
    

Args:
    
  filename.csv: csv file of projects to work on. Optional; can also use stdin instead (with or without the dash). See below for csv format.
    
  -h, --help: Display this help message.
    
  -a, --attempts number: Set the number of scheduling attempts (an integer) to perform before termination.
    
  -d, --start-day YYYYMMDD: Set the start day to the Gregorian date.
    
  -q, --quality variance min_hours: Set the scalar multiplier values for the two quality factors. More detailed quality factors comming soon.
    
  -D, --day-amplifier dayfile.json: Set certain dates or days of the week to different amplifiers than 1.
    

CSV file format: (object_type::description)
    
  float::hours_estimate,int::month,int::day,string::class,string::project,string::assignment
    

For each class, for each 'project' for that class, you will have one assignment for that project being assigned to work on at any one time, so that no two assignments within one project type are being worked on at once, and that you only work on the one due most soon at any time.
    

dayfile.json file format: { key:value,... } where each key is a YYYYMMDD or n (0-6 monday-sunday) and val is amplifier. See writeDates.py for more info.
    
Coming soon (some of these are already implemented): 
    
  optional year parameter,
    
  optional parameter multiple assignments per project to be worked on at once, so that a set of assignments can be finished before the next set of assignments is to be done. 
    
  cleaned-up code,
    
  better command-line arg for quality function customization,
    
  *Comments demarcated by "#" at beginning of line, while block-comments are enclosed by /* ... */. Block comments will cause the entire line on which their start/end characters to be commented 
