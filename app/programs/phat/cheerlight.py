import urllib.request
import urllib.error
import json
import time
import unicornhat as UH

lastID = 0      #most recent entry_id
refresh = 15    #refresh time in secs
urlRoot = "http://api.thingspeak.com/channels/1417/"
pixels = []    #list of pixels and their colours
maxPixels = 32

namesToRGB = {'red': [0xFF, 0, 0],
                'green': [0, 0x80, 0],
                'blue': [0, 0, 0xFF],
                'cyan': [0, 0xFF, 0xFF],
                'white': [0xFF, 0xFF, 0xFF],
                'warmwhite': [0xFD, 0xF5, 0xE6],
                'purple': [0x80, 0, 0x80],
                'magenta': [0xFF, 0, 0xFF],
                'yellow': [0xFF, 0xFF, 0],
                'orange': [0xFF, 0xA5, 0],
                'pink': [0xFF, 0xC0, 0xCB],
                'oldlace': [0xFD, 0xF5, 0xE6]}


#retrieve and load the JSON data into a JSON object
def getJSON(url):
	try:
		jsonFeed = urllib.request.urlopen(urlRoot + url)
		feedData = jsonFeed.read().decode(jsonFeed.headers.get_content_charset())
		#print feedData
		jsonFeed.close()
		data = json.loads(feedData)
		return data
	except urllib.error.HTTPError as e:
		print('HTTPError = ' + str(e.code))
	except urllib.error.URLError as e:
		print('URLError = ' + str(e.reason))
	except Exception:
		import traceback
		print('generic exception: ' + traceback.format_exc())

	return []		

#use the JSON object to identify the colour in use,
#update the last entry_id processed
def parseColour(feedItem):
    global lastID
    global pixels

    for name in namesToRGB.keys():
        if feedItem["field1"] == name:
            if mode != 0 and name == 'green':	#ignore green when in lights or star mode
                name = "yellow" 
            pixels.insert(0, namesToRGB[name])    #add the colour to the head
            break

    lastID = getEntryID(feedItem)

#read the last entry_id
def getEntryID(feedItem):
    if len(feedItem) == 0:
        return -1
    return int(feedItem["entry_id"])

#show all pixels one colour
def showColour(c):
    for x in range(8):
        for y in range(4):
            UH.set_pixel(x, y, c[0], c[1], c[2])
    UH.show()
                  
#main program

UH.brightness(0.4)


#check for new colour requests
def run(params):
    while True:
        data = getJSON("field/1/last.json")
        if getEntryID(data) > lastID:   #Has this entry_id been processed before?
            parseColour(data)
            showColour(pixels[0])
            #if mode != 2:
            time.sleep(5)
        else:
            time.sleep(refresh)