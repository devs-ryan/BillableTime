#!/usr/local/bin/python3

#ignore warnings
import warnings
warnings.filterwarnings("ignore")

#imports
import PySimpleGUI as sg
from time import sleep
import datetime
import sys
import csv
import os

fileName = 'BillableHours.csv'

introText = """
 /$$$$$$$  /$$ /$$ /$$           /$$       /$$        
| $$__  $$|__/| $$| $$          | $$      | $$        
| $$  \ $$ /$$| $$| $$  /$$$$$$ | $$$$$$$ | $$  /$$$$$$
| $$$$$$$ | $$| $$| $$ |____  $$| $$__  $$| $$ /$$__  $$
| $$__  $$| $$| $$| $$  /$$$$$$$| $$  \ $$| $$| $$$$$$$$
| $$  \ $$| $$| $$| $$ /$$__  $$| $$  | $$| $$| $$_____/
| $$$$$$$/| $$| $$| $$|  $$$$$$$| $$$$$$$/| $$|  $$$$$$$
|_______/ |__/|__/|__/ \_______/|_______/ |__/ \_______/
                                                                                                              
    /$$$$$$$$ /$$                                  
   |__  $$__/|__/                                  
      | $$    /$$ /$$$$$$/$$$$   /$$$$$$   /$$$$$$ 
      | $$   | $$| $$_  $$_  $$ /$$__  $$ /$$__  $$
      | $$   | $$| $$ \ $$ \ $$| $$$$$$$$| $$  \__/
      | $$   | $$| $$ | $$ | $$| $$_____/| $$      
      | $$   | $$| $$ | $$ | $$|  $$$$$$$| $$      
      |__/   |__/|__/ |__/ |__/ \_______/|__/      
"""

print(introText)
total = 0

#get hourly rate
hourlyRate = input('What is your hourly rate: $')
try:
    hourlyRateInt = int(hourlyRate)
except ValueError:
    print('Error: Expecting integer.. ABORTING.')
    sys.exit()

#get output path
outputPath = input('Ouput path (Defaults to current directory): ')
if outputPath == '':
    outputPath = '.'

outputPath = outputPath + fileName if (outputPath[-1] == '/') else outputPath + '/' + fileName

#check if file exists and create if not
fileExists = False 
if os.path.isfile(outputPath) and os.access(outputPath, os.R_OK):
    fileExists = True
    f = open(outputPath, 'r+')
else:
    f = open(outputPath, 'w')

print('Info: Output path = ' + outputPath)
writer = csv.writer(f)

if fileExists:
    print('Info: Ouput file found, appending to existing results.')
    lines = f.readlines()
    header = True
    for line in lines:
        if header:
            header = False
            continue
        values = line.split(',')
        amount = float(values[-1].replace('\n', '').replace('$', ''))
        total += amount
else:
    print('Info: Ouput file missing, a new file will be created.')
    headers = ['Date', 'Description', 'Start Time', 'End Time', 'Total Time', 'Hourly Rate', 'Total Amount Billable']
    writer.writerow(headers)
    
#get starting task descriptuon
currentDesc = input('Starting task description: ')

#loading GUI message
print('Loading up the time tracker GUI', end="", flush=True)
for i in range(1, 5):
    print('.', end="", flush=True)
    sleep(.300)
print('\nLet\'s get it!!')


# set theme color
sg.theme('DarkBrown1')

#create layout
onButtonText = 'Start'
offButtonText = 'Stop'
layout = [
        [sg.Text('Controls:')],
        [sg.Button(onButtonText, size=(4,1), button_color=('black', 'green'), key='_TRACK-BUTTON-CLICK_'), sg.Button('Exit')],
        [sg.Text('Timer:', size=(6, 1), font=('Helvetica', 20)), sg.Text('00:00:00.00', size=(11, 1), font=('Helvetica', 20), key='_TIMER_')],
        [sg.Text('Hourly Rate:', size=(12, 1), font=('Helvetica', 20)), sg.Text('$' + hourlyRate, size=(4, 1), font=('Helvetica', 20))],
        [sg.Text('Task Description:')],
        [sg.Multiline(currentDesc, size=(38, 8), font=('Arial', 14), background_color='white', text_color='black', key='_TASK-DESCRIPTION_')],
        [sg.Button('Clear')],
        [sg.Text("Total Billable: ${:.2f}".format(round(total, 2)), key='_TOTAL_')]
    ]

window = sg.Window('Billable Time Tracker', layout, size=(270,350))

#init loop variables
tracking = False
timer_running = False
counter = 0

# function: updateTimer(counter)
def updateTimer(counter):
    timer = '{:02d}:{:02d}:{:02d}.{:02d}'.format((counter // 100) // 3600, ((counter // 100) % 3600) // 60, (counter // 100) % 60, counter % 100)
    window['_TIMER_'].update(timer)

# function: saveTime(counter)
def saveTime(counter):
    # global vars
    global total
    global currentDesc
    #write row
    if (counter // 100 < 600):
        counter = 60000
    now = datetime.datetime.now()
    start = now - datetime.timedelta(seconds=(counter // 100))
    timer = '{:02d}:{:02d}:{:02d}.{:02d}'.format((counter // 100) // 3600, ((counter // 100) % 3600) // 60, (counter // 100) % 60, counter % 100)
    rowTotal = round(float((counter // 100) / 3600) * float(hourlyRate), 2)
    row = [now.strftime("%d/%m/%Y"), currentDesc.rstrip() if currentDesc != '\n' else 'N/A', start.strftime("%H:%M:%S"), now.strftime("%H:%M:%S"), timer, '$' + str(hourlyRate), "${:.2f}".format(rowTotal)]
    total += rowTotal
    print('row:', row)
    print("Total Billable: ${:.2f}".format(round(total, 2)))
    writer.writerow(row)

# Event Loop---
while True:
    event, values = window.read(timeout=10)
    if event in (None, 'Exit'):
        if tracking == True:
            saveTime(counter)
        break
    if event in (None, 'Clear'):
        window.Element('_TASK-DESCRIPTION_').Update('')
        currentDesc = ''
    if event == '_TRACK-BUTTON-CLICK_':
        tracking = not tracking
        timer_running = not timer_running
        window.Element('_TRACK-BUTTON-CLICK_').Update((onButtonText,offButtonText)[tracking], button_color=(('black', ('red', 'green')[tracking])))
        currentDesc = values['_TASK-DESCRIPTION_']
        if tracking == False:
            saveTime(counter)
            window.Element('_TOTAL_').Update("Total Billable: ${:.2f}".format(round(total, 2)))
            counter = 0
    if timer_running:
        counter += 1
        updateTimer(counter)

f.close()
window.Close()