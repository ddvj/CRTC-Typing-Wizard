from tkinter import *
import wikipedia
import string
import time
import random
import re


keyIndexPosition = 0
errors = 0
sampleSentences = ''
startTimeSet = False
startTime = 0
endTime = 0


def getSummary():
    
    try:
        pageContent = wikipedia.page(wikipedia.random(pages=1)).content
    except:
        return getSummary()
    
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr|Mt)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|edu)"
    digits = "([0-9])"

    def split_into_sentences(text):
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        if "Ph.D" in text: 
            text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
        text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
        if "”" in text: 
            text = text.replace(".”","”.")
        if "\"" in text: 
            text = text.replace(".\"","\".")
        if "!" in text: 
            text = text.replace("!\"","\"!")
        if "?" in text: 
            text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences

    pageContent = split_into_sentences(pageContent)
    global sampleSentences
    sampleSentences = ''
    for sentence in pageContent:
        if not ('=' in sentence):
            if sampleSentences == '':
                sampleSentences = sentence
            else:
                sampleSentences = sampleSentences + ' ' + sentence
    
    for character in sampleSentences:
        if not (character in string.printable):
            return getSummary()
    
    return sampleSentences

def getNewPassage():
    
    global keyIndexPosition
    global errors
    global startTimeSet
    
    keyIndexPosition = 0
    errors = 0
    startTimeSet = False

    passageText.configure(state='normal')    
    passageText.delete(1.0, END)
    passageText.insert(1.0, getSummary())
    passageText.configure(state='disabled')

def keyPress(event):
    
    global keyIndexPosition
    global errors
    global startTimeSet
    global startTime
    global endTime

    key = event.char

    if (keyIndexPosition == 0) and (not startTimeSet):
        startTime = time.time()
        startTimeSet = True

    if ((key in string.printable) and (key != '')) or (event.keysym == 'space'):
        passageText.tag_add(str(keyIndexPosition), '1.0 + ' + str(keyIndexPosition) + ' indices', '1.0 + ' + str(keyIndexPosition + 1) + ' indices')
        
        if ((key == sampleSentences[keyIndexPosition]) and (sampleSentences[keyIndexPosition] != ' ')) or ((sampleSentences[keyIndexPosition] == ' ') and (event.keysym == 'space')):
            if sampleSentences[keyIndexPosition] == ' ':
                passageText.tag_config(str(keyIndexPosition), background='light green')
            else:
                passageText.tag_config(str(keyIndexPosition), background='light green')
        else:
            if sampleSentences[keyIndexPosition] == ' ':
                passageText.tag_config(str(keyIndexPosition), background='IndianRed1')
            else:
                passageText.tag_config(str(keyIndexPosition), background='IndianRed1')
            errors += 1
        
        try:
            passageText.tag_delete('underlinedTag')
        finally:
            passageText.tag_add('underlinedTag', '1.0 + ' + str(keyIndexPosition + 1) + ' indices', '1.0 + ' + str(keyIndexPosition + 2) + ' indices')
            passageText.tag_config('underlinedTag', underline=1)
        
        keyIndexPosition += 1
        updateErrorsAccuracy(errors, keyIndexPosition)
        calcWPM(round(time.time() - startTime, 2), keyIndexPosition)
        
        if keyIndexPosition == len(sampleSentences):
            endTime = time.time()
            displayTime(endTime, startTime)
            getNewPassage()

def calcWPM(timeTaken, chars):
    wpmLabel.configure(text='WPM: ' + str(round((((chars / 5) * 60) / timeTaken), 2)))

def updateErrorsAccuracy(Errors, chars):
    errorsLabel.configure(text='Errors: ' + str(Errors))
    accuracyLabel.configure(text='Accuracy: ' + str(round(((chars - Errors) / chars) * 100, 2)) + '%')

def displayTime(endTime, startTime):
    timeLabel.configure(text='Time: ' + str(round(endTime - startTime) / 2) + ' seconds')


root = Tk()
root.title('Typing Wizard')

instructionsText = Text(root, font=('Times', 8), wrap=WORD, height=2, width=175)
instructionsText.grid(row=0, column=1, columnspan=3)
instructionsText.insert(1.0, "The timer will start once you start typing. If you do not like the passage for any reason, you can press the 'New Passage' button to generate a new one. Words per minute is calculated by determining the amount of characters you would've typed in a minute, then dividing that by 5. Pressing backspace will do nothing.")
instructionsText.configure(state='disabled')

wpmLabel = Label(root, text='WPM: 0')
wpmLabel.grid(row=1, column=0)

errorsLabel = Label(root, text='Errors: 0', fg='red')
errorsLabel.grid(row=1, column=1)

accuracyLabel = Label(root, text='Accuracy: 0%')
accuracyLabel.grid(row=1, column=2)

passageText = Text(root, font=('Times', 12), wrap=WORD, width=188)
passageText.grid(row=2, column=0, columnspan=5, pady=10)
passageText.insert(1.0, getSummary())
passageText.configure(state='disabled')

newPassageButton = Button(root, text='New Passage', command=getNewPassage)
newPassageButton.grid(row=3, column=2)

timeLabel = Label(root, text='Time: 0')
timeLabel.grid(row=1, column=3)

root.bind('<Key>', keyPress)

root.mainloop()