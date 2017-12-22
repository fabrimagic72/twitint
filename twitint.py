import re
import getopt
import sys
import tweepy
import time
import datetime
import ConfigParser
import json
import unicodedata
import requests
import logging
import textrazor
import requests
import pymongo
import unicodedata
from pymongo import MongoClient

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.twitint

global ricerca
global TweetId
global TweetText
global LastTweetId
global Config
global configfile
global location
global keyword
global paroleprofilo
global paroleurl
global urlFound

Config = ConfigParser.ConfigParser()
version = "0.95b"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class configuration:
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""
    translateapikey = ""
    imaggakey = ""
    imaggasecret = ""

def PrintRateLimit():
    ratelimit_json = ""
    parsed_ratelimit = ""


    print bcolors.OKBLUE + "[*] Consumer Key = " + bcolors.OKGREEN + configuration.consumer_key
    print bcolors.OKBLUE + "[*] Consumer Secret = " + bcolors.OKGREEN + configuration.consumer_secret
    print bcolors.OKBLUE + "[*] Access Token = " + bcolors.OKGREEN + configuration.access_token
    print bcolors.OKBLUE + "[*] Access Token Secret = " + bcolors.OKGREEN + configuration.access_token_secret
    print""
    print str(datetime.datetime.utcnow()) + " [*] Authenticating..."
    auth = tweepy.OAuthHandler(configuration.consumer_key, configuration.consumer_secret)
    auth.set_access_token(configuration.access_token, configuration.access_token_secret)

    try:
        api = tweepy.API(auth)
    except:
        print bcolors.WARNING + str(datetime.datetime.utcnow()) +  " [*] Error while authenticating. Check API keys"
    else:
        print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Authenticated!"
    print bcolors.OKBLUE
    ratelimit_json = api.rate_limit_status()
    parsed_ratelimit = json.loads(ratelimit_json)
    print (parsed_ratelimit['/statuses/home_timeline'])
    print (parsed_ratelimit['/search/tweets'])



def usage():
    print
    print
    print
    print "___________       .__  __  .___        __    "
    print "\__    ___/_  _  _|__|/  |_|   | _____/  |_  "
    print "  |    |  \ \/ \/ /  \   __\   |/    \   __\ "
    print "  |    |   \     /|  ||  | |   |   |  \  |   "
    print "  |____|    \/\_/ |__||__| |___|___|  /__|   "
    print "                                    \/       "
    print
    print bcolors.HEADER + "TwitInt v" + version +" - by Fabrizio 'Fabrimagic' Monaco"
    print
    print
    print bcolors.OKGREEN + "Usage python tweetfab [Options]"
    print
    print "Options:"
    print "-h, --help                               Show help message and exit"
    print "-s <string>, --string <string            Specify a search string"
    print "-r, --rate                               Print rate limit status (JSON)"
    print "-c <file>, --config <file>               Use configuration file"
    print "-f, --follow                             Follow users with matching criteria tweets"
    print "-b, --block                              Block users with matching criteria tweets"
    print "-r, --report                             Report users with matching criteria as spam"
    print "-o <file>, --output <file>               Save logs to log file"
    print "-t, --trends                             Retrieve the locations that Twitter has trending topic information for. WOEID (a Yahoo! Where On Earth ID) format"
    print "-l <location>, --list <location>         print list of trend topics for a given location"
    print "-y <dest lang>, --yandex <dest lang>     Automatically translate tweet text into <dest lang>"
    print "-d, --deep                               Perform deep imapge analisys, categorization and tagging"
    sys.exit()

def main():
   
    urlFound = ""
    TweetId=[]
    TweetText=[]
    LastTweetId=0
    LastTweetText=""
    ricerca = []
    configfile = ""
    follow = False
    report = False
    block = False
    trends = False
    list = False
    yandex = False
    destlang = ""
    deep = False
    listakeyword = []
    paroleprofilo = []
    paroleurl = []
    dologging = False


    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hs:rc:fbro:tl:y:d", ["help", "string=", "rate", "config=", "follow", "block", "report", "output=", "trends", "--list=", "yandex=", "deep"])
        except getopt.GetoptError as err:
            print(err) # will print something like "option -a not recognized"
            usage()
            sys.exit(2)
        output = None

        if len(opts) == 0:
            usage()
        for o, a in opts:
            if o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-s", "--string"):
                temp = unicode(a, 'utf8')
                ricerca.append(temp.lower())
            elif o in ("-r", "--rate"):
                PrintRateLimit()
                sys.exit()
            elif o in ("-c", "--config"):
                configfile = a
            elif o in ("-d", "--deep"):
                deep = True
            elif o in ("-f", "--follow"):
                follow = True
            elif o in ("-b", "--block"):
                block = True
            elif o in ("-r", "--report"):
                report = True
            elif o in ("-t", "--trends"):
                trends = True
            elif o in ("-y", "--yandex"):
                yandex = True
                destlang = a
            elif o in ("-l", "--list"):
                location = a
                list = True
            elif o in ("-o", "--output"):
                dologging = True
                logfile = a
            else:
                assert False, "[*] Unhandled option"
        if dologging:
            logging.basicConfig(filename=logfile, level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s',
                                datefmt='%d/%m/%Y %I:%M:%S %p')
            logging.warning(bcolors.HEADER + "[*] Configuration file: " + configfile)
            logging.getLogger().addHandler(logging.StreamHandler())
        else:
            logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        if not trends and not list:
            if len(ricerca) == 0:
                print
                logging.critical(bcolors.FAIL + " [*] ERROR: Missing mandatory parameter")
                usage()
                sys.exit()



        try:
            Config.read(configfile)
            configuration.access_token_secret = Config.get('access', "access_token_secret")
            configuration.access_token = Config.get('access', "access_token")
            configuration.consumer_key = Config.get('access', "consumer_key")
            configuration.consumer_secret = Config.get('access', "consumer_secret")
            configuration.translateapikey = Config.get('translate', 'key')
            configuration.imaggakey = Config.get('imagga', 'key')
            configuration.imaggasecred = Config.get('imagga', 'secret')
            textrazor.api_key = Config.get('textrazor', 'key')

        except:
            print bcolors.FAIL + str(datetime.datetime.utcnow()) + "[*] Error while reading config file"
            sys.exit()

        print bcolors.OKBLUE
        print ("___________       .__  __  .___        __    ")
        print ("\__    ___/_  _  _|__|/  |_|   | _____/  |_  ")
        print ("  |    |  \ \/ \/ /  \   __\   |/    \   __\ ")
        print ("  |    |   \     /|  ||  | |   |   |  \  |   ")
        print ("  |____|    \/\_/ |__||__| |___|___|  /__|   ")
        print ("                                    \/       ")
        print
        print "TwitInt v" + version +"- by Fabrizio 'Fabrimagic' Monaco"
        print


        logging.warning(bcolors.HEADER + "[*] Twitter Consumer Key = " + bcolors.OKGREEN + configuration.consumer_key + bcolors.OKBLUE)
        logging.warning(bcolors.HEADER + "[*] Twitter Consumer Secret = " + bcolors.OKGREEN + configuration.consumer_secret + bcolors.OKBLUE)
        logging.warning(bcolors.HEADER + "[*] Twitter Access Token = " + bcolors.OKGREEN + configuration.access_token + bcolors.OKBLUE)
        logging.warning(bcolors.HEADER + "[*] Twitter Access Token Secret = " + bcolors.OKGREEN + configuration.access_token_secret + bcolors.OKBLUE)
        logging.warning(
            bcolors.HEADER + "[*] Imagga API Key = " + bcolors.OKGREEN + configuration.imaggakey + bcolors.OKBLUE)
        logging.warning(
            bcolors.HEADER + "[*] Imagga Api Secret = " + bcolors.OKGREEN + configuration.imaggasecred + bcolors.OKBLUE)
        logging.warning(
            bcolors.HEADER + "[*] TextRazor Key = " + bcolors.OKGREEN + textrazor.api_key + bcolors.OKBLUE)
	logging.warning(
            bcolors.HEADER + "[*] Yandex Translate Key = " + bcolors.OKGREEN + configuration.translateapikey + bcolors.OKBLUE)
        print
        if yandex:
                print bcolors.BOLD + '*** Translation Powered by Yandex.Translate -  http://translate.yandex.com ***' + bcolors.ENDC + bcolors.OKBLUE
                print
        if deep:
            print bcolors.BOLD + '*** Image Categorization and tagging Powered by Imagga - http://www.imagga.com ***' + bcolors.ENDC + bcolors.OKBLUE
            print
        logging.warning(bcolors.HEADER + " [*] Authenticating..." + bcolors.OKBLUE)


        auth = tweepy.OAuthHandler(configuration.consumer_key, configuration.consumer_secret)
        auth.set_access_token(configuration.access_token, configuration.access_token_secret)


        try:
            api = tweepy.API(auth)
        except:
            logging.critical(bcolors.FAIL + " [*] Error while authenticating. Check API keys" + bcolors.OKBLUE)
        else:
            logging.warning(bcolors.HEADER + " [*] Authenticated!" + bcolors.OKBLUE)

        if trends:
            try:
                print
                print "##### MANUAL INPUT REQUIRED #####"
                location = str(raw_input("Please specify a location name (ENTER for none): "))
                listlocationjson = api.trends_available()
                if location == "":
                    for elemento in listlocationjson:
                        print bcolors.OKBLUE + '[*] Location Info: ' + bcolors.OKGREEN + elemento['name'] + ' - ' + elemento['country'] + bcolors.OKBLUE + ' - WOEID:' + bcolors.OKGREEN + ' ' + str(elemento['woeid'])
                else:
                    for elemento in listlocationjson:
                        if elemento['name'] == location:
                            print bcolors.OKBLUE + '[*] Location Info: ' + bcolors.OKGREEN + elemento['name'] + ' - ' + elemento['country'] + bcolors.OKBLUE + ' - WOEID:' + bcolors.OKGREEN + ' ' + str(elemento['woeid'])
            except tweepy.RateLimitError:
                PrintRateLimit()
            print bcolors.OKBLUE + '[*] Number of Total Locations Retrieved : ' + bcolors.OKGREEN + str(len(listlocationjson))
            sys.exit()

        if list:
            woeid = ""
            try:
                listlocationjson = api.trends_available()
                if str(location) != "":
                    for elemento in listlocationjson:
                        if elemento['name'] == str(location):
                            woeid = str(elemento['woeid'])
                    if str(woeid) == "":
                        print bcolors.FAIL + "[*] Failed to retrieve trend topics for " + location
                        sys.exit()
                else:
                    print bcolors.FAIL + "[*] Missing location. Check parameters"
                    sys.exit()

                print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + bcolors.OKGREEN + " [*] WOEID for " + location + " is: " + str(woeid)
                listtrends = api.trends_place(woeid)
                print bcolors.OKBLUE + '[*] List of trend topics retrieved for  ' + str(location)
                listtrendsjson = json.dumps(listtrends[0])
                listtrendsparsed = json.loads(listtrendsjson)

                for elemento in listtrendsparsed['trends']:
                    print bcolors.OKBLUE + '[*] ' + bcolors.OKGREEN + elemento['name'] + bcolors.OKBLUE + ' - Tweet Volume: ' + bcolors.OKGREEN + str(elemento['tweet_volume'])
            except:
                raise

            sys.exit()

        while True:
            try:
                public_tweets = tweepy.Cursor(api.search, q=ricerca[0]).items(1)
                break
            except tweepy.RateLimitError:
                logginf.critical(" [*] WARNING: Rate Limit error encountered. Sleeping 15 minutes")
                PrintRateLimit()
                time.sleep(61*15)
                print logging.warning(bcolors.HEADER + " [*] Retrying..." + bcolors.OKBLUE)
                continue

        for tweet in public_tweets:
            LastTweetText = tweet.text
            LastTweetId = tweet.id

        logging.warning(bcolors.HEADER + "[*] Twitint is being initialized. This will take a minute" + bcolors.OKBLUE)

        while True:
            trovato = False
            trovatototal = 0
            logging.warning(bcolors.HEADER + " [*] Waiting 60 seconds in order to avoid Twitter API Rate Limit" + bcolors.OKBLUE)
            time.sleep(60)


            while True:
                try:
                    logging.warning(bcolors.HEADER + " [*] Trying to get new tweets" + bcolors.OKBLUE)

                    public_tweets = tweepy.Cursor(api.search, q=ricerca[0], since_id=LastTweetId).items(10)
                    break

                except tweepy.RateLimitError:
                    logging.critical(bcolors.FAIL + " [*] ERROR: Rate Limit error encountered. Sleeping 15 minutes" + bcolors.OKBLUE)
                    PrintRateLimit()
                    time.sleep(61*15)
                    logging.warning(bcolors.HEADER + " [*] Retrying..." + bcolors.OKBLUE)
                    continue
                except tweepy.TweepError:
                    print (bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] ERROR: Failed to establish a new connection" + bcolors.OKBLUE)
                    time.sleep(10)
                    continue

            if public_tweets:
                listatweet = []
                try:
                    for tweet in public_tweets:
                        listatweet.append(tweet.id)
                        LastTweetId = listatweet[0]
                        LastTweetText = tweet.text.lower()

                        for elemento in range(0,len(ricerca)):
                            if LastTweetText.find(ricerca[elemento]) != -1:
                                trovato = True
                            else:
                                trovato = False
                                break

                        if trovato:
                            trovatototal += 1
                            logging.warning(bcolors.HEADER + "*************************************************************************************" + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] Found new tweet matching selected criteria: " + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] Tweet Text: " + bcolors.OKGREEN + tweet.text + bcolors.OKBLUE)
                            if yandex:
                                yandexurl = 'https://translate.yandex.net/api/v1.5/tr.json/detect?key=' + str(configuration.translateapikey) + '&text=' + tweet.text.encode('utf8')
                                detectedlanguagejson = requests.post(yandexurl)
                                detectedlanguageparsed = json.loads(detectedlanguagejson.text)
                                logging.warning(bcolors.HEADER + " [*] Detected Language: " + bcolors.OKGREEN + str(detectedlanguageparsed['lang'] + bcolors.OKBLUE))
                                yandextransurl = 'https://translate.yandex.net/api/v1.5/tr.json/translate?key=' + str(configuration.translateapikey) + '&text=' + tweet.text.encode('utf8') + '&lang=' + str(destlang)
                                translatedtweetjson = requests.post(yandextransurl)
                                translatedtweetparsed = json.loads(translatedtweetjson.text)
                                if str(translatedtweetparsed['code']) == "200":
                                    logging.warning(bcolors.HEADER + " [*] Translated Tweet: " + bcolors.OKGREEN + str(translatedtweetparsed['text'])[3:-2] + bcolors.OKBLUE)
                                else:
                                    logging.critical(bcolors.FAIL + " [*] Unable to translate this tweet - Error Code: " + str(translatedtweetparsed['code']) + bcolors.OKBLUE)
			    urlFound=""
			    try:
			    	urlFound = re.search("(?P<url>https?://[^\s]+)", tweet.text).group("url")
			    except:
				logging.warning(bcolors.HEADER + " [*] No URL Found inside Tweet Text" )
                            logging.warning(bcolors.HEADER + " [*] User Id: " + bcolors.OKGREEN + str(tweet.user.id) + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] User Screen Name: " + bcolors.OKGREEN + tweet.user.screen_name + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] User Name: " + bcolors.OKGREEN + tweet.user.name + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] Followers : " + bcolors.OKGREEN + str(tweet.user.followers_count) + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] Tweet Created At : " + bcolors.OKGREEN + str(tweet.created_at) + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] Retweet Count : " + bcolors.OKGREEN + str(tweet.retweet_count) + bcolors.OKBLUE)
                            logging.warning(bcolors.HEADER + " [*] Geo Enabled : " + bcolors.OKGREEN + str(tweet.user.geo_enabled) + bcolors.OKBLUE)
		  	    database = { "keyword" : ricerca, "text" : tweet.text.encode('utf8'), "user" : unicode(tweet.user.id), "name" : tweet.user.screen_name.encode('utf8'), "time" : str(tweet.created_at)}
			    if yandex:
				database["translated"] = str(translatedtweetparsed['text'])[3:-2]
		            if urlFound !="":
			    	logging.warning(bcolors.HEADER + " [*] URL Found : " + bcolors.OKGREEN + urlFound  + bcolors.OKBLUE)
				database["url"] = urlFound
                            try:
                                logging.warning(bcolors.HEADER + " [*] Source : " + bcolors.OKGREEN + str(tweet.source) + bcolors.OKBLUE)
                            except:
                                logging.warning(" [*] Could not retrieve Source")
			    try:
			    	post_id = db.tweets.insert_one(database)
			    except:
				logging.warning(" [*] Could not insert tweet into database")
			    database = {}
                            if deep:
                                imaggatagjson = requests.get('https://api.imagga.com/v1/tagging?url=' + str(tweet.user.profile_background_image_url), auth=(configuration.imaggakey, configuration.imaggasecred))
                                imaggatagparsed = json.loads(imaggatagjson.text)

                                logging.warning(" [*] Twitter User Profile Image Analysis in Progress...")
                                for elencotag in imaggatagparsed['results']:
                                    for tags in elencotag['tags']:
                                        key = tags['tag']
                                        confidence = tags['confidence']
                                        if confidence > 30:
                                            logging.warning(bcolors.HEADER + " [*] Profile Image Tag Found: " + bcolors.OKGREEN + key + bcolors.OKBLUE)
                                            logging.warning(bcolors.HEADER + " [*] Confidence: " + bcolors.OKGREEN + str(confidence))
 #                                       if listakeyword.count(key.lower()) > 0:
 #                                           logging.info(" [*] Tag: " + bcolors.OKGREEN +  key + bcolors.OKBLUE + " found in " + str(tweet.user.profile_background_image_url) + bcolors.OKBLUE)
 #                                           paroleprofilo.append(key)

                            if len(tweet.entities['urls']) > 0:
                                urljson = json.dumps(str(tweet.entities['urls'][0]))
                                urlparsed = str(json.loads(urljson))
                                strsearch = "expanded_url"
                                urlindex = urlparsed.index(strsearch)
                                urlfinestringa = urlparsed.index("', u'display_url")
                                expandedurl = urlparsed[(urlindex+17):urlfinestringa]

                                if expandedurl[:-4] == ".jpg" or expandedurl[:-4] == ".gif" or expandedurl[:-4] == ".png" or expandedurl[:-5] == ".jpeg":
                                    isimage = True
                                else:
                                    isimage = False

                                logging.warning(bcolors.HEADER + " [*] Expanded Media URL:" + bcolors.OKGREEN + expandedurl + bcolors.OKBLUE)

                                client = textrazor.TextRazor(extractors=["entities", "topics"])
                                response = client.analyze_url(expandedurl)

                                if deep:
                                    try:
                                        logging.warning(" [*] Semantic Analysis in Progress...")
                                        for entity in response.entities():
                                            if entity.confidence_score > 3:
                                                logging.warning(" [*] ID: " + bcolors.OKGREEN + entity.id + bcolors.OKBLUE)
                                                logging.warning(" [*] Confidence Score: " + bcolors.OKGREEN + str(
                                                    entity.confidence_score) + bcolors.OKBLUE)

                                    except:
                                        raise

                                if deep and isimage:
                                    logging.warning(" [*] Media Image Analysis in progress...")
                                    imaggatagjson = requests.get('https://api.imagga.com/v1/tagging?url=' + expandedurl, auth=(configuration.imaggakey, configuration.imaggasecred))
                                    imaggatagparsed = json.loads(imaggatagjson.text)
                                    for elencotag in imaggatagparsed['results']:
                                        for tags in elencotag['tags']:
                                            key = tags['tag']
                                            if listakeyword.count(key.lower()) > 0:
                                               logging.warning(bcolors.HEADER + " [*] Tag: " + bcolors.OKGREEN +  key + bcolors.OKBLUE + " found in " + expandedurl + bcolors.OKBLUE)
                                               paroleurl.append(key)
                                elif deep and not isimage:
                                    logging.warning(" [*] Attached URL is not an image. Skipping Image Analysis")

                                logging.warning(bcolors.HEADER + " [*] GPS Coords: " + bcolors.OKGREEN + str(tweet.coordinates) + bcolors.OKBLUE)
                                userlocation = tweet.user.location.encode('utf8')
                                try:
                                    logging.warning(bcolors.HEADER + " [*] User Location: " + bcolors.OKGREEN + str(userlocation) + bcolors.OKBLUE)
                                except:
                                    logging.warning(" [*] Could not retrieve User Location")
                                    continue

                            logging.warning(bcolors.HEADER + " [*] Direct Link: " + bcolors.OKGREEN + "https://twitter.com/intent/user?user_id=" + str(tweet.user.id) + bcolors.OKBLUE)
                            if follow:
                                api.create_friendship(id=tweet.user.id)
                                logging.warning(bcolors.HEADER + " [*] Just followed User: " + bcolors.OKGREEN + tweet.user.screen_name + bcolors.OKBLUE)
                            if block:
                                api.create.block(id=tweet.user.id)
                                logging.warning(bcolors.HEADER + ' [*] Blocked User: ' + bcolors.OKGREEN + tweet.user.screen_name + bcolors.OKBLUE)
                            if report:
                                api.report_spam(id=tweet.user.id)
                                logging.warning(bcolors.HEADER + ' [*] Reported spam. User: ' + bcolors.OKGREEN + tweet.user.screen_name + bcolors.OKBLUE)

                except KeyError:
                        logging.critical(bcolors.FAIL + " [*] Key Error Occurred" + bcolors.OKBLUE)
                        continue
                except:
                    logging.critical(bcolors.FAIL + " [*] Internal Error Occurred: "+ bcolors.OKBLUE)
                    time.sleep(1)
                    continue
                else:
                    if trovatototal == 0:
                        logging.warning(bcolors.HEADER + " [*] No New tweets matching selected criteria" + bcolors.OKBLUE)


    except KeyboardInterrupt:
        logging.warning(bcolors.HEADER + "Interrupted from keyboard. I Hope you enjoyed using Twitint!" + bcolors.OKBLUE)
        sys.exit()

if __name__ == "__main__":
    main()

