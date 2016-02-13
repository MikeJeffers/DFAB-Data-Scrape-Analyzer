'''
15-112 TermProject
Created on Mar 4, 2014
Last Update: April 30, 2014

@author: mjeffers, Section P
@Mentor: Rokhini 
'''

import urllib2
import string
import threading
import Queue
import random
import copy
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
from Tkinter import *


##################GLOBALS############################


MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

# TODO this list is incomplete and unordered...
EQUIP = ['1.equipmentappointments-e.vacuumformer(max1hr)',
         '1.equipmentappointments-h.plaster3dprinter(queue)',
         '1.equipmentappointments-i.plastic3dprinter(queue)',
         '1.equipmentappointments-b.lasersystem1(max1hr)',
         '1.equipmentappointments-c.lasersystem2(max1hr)',
         '1.equipmentappointments-d.3-axiscncrouter(max3hrs)',
         '1.equipmentappointments-f.abbirb-4400(max6hrs)',
         '1.equipmentappointments-g.abbirb-6640(max6hrs)',
         '2.officeappointments-1.p.zachali',
         '2.officeappointments-2.mikejeffers',
         '3.afterappointments-cncrouter',
         '3.afterappointments-lasersystem1',
         '3.afterappointments-lasersystem2',
         '3.afterappointments-roboticcell(large)',
         '4.dfabschedule-a.ofoperation',
         '4.dfabschedule-b.openingshift',
         '4.dfabschedule-c.mid-shift',
         '4.dfabschedule-d.closingshift']

RE_EQUIP = ['1e.VacuumFormer',
         '1h.Plaster3DPrinter',
         '1i.Plastic3DPrinter',
         '1b.Laser1',
         '1c.Laser2',
         '1d.3-axis CNC',
         '1f.ABB IRB-4400',
         '1g.ABB IRB-6640',
         '2a.OH: Zach Ali',
         '2b.OH: Mike Jeffers',
         '3.3-axis CNC',
         '3.Laser1',
         '3.Laser2',
         '3.Robots',
         '4.a.ofoperation',
         '4.b.openingshift',
         '4.c.mid-shift',
         '4.d.closingshift']

DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

# Lets define a deadline as any time unit that has a peak of hours booked
# Peak is above average by some stdDev
# The timeunit preceding is also high, but not higher
# the time unit after is very low
ATTRIBS_OF_DEADLINE = {}

##############UI CLASS####################

class userInterface(object):
    def __init__(self, entryDictList=[], modeList=[], phase=0, progressPointer=[]):
        self.root = Tk()
        self.width = 800
        self.height = 600
        self.root.bind("<Button-1>", self.mousePressed)
        self.root.bind("<Key>", self.keyPressed)
        self.canvas = Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()
        self.phase = phase
        self.running = False
        self.userInput = "all"
        self.userInputInt = "30"
        self.userCategory = ""
        self.userEntryMode = False
        self.mod = self.width / 8
        self.progress = progressPointer
        self.titleFont = ('helvetica', 18)
        self.contentFont = ('helvetica', 9)
        self.helpFont = ('helvetica', 7)
        self.count = 0
        self.background = "#%02x%02x%02x" % (222, 222, 222)
        self.red = "#%02x%02x%02x" % (245, 15, 5)
        self.green = "#%02x%02x%02x" % (15, 245, 15)
        self.cyan = "#%02x%02x%02x" % (0, 245, 196)
        self.gray = "#%02x%02x%02x" % (190, 190, 190)
        if(phase == 1):
            self.plotMode = True
            self.entryList = entryDictList
            self.modes = modeList
            self.btWidth = self.width / len(self.modes)
            self.btHeight = self.height / 8
            self.btPressed = [False] * len(self.modes)

    def mousePressed(self, event):
        if(self.phase == 0):
            self.p0MousePressed(event)
        elif(self.phase == 1):
            self.p1MousePressed(event)
        (x, y, x2, y2) = (self.width - self.mod, 0, self.width, self.mod / 2)
        if(event.x > x and event.x < x2):
            if(event.y > y and event.y < y2):
                self.quitSelf()
        self.redrawAll()

    def p0MousePressed(self, event):
        (x, y, x2, y2) = (self.width * 0.75, self.height * 0.75, self.width * 0.75 + self.mod, self.height * 0.75 + self.mod)
        if(event.y > y and event.y < y2):
            if(event.x > x and event.x < x2):
                print "clicked run button"
                self.running = True
                self.redrawAll()
                numOfentries = int(self.userInputInt)
                t = threading.Thread(target=getNewEntries, args=[numOfentries])
                t.daemon = True
                t.start()

    def p1MousePressed(self, event):
        (x, y, x2, y2) = (self.mod / 2, self.mod / 2, self.mod * 2, self.mod)
        if(event.y > (self.height - self.btHeight)):
            for i in xrange(len(self.modes)):
                if(event.x > (self.btWidth * i) and event.x < (self.btWidth * (i + 1))):
                    self.btPressed = [False] * len(self.modes)
                    self.btPressed[i] = True
                    self.userCategory = self.modes[i]
        elif(event.x > x and event.x < x2):
            for i in xrange(4):
                (y, y2) = (self.mod * (i + 0.5), self.mod * (i + 1))
                if(event.y < y2 and event.y > y):
                    if(i == 0):
                        self.userEntryMode = not self.userEntryMode
                    elif(i == 1):
                        self.plotMode = not self.plotMode
                    else:
                        presetPlotBy(i - 1, self.entryList)

    def p0KeyPressed(self, event):
        if(event.keysym in ["BackSpace", "Delete"]):
                self.userInputInt = str(self.userInputInt)[:len(str(self.userInputInt)) - 1]
        elif(event.keysym in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                self.userInputInt += event.keysym
        if(event.keysym == "Return"):
            numOfEntries = 0
            try:
                numOfEntries = int(self.userInputInt)
            except:
                print "userinputTime not valid integer!"
                self.userInputInt = ""
            self.userInputInt = numOfEntries
            if( numOfEntries > 0 and numOfEntries < 2000):
                print "Submitted number"
                if(not self.running):
                    getNewEntries(numOfEntries)
                    self.running = True
            elif( numOfEntries > 2000):
                self.userInputInt=2000
            elif(numOfEntries<0):
                self.userInputInt = 1
            else:
                print "Something awful happened"
            print "entry submission"
            


    def p1KeyPressed(self, event):
        if(self.userEntryMode):
            if(event.keysym in ["BackSpace", "Delete"]):
                self.userInput = self.userInput[:len(self.userInput) - 1]
            elif(event.keysym == "space"):
                self.userInput += " "
            elif(event.keysym != "Return"):
                self.userInput += event.keysym
        else:
            if(event.keysym in ["BackSpace", "Delete"]):
                self.userInputInt = str(self.userInputInt)[:len(str(self.userInputInt)) - 1]
            elif(event.keysym in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                self.userInputInt += event.keysym
        if(event.keysym == "Return"):
            try:
                self.userInputInt = int(self.userInputInt)
            except:
                print "userinputTime not valid integer!"
            if(self.userCategory != "" and self.userInput != "" and type(int(self.userInputInt)) == int):
                if(self.plotMode):
                    makePlotWithCategory(self.userCategory, int(self.userInputInt), self.entryList)
                else:
                    makePlotBy(self.userInput, self.userCategory, int(self.userInputInt), self.entryList)
            else:
                print "Category not selected!", "Or no userinput found!"
            print "entry submission"
            self.userInput = ""
            self.userInputInt = ""

    def keyPressed(self, event):
        if(self.phase == 0):
            self.p0KeyPressed(event)
        elif(self.phase == 1):
            self.p1KeyPressed(event)
        self.redrawAll()

    ##################p1##################
    def drawPresets(self):
        for i in xrange(1, 3):
            if(i == 1):
                s = "Plot All by Year"
            elif(i == 2):
                s = "Plot All by Month"
            (x, y, x2, y2) = (self.mod * 0.5, self.mod * (i + 1.5), self.mod * 2, self.mod * (i + 2))
            self.canvas.create_rectangle(x, y, x2, y2, fill=self.cyan)
            self.canvas.create_text((x + x2) / 2, (y + y2) / 2, text=s, font=self.contentFont)

    def drawHelp1(self):
        helpText = """
        This window allows you to create and view plots of various types.
        Please use the Toggle to input either a 'Keyword' or 'TimeUnit'.
        'Time-unit' will determine the resolution in # of days of the bar graph.
        'Keyword' is the character pattern to search for and will plot only entries containing the key.
        You may see 'ALL' entries, by typing 'all' into the keyword search.
        Select the appropriate 'category' below to search within.
        Hit ENTER to RUN using the current input.
        """
        self.canvas.create_text(self.mod * 0.1, self.height - self.btHeight, text=helpText, anchor='sw', font=self.helpFont)

    def drawButtons(self):
        for i in xrange(len(self.modes)):
            if(self.btPressed[i]):
                tempColor = self.green
            else:
                tempColor = self.red
            self.canvas.create_rectangle(self.btWidth * i, self.height - self.btHeight, self.btWidth * (i + 1), self.height, fill=tempColor)
            self.canvas.create_text(self.btWidth * (i + 0.5), self.height - (self.btHeight / 2), text=str(self.modes[i]), font=self.contentFont)


    def drawPlotToggle(self):
        if(self.plotMode):
            tempColor = self.green
            entryMode = "Category Breakdown"
        else:
            tempColor = self.red
            entryMode = "DeadLine Detection"
        (x, y, x2, y2) = (self.mod * 0.5, self.mod * (1.5), self.mod * 2, self.mod * (2))
        self.canvas.create_rectangle(x, y, x2, y2, fill=tempColor)
        self.canvas.create_text(x, (y + y2) / 2, text="Plot Mode: " + entryMode, anchor="w", font=self.contentFont)

    def drawToggle(self):
        if(self.userEntryMode):
            tempColor = self.green
            entryMode = "Keyword"
        else:
            tempColor = self.red
            entryMode = "TimeUnit"
        (x, y, x2, y2) = (self.mod / 2, self.mod / 2, self.mod * 2, self.mod)
        self.canvas.create_rectangle(x, y, x2, y2, fill=tempColor)
        self.canvas.create_text(x, (y + y2) / 2, text="Input Mode Toggle: " + entryMode, anchor="w", font=self.contentFont)

    def drawCategories(self):
        self.canvas.create_text(self.width / 2, self.height / 2, text="Select a category to plot by: \n Current selection: " + self.userCategory, font=self.contentFont)
        self.canvas.create_text(self.width / 2, self.height / 4, text="Type in data to display by:", font=self.contentFont)
        self.canvas.create_text(self.width / 2, self.height / 3, text=self.userInput + " per " + str(self.userInputInt) + " # of Days", font=self.contentFont)
    ###########################P0#################

    def drawTitle(self):
        self.canvas.create_text(self.width / 2, self.mod * 0.1, text="DFAB RESERVATION DATA \n VISUALIZATION AND ANALYSIS", anchor='n', font=self.titleFont)

    def drawHelp0(self):
        helpText = """
        Welcome to the Dfab Reservation System Web-scraping and Analysis Application
        This window allows you to Live-scrape the Reservation Server and 
        build a local File log of as many Entries as you choose.
        If you are starting from scratch, you will need to run this many times, 
        as the server has 50,000+ entries, and you may only scrape between 1-2000 at a time.
        This will prevent Server-side failures which may interrupt typical usage.
        Click 'Run' to execute a round of scraping.  Entries retrieved will be 
        appended to the local File for later processes.
        If you have run this before, or are done scraping, 
        you may click "Done" to begin Data-Visualization and Analysis.
        """
        self.canvas.create_text(self.mod * 0.1, self.mod, text=helpText, anchor='nw', font=self.helpFont)

    def drawRunButton(self):
        (x, y, x2, y2) = (self.width * 0.75, self.height * 0.75, self.width * 0.75 + self.mod, self.height * 0.75 + self.mod)
        self.canvas.create_rectangle(x, y, x2, y2, fill=self.red)
        self.canvas.create_text((x + x2) / 2, (y + y2) / 2, text="RUN", font=self.titleFont)

    def drawProgressBar(self):
        (x, y, x2, y2) = (self.mod * 0.5, self.height - self.mod, self.width * 0.75, self.height - self.mod / 2)
        self.canvas.create_rectangle(x, y, x2, y2, fill=self.gray)
        if(self.running):
            self.count += 1
            self.count = self.count % 10
            self.userInputInt = int(self.userInputInt)
            prog = (1.0 * len(self.progress)) / (self.userInputInt + 2)
            self.canvas.create_rectangle(x, y, ((x2 - x) * prog) + x, y2, fill=self.red)
            dots = "."*self.count
            self.canvas.create_text((x + x2) / 2, (y + y2) / 2, text=dots + "Please Wait: Processing Entries" + dots, font=self.contentFont)
            if(1 in self.progress):
                self.running = False
                clearProgress()

    def drawURLBox(self):
        (x, y, x2, y2) = (self.width * 0.75, self.height / 2, self.width * 0.75 + self.mod, self.height / 2 + self.mod)
        self.canvas.create_rectangle(x, y, x2, y2, fill=self.gray)
        self.canvas.create_text((x + x2) / 2, y, text="URL Pull Requests per run:", anchor="s", font=self.contentFont)
        self.canvas.create_text((x + x2) / 2, (y + y2) / 2, text=self.userInputInt, font=self.titleFont)

    def drawQuit(self):
        (x, y, x2, y2) = (self.width - self.mod, 5, self.width, self.mod / 2)
        self.canvas.create_rectangle(x, y, x2, y2, fill=self.green)
        self.canvas.create_text((x + x2) / 2, (y + y2) / 2, text="DONE", font=self.titleFont)
    
    def drawBackground(self):
        self.canvas.create_rectangle(-5, -5, self.width+5, self.height+5, fill=self.background)

    def redrawAll(self):
        self.canvas.delete(ALL)
        self.drawBackground()
        self.drawQuit()
        if(self.phase == 1):
            self.drawPlotToggle()
            self.drawPresets()
            self.drawToggle()
            self.drawButtons()
            self.drawCategories()
            self.drawHelp1()
        elif(self.phase == 0):
            self.drawURLBox()
            self.drawRunButton()
            self.drawTitle()
            self.drawHelp0()
            self.drawProgressBar()

    def quitSelf(self):
        self.root.quit()
        self.root.destroy()

    def timerFired(self):
        self.redrawAll()
        delay = 100
        self.canvas.after(delay, self.timerFired)

    def run(self):
        self.timerFired()
        self.root.mainloop()


##################ENTRY DICT REFORMATTING##########################


def reFormatContent(entryList):
    for d in entryList:
        for key in d:
            for i in xrange(len(EQUIP)):
                if(d[key] == EQUIP[i]):
                    d[key] = d[key].replace(EQUIP[i], RE_EQUIP[i])
            d[key] = d[key].replace('hours', '')
            d[key] = d[key].replace('30minutes', '0.5')
            d[key] = d[key].replace('days', '')
            if(key.find("time") != -1):
                for i in xrange(len(DAYS)):
                    d[key] = d[key].replace(DAYS[i], "(" + str(i) + ')*')
            for i in xrange(len(MONTHS)):
                d[key] = d[key].replace(MONTHS[i], "/%02d/" % (i + 1))
    entryList = swapDateFormat(entryList)
    return entryList

def swapDateFormat(entryList):
    for d in entryList:
        for key in d:
            if(key.find("time") != -1):
                i = d[key].find('*')
                if(i != -1):
                    s = d[key]
                    timeStr = s[:i + 1]
                    date = s[i + 1:]
                    spliStr = date.split('/')
                    year = spliStr[2]
                    month = spliStr[1]
                    day = spliStr[0]
                    d[key] = timeStr + year + "/" + month + "/" + day
    return entryList

################FOR FILE I/O#########################
def dictToString(entryList):
    s = ""
    for d in entryList:
        idString = ""
        otherKeys = ""
        for key in d:
            if(key == "ID"):
                # This MUST match the ExtractIDs() function
                idString = str(key) + "#" + str(d[key]) + ";"
            elif(key in["description", "repeatenddate", "repeattype", "repeatday"]):
                continue
            else:
                otherKeys += str(key) + "<" + str(d[key]) + ">;"
        s += idString + otherKeys
        s += "\n"
    return s

def fileStringToDict(contents):
    if(contents == None):
        return []
    dictList = []
    for line in contents.splitlines():
        d = {}
        for sub in line.split(";"):
            if(sub.find("ID#") != -1):
                d["ID"] = sub[sub.find("#") + 1:]
            else:
                index = sub.find("<")
                if(index != -1):
                    titleKey = sub[:index]
                    data = sub[index + 1:].replace(">", "")
                    d[titleKey] = data
        dictList.append(d)
    return dictList

def getEntryFile():
    try:
        fileObj = open("C:\\Users\\Mike\\Documents\\_DFAB_SCRAPE_LOG\\entryFile.txt", "rt")
        return fileObj.read()
    except:
        return None


def writeEntryFile(contents):
    try:
        fileObj = open("C:\\Users\\Mike\\Documents\\_DFAB_SCRAPE_LOG\\entryFile.txt", "a+")
        fileObj.write(contents)
        return "success!"
    except:
        return "Failure"


def extractIDs(content):
    if(content == None):
        return []
    idList = []
    for line in content.split("\n"):
        if(line.find("URLFAILED") != -1):
            continue
        # NOTE: exact formatting depends on the dictToString() Function!!
        start = line.find("#")  # TODO Check these with current writing protocols
        end = line.find(";")
        if(start != -1 and end != -1):
            idList.append(line[start + 1:end])
    return idList


####################DRAW FUNCTIONS#########################################

##############ANIMATION-BASED UI PLOT FUNCTION###########

def makePlotBy(userInput, userCategory, userTimeUnit, entryList):
    userInput = userInput.lower()
    if(userInput == "all"):
        userInput = "m"
        userCategory = 'starttime'

    timeList = getArbitraryTimeUnit(entryList, userTimeUnit)
    byCategory = [0] * len(timeList)
    for entry in entryList:
        if(entry[userCategory].lower().find(userInput) != -1):
            entryTUdate = getTUdate(entry, userTimeUnit)
            if(isEntryToIgnore(entry)):
                for i in xrange(len(timeList)):
                    if(entryTUdate == timeList[i]):
                        byCategory[i] += float(entry['duration'])

    (begin, end) = trimListByData(timeList, byCategory)
    truncTimeList = timeList[begin:end + 1]
    truncbyKey = byCategory[begin:end + 1]

    truncTimeList = sorted(truncTimeList, cmp=compareDateStrs)
    dateFromDays = []
    for i in xrange(len(truncTimeList)):
        year = int(truncTimeList[i].split("/")[0])
        dayIncr = int(truncTimeList[i].split("/")[1]) * userTimeUnit
        dateFromDays.append(convertDayNumToDate(dayIncr, year))
    probOfDeadline = findDeadlines(truncbyKey, truncTimeList)

    colorList = colorByFactor(probOfDeadline)

    if(userInput == "m" and userCategory == 'starttime'):
        userInput = "Reserved"
        userCategory = 'All Categories'

    xLabel = "t = " + str(userTimeUnit) + " # of Days"
    yLabel = userInput + " in " + userCategory + "\n" + "Hours Reserved"
    titleLabel = userInput + " in " + userCategory + " Hours by " + str(userTimeUnit) + " # of Days"

    plotBar(dateFromDays, truncbyKey, colorList, xLabel, yLabel, titleLabel, probability=probOfDeadline)


#######PRESETS########
def presetPlotBy(index, entryList):
    if(index == 1):
        TU = getYearList(entryList)
    elif(index == 2):
        TU = getMonthsList(entryList)
    plotByPresetTimeUnit(TU, entryList, index)

def plotByPresetTimeUnit(byTimeUnit, entryDictList, timeUnit=1):
    # timeUnit 1=year, 2=month 3=day ### not so great, should revise
    if(timeUnit == 1):
        TU = "Year"
    elif(timeUnit == 2):
        TU = "Month"
    hoursPerTU = [0] * len(byTimeUnit)
    for entry in entryDictList:
        s = entry['starttime']
        s = s[s.find('*') + 1:]
        dateSplit = s.split("/")
        date = ""
        for i in xrange(timeUnit):
            date += dateSplit[i] + "/"
        date = date[:len(date) - 1]
        for i in xrange(len(byTimeUnit)):
            if(date == byTimeUnit[i] and isEntryToIgnore(entry)):
                hoursPerTU[i] += float(entry['duration'])
    probOfDeadline = findDeadlines(hoursPerTU, byTimeUnit)

    colorList = colorByFactor(probOfDeadline)
    xLabel = "t = " + TU
    yLabel = "Hours Reserved"
    titleLabel = "Hours Reserved every " + TU
    plotBar(byTimeUnit, hoursPerTU, colorList, xLabel, yLabel, titleLabel, probability=probOfDeadline)


#########TABLE ByEquip##################

def makePlotWithCategory(userCategory, userTimeUnit, entryDictList):
    xLabel = "TimeInterval = " + str(userTimeUnit)+ " Days"
    yLabel = "Hours Reserved"
    titleLabel = "Hours Reserved every " + str(userTimeUnit)+ " Days with Categorical Breakdown"
    byCategory = getUniqueItemsOfCategory(userCategory, entryDictList)
    timeList = getArbitraryTimeUnit(entryDictList, userTimeUnit)

    byCategory = getSortedByHours(byCategory, entryDictList, userCategory)
    print byCategory
    hoursByCategory = []
    for i in xrange(len(timeList)):
        hoursByCategory.append([0] * len(byCategory))

    for entry in entryDictList:
        entryTUdate = getTUdate(entry, userTimeUnit)
        if(isEntryToIgnore(entry)):
            for i in xrange(len(timeList)):
                if(entryTUdate == timeList[i]):
                    for j in xrange(len(byCategory)):
                        if(byCategory[j] == entry[userCategory]):
                            hoursByCategory[i][j] += float(entry['duration'])

    colorList = []
    for i in xrange(len(byCategory)):
        colorFactor = ((1.0 * i) / len(byCategory))
        rgbCol = (colorFactor**0.3, (1.0 * colorFactor), 1.0 / (1.0 + i**1.5))
        colorList.append(rgbCol)

    if(userCategory=="createdby"):
        newArrayByTime = []
        for i in xrange(len(byCategory)):
            row = []
            for j in xrange(len(timeList)):
                row.append(hoursByCategory[j][i] + sumOfPrevious(hoursByCategory[j], i))
            newArrayByTime.append(row)
    
        timeArray = [x for x in xrange(len(timeList))]
        for i in xrange(len(byCategory) - 1, -1, -1):
            plt.fill_between(timeArray, 0, newArrayByTime[i], facecolor=colorList[i], alpha=0.5, linewidth=0.0)
    
    else:
        for i in xrange(len(timeList)):
            for j in xrange(len(byCategory)):
                top = hoursByCategory[i][j]
                btm = sumOfPrevious(hoursByCategory[i], j)
                rgbCol = colorList[j]
                plt.bar(i, top, 0.8, bottom=btm, color=rgbCol, alpha=0.8)
    dateFromDays = []
    for i in xrange(len(timeList)):
        year = int(timeList[i].split("/")[0])
        dayIncr = int(timeList[i].split("/")[1]) * userTimeUnit
        dateFromDays.append(convertDayNumToDate(dayIncr, year))

    plt.xticks(xrange(0, len(timeList)), dateFromDays, rotation=35, size=7, va='top', ha='right')
    for j in xrange(len(byCategory)):
        plt.bar(0, 0, color=colorList[j], alpha=0.8, label=byCategory[j])
    plt.legend(title=userCategory + ":", loc=0, fontsize=8)
    
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(titleLabel)
    plt.tight_layout(1.01, 1, 1)
    plt.show()


def getUniqueItemsOfCategory(userCategory, entryDictList):
    byCategory = []
    for entry in entryDictList:
        if(isEntryToIgnore(entry)):
            byCategory.append(entry[userCategory])
    return sorted(list(set(byCategory)))  # get unique instances of each item

def getSortedByHours(byCategory, entryDictList, categoryKey):
    byCategoryHourSum = [0] * (len(byCategory))
    for entry in entryDictList:
        if(isEntryToIgnore(entry)):
            for j in xrange(len(byCategory)):
                if(byCategory[j] == entry[categoryKey]):
                    byCategoryHourSum[j] += float(entry['duration'])
    zippedCate = zip(byCategoryHourSum, byCategory)
    zippedCate = sorted(zippedCate, cmp=lambda x, y: cmp(y[0], x[0]))
    print zippedCate
    sortedCategories = []
    for pair in zippedCate:
        sortedCategories.append(pair[1])
    return sortedCategories

def isEntryToIgnore(entry):
    # boolean if entry is 'closed' hours or for Scheduling (category4)
    return (entry['type'] != 'closed' and entry['equipment'].find("4.") == -1)

def getTUdate(dictOfEntry, timeUnit):
    content = dictOfEntry['starttime']
    content = content[content.find('*') + 1:]
    year = content.split("/")[0]
    daysSince = sumNumberOfDays(content)
    timeUnitSince = daysSince / timeUnit
    TUDate = year + "/%03d" % (timeUnitSince)
    return TUDate

def trimListByData(L, data):
    # get Cropping indicies for 2 lists based on data
    startIndex = 0
    endIndex = len(L)
    for i in xrange(len(L)):
        if (data[i] != 0):
            startIndex = i
            break
    for i in xrange(len(L), -1):
        if (data[i] != 0):
            endIndex = i
            break
    return(startIndex, endIndex)

def colorByFactor(values):
    # Create matplotLib compatible RGB based on array of floats 0.0-1.0
    maxValue = max(values)
    colorList = []
    for i in xrange(len(values)):
        factor = round(values[i] / maxValue, 1)
        colorList.append((1.0 * factor, 1.0 / (factor + 1.1), 1.0 * factor))
    return colorList


def plotBar(xVals, yVals, colorList, xLabel="", yLabel="", titleLabel="", probability=[]):
    if(len(probability) == len(xVals)):
        titleLabel += " with Probability of DeadLine Occurrence"
        textBox = ""
        for i in xrange(len(probability)):
            prob = probability[i]
            if(prob > 0.01):
                txt = "%d%%" % (prob * 100)
                plt.text(i, yVals[i], txt, fontsize=8, ha='left', va='bottom')
                if(prob>0.49):
                    textBox+="%d%%" % (prob * 100)
                    textBox+=", " + xVals[i]+"\n"
        plt.text(0.5, max(yVals)*0.5, textBox, fontsize=8, bbox=dict(lw=1.0, facecolor=(0.9, 0.9, 0.9), alpha=0.5))
    plt.bar(xrange(0, len(xVals)), yVals, color=colorList, alpha=0.9)
    plt.xticks(xrange(0, len(xVals)), xVals, rotation=35, size=7, va='top', ha='right')
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(titleLabel)
    plt.tight_layout(1.01)
    plt.show()

###################TIME UNIT HELPERS#####################

def daysPerMonth(month, year):
    # MONTH IS 1-BASED!! Jan=1
    if(month in [4, 6, 9, 11]):
        return 30
    elif(month == 2):
        if(year % 4 == 0):
            return 29
        return 28
    else:
        return 31

def sumNumberOfDays(dateStr):
    dateSplit = dateStr.split("/")
    year = dateSplit[0]
    month = dateSplit[1]
    day = dateSplit[2]
    sumDays = 0
    for i in xrange(1, int(month)):
        sumDays += daysPerMonth(i, int(year))
    sumDays += int(day)
    return sumDays

def convertDayNumToDate(dayNumber, year):
    daySum = dayNumber
    i = 0
    while daySum >= 0:
        daySum -= daysPerMonth(i + 1, year)
        i += 1
    dayOfMonth = daySum + daysPerMonth(i, year)
    dateStr = "%s %d %d" % (MONTHS[(i - 1) % len(MONTHS)], dayOfMonth + 1, year)
    return dateStr

def getYearList(entryDictList):
    allYears = []
    for entry in entryDictList:
        if(entry['type'] != 'closed'):
            s = entry['starttime']
            s = s[s.find('*') + 1:]
            dateList = s.split("/")
            year = dateList[0]
            allYears.append(year)
    return sorted(list(set(allYears)), cmp=compareDateStrs)

def getMonthsList(entryDictList):
    byMonth = []
    for entry in entryDictList:
        if(entry['type'] != 'closed'):
            s = entry['starttime']
            s = s[s.find('*') + 1:]
            month = s.split("/")[0] + "/" + s.split("/")[1]
            byMonth.append(month)
    return sorted(list(set(byMonth)), cmp=compareDateStrs)

def getDayList(entryDictList):
    allDays = []
    for entry in entryDictList:
        if(entry['type'] != 'closed'):
            s = entry['starttime']
            s = s[s.find('*') + 1:]
            allDays.append(s)
    return sorted(list(set(allDays)), cmp=compareDateStrs)

def getArbitraryTimeUnit(entryDictList, numOfDays):
    byNumOfDays = []
    for entry in entryDictList:
        if(entry['type'] != 'closed'):
            s = entry['starttime']
            s = s[s.find('*') + 1:]
            year = s.split("/")[0]
            daysSince = sumNumberOfDays(s)
            timeUnitSince = daysSince / numOfDays
            yearAndTU = year + "/%03d" % (timeUnitSince)
            byNumOfDays.append(yearAndTU)
    return sorted(list(set(byNumOfDays)), cmp=compareDateStrs)

def compareDateStrs(x, y):
    return int(x.replace("/", "")) - int(y.replace("/", ""))


###########################NAIVE-BAYES HALFASS IMPLEMENTATION################3

def findDeadlines(dataSet, timeIntervalList):
    trainDeadLineClassification()
    for i in xrange(len(dataSet)):
        dataSet[i] += 0.1
    # extract peaks, hardline criteria for DL
    peaks = findPeaks(dataSet)
    # print peaks
    dictListOfSuspects = detectByFeatures(dataSet, peaks, ATTRIBS_OF_DEADLINE)
    scores = [0] * len(dataSet)
    peaksOnly = []
    for d in dictListOfSuspects:
        i = d["ID"]
        score = 1
        score *= abs(d["preRelD"])
        score *= abs(d["SD_ofDL"])
        score *= abs(d["SDofFallOff"])
        peaksOnly.append(score)
        scores[i] = score**0.01
    maxScore = max(peaksOnly)
    minScore = min(peaksOnly)
    aveScore = getMean(peaksOnly)
    SDofScore = getStdDev(peaksOnly, aveScore)
    print "maxScore", maxScore
    print "minScore", minScore
    print "aveScore", aveScore
    print "SDofScore", SDofScore
    return scores


def findPeaks(data):
    marks = [0]
    for i in xrange(1, len(data) - 1):
        if(data[i - 1] < data[i]and data[i] > data[i + 1]):
            marks.append(1)
        else:
            marks.append(0)
    marks.append(0)
    return marks

def detectByFeatures(data, guesses, dictOfFeatures):
    # gets Difference for each feature, returns as dict of feature differences
    ave = getMean(data)
    stdDev = getStdDev(data, ave)

    preRelD_diffList = []
    SD_ofDL_diffList = []
    SDofFallOff_diffList = []

    listOfFeatureDicts = []
    previousMark = 0
    for i in xrange(2, len(data) - 1):
        if(guesses[i] == 1):
            # get data from current DL to previous, pre-deadline behaviours
            dataPreceding = data[previousMark + 1:i]
            aveOfPre = getMean(dataPreceding)
            SDOfPre = getStdDev(dataPreceding, ave)
            # get relative measures of pre- features to match against
            # relative features
            relativeSDdiff = ((data[i] * 1.0) - aveOfPre) / SDOfPre
            # global features
            globalSDdiff = ((data[i] * 1.0) - ave) / stdDev
            # Fall-off features
            globalSDofFallOff = ((data[i + 1] * 1.0) - ave) / stdDev
            currentFeatures = {}
            currentFeatures["ID"] = i
            preRelD_diffList.append(relativeSDdiff - ATTRIBS_OF_DEADLINE["preRelD"])
            SD_ofDL_diffList.append(globalSDdiff - ATTRIBS_OF_DEADLINE["SD_ofDL"])
            SDofFallOff_diffList.append(globalSDofFallOff - ATTRIBS_OF_DEADLINE["SDofFallOff"])

            currentFeatures["preRelD"] = (relativeSDdiff - ATTRIBS_OF_DEADLINE["preRelD"])
            currentFeatures["SD_ofDL"] = (globalSDdiff - ATTRIBS_OF_DEADLINE["SD_ofDL"])
            currentFeatures["SDofFallOff"] = (globalSDofFallOff - ATTRIBS_OF_DEADLINE["SDofFallOff"])
            previousMark = i
            listOfFeatureDicts.append(currentFeatures)

    preRelD_ave = getMean(preRelD_diffList)
    SD_ofDL_ave = getMean(SD_ofDL_diffList)
    SDofFallOff_ave = getMean(SDofFallOff_diffList)

    preRelD_SD = getStdDev(preRelD_diffList, preRelD_ave)
    SD_ofDL_SD = getStdDev(SD_ofDL_diffList, SD_ofDL_ave)
    SDofFallOff_SD = getStdDev(SDofFallOff_diffList, SDofFallOff_ave)

    # We want to find the number of SDevs from 0
    # FeatureDict contains the differences from the DL ATTRIBS
    # getProbability and store in dict (mean is 0 because we are looking for fitness to DL ATTRIBs)
    for d in listOfFeatureDicts:
        d["preRelD"] = getProbabilty(d["preRelD"], 0, preRelD_SD)
        d["SD_ofDL"] = getProbabilty(d["SD_ofDL"], 0, SD_ofDL_SD)
        d["SDofFallOff"] = getProbabilty(d["SDofFallOff"], 0, SDofFallOff_SD)
    return listOfFeatureDicts

def getProbabilty(x, mean, SD):
    e = np.e
    pi = np.pi
    prob = (1.0 / (SD * ((2 * pi) ** 0.5))) * (e ** -((x - mean) ** 2) / (2 * (SD ** 2)))
    return prob

def trainDeadLineClassification():
    trainingList = [45, 24, 66, 26, 57, 190, 5, 10, 34, 76, 43, 68, 222, 12, 34, 56, 78, 67, 275, 18, 35, 99, 79, 200, 14]
    trainDeadlines = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0]
    getTrainedFeaturesForDL(trainingList, trainDeadlines)

def getTrainedFeaturesForDL(data, markers):
    ave = getMean(data)
    stdDev = getStdDev(data, ave)
    relSDdelta = []
    globalSDDelta = []
    SDofFallOff = []
    previousMark = 0
    for i in xrange(len(data)):
        if(markers[i] == 1):
            # get data from current DL to previous, pre-deadline behaviours
            dataPreceding = data[previousMark + 1:i]
            aveOfPre = getMean(dataPreceding)
            SDOfPre = getStdDev(dataPreceding, ave)
            # get relative measures of pre- features to match against
            # relative features
            relativeSDdiff = ((data[i] * 1.0) - aveOfPre) / SDOfPre
            # global features
            globalSDdiff = ((data[i] * 1.0) - ave) / stdDev
            # Fall-off features
            globalSDofFallOff = ((data[i + 1] * 1.0) - ave) / stdDev
            relSDdelta.append(relativeSDdiff)
            globalSDDelta.append(globalSDdiff)
            SDofFallOff.append(globalSDofFallOff)
            previousMark = i
    ATTRIBS_OF_DEADLINE["preRelD"] = getMean(relSDdelta)
    ATTRIBS_OF_DEADLINE["SD_ofDL"] = getMean(globalSDDelta)
    ATTRIBS_OF_DEADLINE["SDofFallOff"] = getMean(SDofFallOff)


def findOccurenceBefore(currentIndex, L):
    item = L[currentIndex]
    trimL = L[:currentIndex]
    for i in xrange(len(trimL), -1):
        if(trimL[i] == item):
            return i
    # no such item found, return start of list
    return 0

#######STAT FUNCTIONS########

def getMean(values):
    total = 0.0
    for val in values:
        total += val * 1.0
    return total / len(values) * 1.0

def getStdDev(values, ave):
    sqDiffs = []
    for val in values:
        sqDiffs.append((val * 1.0 - ave) ** 2)
    return (getMean(sqDiffs)) ** 0.5



##############ENTRY READING MAIN THREAD#################

def getNewEntries(maxEntries):
    # THREAD SAFE QUEUES
    global entry_Q
    global url_Q
    # URLLIB ASSET FOR THREADED FUNCTION
    global opener
    # GLOBAL LIST FOR FILEREADER THREAD
    global ID_List
    ID_List = []

    clearProgress()
    # Read File in separate Thread
    fileReader = threading.Thread(target=fileReaderThread)
    fileReader.daemon = True
    progress.append(0)
    fileReader.start()
    fileReader.join()
    # get current list of ID entries in file
    idsFromFile = ID_List
    # create list of IDs that check any missing ids and add to the list for maxEntries allowed per run
    idsToCheck = []
    Id = 0
    while len(idsToCheck) < maxEntries:
        if(str(Id) not in idsFromFile):
            idsToCheck.append(Id)
        Id += 1
    entry_Q = Queue.Queue(maxEntries)
    url_Q = Queue.Queue(maxEntries)
    # INIT URL-HANDLER
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    for x in idsToCheck:
        url = "http://cmu-dfab.org/reservations/view_entry.php?id=%d" % (x)
        url_Q.put(url)
    threads = []
    for i in xrange(16):
        print i, "#thread"
        t = threading.Thread(target=urlThreadMain)
        threads.append(t)
        t.daemon = True
        t.start()
# Blocks until url_q and entry_Q finished
    url_Q.join()
    entry_Q.join()
    extractCurrentScrape(idsFromFile)

################WRITE TO FILE, READ NEW FILE, CONVERT TO DISPLAY DICTLIST######################
def extractCurrentScrape(idsFromFile):
    # Convert from Q to List for CURRENT Scrape
    currentScrape = []
    for i in xrange(entry_Q.maxsize):
        a = entry_Q.get()
        if('ID' in a):
            currentScrape.append(a)  # change to list from Q (easier to deal with)
    # Reformat Current DictList
    currentScrape = reFormatContent(currentScrape)
    idsFromCurrent = []
    idsToAppendToFile = []
    for d in currentScrape:
        if "ID" in d and not "URLFAILED" in d:
            s = d["ID"].replace("ID#", "").replace(";", "")
            idsFromCurrent.append(s)
    idsToAppendToFile += set(idsFromCurrent).difference(set(idsFromFile))  # get ids from current scrape that are not in file
    idsToAppendToFile = sorted(list(set(idsToAppendToFile)), cmp=lambda x, y:cmp(int(x), int(y)))
    dictsToWriteFromCurrent = []
    for i in idsToAppendToFile:
        for d in currentScrape:
            if str(i) == d["ID"]:
                dictsToWriteFromCurrent.append(d)
    # Write NEW dicts to File
    strOfNewDicts = dictToString(dictsToWriteFromCurrent)
    writeEntryFile(strOfNewDicts)
    # Flag end of Progress
    progress.append(1)

def clearProgress():
    # Clear global Progress List
    while(1 in progress):
        progress.remove(0)
        progress.remove(1)
    while(0 in progress):
        progress.remove(0)

def fileReaderThread():
    notDone = True
    while notDone:
        ids = extractIDs(getEntryFile())
        for Id in ids:
            ID_List.append(Id)
        notDone = False
        # This is probably excessive

##################URL THREAD FUNCTION##########################

def urlThreadMain():
    while True:
        url = url_Q.get()
        progress.append(0)
        # Find the entry ID
        idStr = getIDfromUrl(url)
        request = urllib2.Request(url)
        try:
            # try to open and read page
            page = opener.open(request)
            raw = page.read()
            print "URL read entry#" + idStr + " success!",

        except:
            # Upon failure, record this in entryDict
            raw = ""
            entryDict = {"ID": idStr, "URLFAILED" : "!!FAILED URL REQUEST!!"}
            entry_Q.put(entryDict)
            print "URL Request Failure!"
            entry_Q.task_done()
            url_Q.task_done()

        startIndex = raw.find('<table id="entry">')

        if(startIndex == -1):
            print "INVALID ENTRY FOR " + idStr
            entryDict = {"ID": idStr, "isValidEntry" : "!!INVALIDENTRY!!"}
            entry_Q.put(entryDict)
            entry_Q.task_done()
            url_Q.task_done()
        else:
            print "Valid Entry!"
            entry = parseHTMLofEntry(raw[startIndex:])
            entryDict = getEntryAsDict(entry, idStr)
            entry_Q.put(entryDict)
            entry_Q.task_done()
            url_Q.task_done()

######## HTML SCRAPING HELPERS ##############
def getIDfromUrl(urlStr):
    index = urlStr.find("=")
    idStr = ""
    if(index != -1):
        idStr = urlStr[index + 1:]
    return idStr

def parseHTMLofEntry(entry):
    entry = entry.replace('<table id="entry">', '')
    endIndex = entry.find('</table>')
    entry = entry[:endIndex]
    entry = entry.lower()
    entry = entry.replace("</tr>", '')
    entry = entry.replace('\n', '')
    entry = entry.replace(' ', '')
    return entry

def getEntryAsDict(entry, idStr):
    titles = []
    contents = []
    entryDict = {"ID": idStr}
    for s in entry.split("<tr>"):
        i = 0
        for sub in s.split("<td>"):
            if(i == 1):
                title = sub.replace("</td>", '').replace(":", '')
                titles.append(title)
            elif(i == 2):
                contents.append(sub.replace("</td>", ''))
            i += 1
    if(len(contents) == len(titles)):
        for i in xrange(len(titles)):
            if titles[i] not in entryDict:
                entryDict[titles[i]] = contents[i]
            else:
                entryDict[titles[i]] += contents[i]
    return entryDict

###################MISC HELPERS##################################
def sumOfPrevious(L, i):
    total = 0
    for j in xrange(0, i):
        total += L[j]
    return total

def countDuplicates(unique, fullList):
    duplications = [0] * len(unique)
    for i in xrange(len(unique)):
        count = 0
        for j in xrange(len(fullList)):
            if(unique[i] == fullList[j]):
                count += 1
        duplications[i] = count
    return duplications

############################MAIN#########################################
def main():
    global progress
    progress = []
    # global list to append to, track progress across threads as rough length count
    # init UI class for Phase 0
    UI = userInterface(phase=0, progressPointer=progress)
    UI.run()
    # Closed UI: read current file, store as Final DictList
    # Re-read appended file with all EntryDicts
    dictListFromFile = fileStringToDict(getEntryFile())
    entryDictList = []
    ######THE FINAL DICTLIST THAT CONTAINS ALL ENTRIES, FROM FILE, AND NEWLY PARSED######
    for i in xrange(len(dictListFromFile)):
        a = dictListFromFile[i]
        if('equipment' in a):  # arbitrary key check THAT IGNORES INVALID ENTRIES! (GOOD JOB PAST-SELF)
            entryDictList.append(a)
    modeList = ['equipment', 'createdby', 'duration', 'type']
    inputField = userInterface(entryDictList, modeList, phase=1)
    inputField.run()
    #######TODO LIST######
    # Local Entry File storage and location (not rigid file path)--DOESNT MATTER?
    # better UI, more explaination and text!!---TODO some more
    # highlight predictive analysis---DONE-ish
    # Incorporate those other cool graphs into UI!!! Done!
    # Fix Colors, layout, other UI visual issues--TODO

######################################
if __name__ == "__main__":
    main()


