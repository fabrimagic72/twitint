import getopt
import sys
import tweepy
import time
import datetime
import ConfigParser
import json
import unicodedata
import requests

global ricerca
global TweetId
global TweetText
global LastTweetId
global verbose
global Config
global configfile
global location


verbose = False
Config = ConfigParser.ConfigParser()
version = "0.93b"


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


def PrintRateLimit():
    ratelimit_json = ""
    parsed_ratelimit = ""

    if verbose:
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
        if verbose:
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
    print "-v, --verbose                            Enable verbose output"
    print "-s <string>, --string <string            Specify a search string"
    print "-r, --rate                               Print rate limit status (JSON)"
    print "-c <file>, --config <file>               Use configuration file"
    print "-f, --follow                             Follow users with matching criteria tweets"
    print "-b, --block                              Block users with matching criteria tweets"
    print "-r, --report                             Report users with matching criteria as spam"
    print "-o <file>, --output <file>               Save logs to log file"
    print "-n, --notweet                            Do not save tweets on log file to prevent encoding issues"
    print "-u, --userid                             Save only user ID on logfile, creating a direct link to user timeline"
    print "-t, --trends                             Retrieve the locations that Twitter has trending topic information for. WOEID (a Yahoo! Where On Earth ID) format"
    print "-l <location>, --list <location>         print list of trend topics for a given location"
    print "-y <dest lang>, --yandex <dest lang>     Automatically translate tweet text into <dest lang>"
    sys.exit()

def main():

    TweetId=[]
    TweetText=[]
    LastTweetId=0
    LastTweetText=""
    ricerca = []
    verbose = False
    configfile = ""
    follow = False
    report = False
    block = False
    logfile =""
    dologging = False
    notweet = False
    userid = False
    trends = False
    list = False
    yandex = False
    destlang = ""


    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hs:vrc:fbro:nutl:y:", ["help", "string=", "verbose", "rate", "config=", "follow", "block", "report", "output=", "notweet", "userid", "trends", "--list=", "yandex="])
        except getopt.GetoptError as err:
            print(err) # will print something like "option -a not recognized"
            usage()
            sys.exit(2)
        output = None
        verbose = False
        if len(opts) == 0:
            usage()
        for o, a in opts:
            if o == "-v":
                verbose = True
            elif o in ("-h", "--help"):
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
            elif o in ("-f", "--follow"):
                follow = True
            elif o in ("-u", "--userid"):
                userid = True
            elif o in ("-b", "--block"):
                block = True
            elif o in ("-r", "--report"):
                report = True
            elif o in ("-n", "--notweet"):
                notweet = True
            elif o in ("-t", "--trends"):
                trends = True
            elif o in ("-y", "--yandex"):
                yandex = True
                destlang = a
            elif o in ("-l", "--list"):
                location = a
                list = True
            elif o in ("-o", "--output"):
                logfile = a
                dologging = True
                try:
                    out_file = open(logfile, "a")
                except:
                    print "[*] Error while creating output file"
                    sys.exit()
            else:
                assert False, "[*] Unhandled option"
        if not trends and not list:
            if len(ricerca) == 0 or configfile == "":
                print
                print bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] ERROR: Missing mandatory parameter"
                usage()
                sys.exit()

        if verbose:
            print bcolors.OKBLUE + "[*] Configuration file: " + configfile

        try:
            Config.read(configfile)
            configuration.access_token_secret = Config.get('access', "access_token_secret")
            configuration.access_token = Config.get('access', "access_token")
            configuration.consumer_key = Config.get('access', "consumer_key")
            configuration.consumer_secret = Config.get('access', "consumer_secret")
            configuration.translateapikey = Config.get('translate', 'key')

        except:
            print bcolors.FAIL + str(datetime.datetime.utcnow()) + "[*] Error while reading config file"
            sys.exit()

        print ("___________       .__  __  .___        __    ")
        print ("\__    ___/_  _  _|__|/  |_|   | _____/  |_  ")
        print ("  |    |  \ \/ \/ /  \   __\   |/    \   __\ ")
        print ("  |    |   \     /|  ||  | |   |   |  \  |   ")
        print ("  |____|    \/\_/ |__||__| |___|___|  /__|   ")
        print ("                                    \/       ")
        print
        print bcolors.HEADER + "TwitInt v" + version +"- by Fabrizio 'Fabrimagic' Monaco"
        print ""

        if verbose:
            print bcolors.OKBLUE + "[*] Consumer Key = " + bcolors.OKGREEN + configuration.consumer_key
            print bcolors.OKBLUE + "[*] Consumer Secret = " + bcolors.OKGREEN + configuration.consumer_secret
            print bcolors.OKBLUE + "[*] Access Token = " + bcolors.OKGREEN + configuration.access_token
            print bcolors.OKBLUE + "[*] Access Token Secret = " + bcolors.OKGREEN + configuration.access_token_secret
            print""
            if yandex:
                    print bcolors.HEADER + '*** Translation Powered by Yandex.Translate -  http://translate.yandex.com ***'
            print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Authenticating..."


        auth = tweepy.OAuthHandler(configuration.consumer_key, configuration.consumer_secret)
        auth.set_access_token(configuration.access_token, configuration.access_token_secret)


        try:
            api = tweepy.API(auth)
        except:
            print bcolors.WARNING + str(datetime.datetime.utcnow()) + " [*] Error while authenticating. Check API keys"
        else:
            if verbose:
                print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Authenticated!"
            if dologging and userid == False:
                out_file.write(str(datetime.datetime.utcnow()) + " [*] Authenticated!\n")

        if trends:
            try:
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
                print bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] WARNING: Rate Limit error encountered. Sleeping 15 minutes"
                PrintRateLimit()
                time.sleep(61*15)
                print bcolors.WARNING + str(datetime.datetime.utcnow()) + " [*] Retrying..."
                continue

        for tweet in public_tweets:
            LastTweetText = tweet.text
            LastTweetId = tweet.id

        if verbose:
            print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Twitint is being initialized. This will take a minute"
        if dologging and userid == False:
            out_file.write(str(datetime.datetime.utcnow()) + " [*] TwitInt Initialized\n")
            out_file.close()

        while True:
            trovato = False
            trovatototal = 0
            if verbose:
                print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Waiting 60 seconds in order to avoid Twitter API Rate Limit"
            time.sleep(60)


            while True:
                try:
                    if verbose:
                        print str(datetime.datetime.utcnow()) + " [*] Trying to get new tweets"

                    public_tweets = tweepy.Cursor(api.search, q=ricerca[0], since_id=LastTweetId).items(10)
                    break

                except tweepy.RateLimitError:
                    print bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] ERROR: Rate Limit error encountered. Sleeping 15 minutes"
                    PrintRateLimit()
                    time.sleep(61*15)
                    print bcolors.WARNING + str(datetime.datetime.utcnow()) + " [*] Retrying..."
                    continue
                except tweepy.TweepError:
                    print (bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] ERROR: Failed to establish a new connection")
                    time.sleep(10)
                    continue

            if public_tweets:
                try:
                    if dologging:
                        out_file = open(logfile, "a")
                except:
                    print "[*] Error while opening logfile"
                    sys.exit()

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
                            if verbose:
                                #print tweet
                                print bcolors.OKBLUE + "*************************************************************************************"
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + bcolors.HEADER + " [*] Found new tweet matching selected criteria: ")
                                print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Tweet Text: " + bcolors.OKGREEN + tweet.text
                                if yandex:
                                    yandexurl = 'https://translate.yandex.net/api/v1.5/tr.json/detect?key=' + str(configuration.translateapikey) + '&text=' + tweet.text.encode('utf8')
                                    detectedlanguagejson = requests.get(yandexurl)
#                                    detectedlanguagejson = requests.get('https://translate.yandex.net/api/v1.5/tr.json/detect?key=' + str(configuration.translateapikey) + '&text="' + str(tweet.text) + '"')
                                    detectedlanguageparsed = json.loads(str(detectedlanguagejson.text))
                                    print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Detected Language: " + bcolors.OKGREEN + str(detectedlanguageparsed['lang'])
                                    yandextransurl = 'https://translate.yandex.net/api/v1.5/tr.json/translate?key=' + str(configuration.translateapikey) + '&text=' + tweet.text.encode('utf8') + '&lang=' + str(destlang)
#                                    print yandextransurl
                                    translatedtweetjson = requests.get(yandextransurl)
                                    translatedtweetparsed = json.loads(translatedtweetjson.text)
                                    if str(translatedtweetparsed['code']) == "200":
                                        print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Translated Tweet: " + bcolors.OKGREEN + str(translatedtweetparsed['text'])[3:-2]
                                    else:
                                        print bcolors.WARNING + str(datetime.datetime.utcnow()) + " [*] Unable to translate this tweet - Error Code: " + str(translatedtweetparsed['code'])
                                print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] User Id: " + bcolors.OKGREEN + str(tweet.user.id)
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] User Screen Name: " + bcolors.OKGREEN + tweet.user.screen_name)
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] User Name: " + bcolors.OKGREEN + tweet.user.name)
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Followers : " + bcolors.OKGREEN + str(tweet.user.followers_count))
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Tweet Created At : " + bcolors.OKGREEN + str(tweet.created_at))
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Retweet Count : " + bcolors.OKGREEN + str(tweet.retweet_count))
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Geo Enabled : " + bcolors.OKGREEN + str(tweet.user.geo_enabled))
                                try:
                                    print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Source : " + bcolors.OKGREEN + str(tweet.source))
                                except:
                                    print bcolors.WARNING + str(datetime.datetime.utcnow()) + " [*] Could not retrieve Source"
                                print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] GPS Coords: " + bcolors.OKGREEN + str(tweet.coordinates))
                                userlocation = tweet.user.location.encode('utf8')
                                try:
                                    print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] User Location: " + bcolors.OKGREEN + str(userlocation))
                                except:
                                    print bcolors.WARNING + str(datetime.datetime.utcnow()) + " [*] Could not retrieve User Location"
                                    continue

                                if dologging and userid == False:
                                    out_file.write('------------------------------------------------------------------------------------------\n')
                                    if notweet == False and userid == False:
                                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] ' + tweet.text.encode('utf8') + '\n')
                                        if yandex and str(translatedtweetparsed['code']) == "200":
                                            out_file.write(str(datetime.datetime.utcnow()) + ' [*] ' + str(translatedtweetparsed['text']))

                                    if userid == False:
                                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] Originating user id: ' + str(tweet.user.id) + '\n')
                                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] Originating user screen name: ' + str(tweet.user.screen_name) + '\n')
                                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] Followers: ' + bcolors.OKGREEN + str(tweet.user.followers_count) + '\n')
                                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] Tweet Created At: ' + bcolors.OKGREEN + str(tweet.created_at) + '\n')
                                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] Retweet Count: ' + bcolors.OKGREEN + str(tweet.retweet_count) + '\n')
                                        try:
                                            out_file.write(str(datetime.datetime.utcnow()) + ' [*] Source: ' + bcolors.OKGREEN + str(tweet.source) + '\n')
                                        except:
                                            continue
                                        try:
                                            out_file.write(str(datetime.datetime.utcnow()) + ' [*] User Location: ' + bcolors.OKGREEN + str(userlocation) + '\n')
                                        except:
                                            continue

                            if dologging and userid:
                                out_file.write("https://twitter.com/intent/user?user_id=" + str(tweet.user.id) + '\n')
                            if follow:
                                api.create_friendship(id=tweet.user.id)
                                if verbose:
                                    print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Just followed User: " + bcolors.OKGREEN + tweet.user.screen_name)
                                if dologging and userid == False:
                                    out_file.write(str(datetime.datetime.utcnow()) + ' [*] Just followed User: ' + str(tweet.user.screen_name) + '\n')
                            if block:
                                api.create.block(id=tweet.user.id)
                                if dologging and userid == False:
                                    out_file.write(str(datetime.datetime.utcnow()) + ' [*] Blocked User: ' + str(tweet.user.screen_name) + '\n')
                                if verbose:
                                    print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + ' [*] Blocked User: ' + bcolors.OKGREEN + tweet.user.screen_name)
                            if report:
                                api.report_spam(id=tweet.user.id)
                                if verbose:
                                    print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + ' [*] Reported spam. User: ' + bcolors.OKGREEN + tweet.user.screen_name)
                                if dologging and userid == False:
                                    out_file.write(str(datetime.datetime.utcnow()) + ' [*] Reported spam. User: ' + str(tweet.user.screen_name) + '\n')
                    if dologging:
                        out_file.close()
                except KeyError:
                        print bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] Key Error Occurred"
                        continue
                except:
                    print (bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] ERROR: Failed to establish a new connection.")
                    print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + bcolors.OKGREEN + " [*] Sleeping 10 seconds and then i will retry.")
                    time.sleep(10)
                    continue
                else:
                    if trovatototal == 0:
                        print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + bcolors.WARNING + " [*] No New tweets matching selected criteria")


    except KeyboardInterrupt:
        print bcolors.HEADER + "Interrupted from keyboard. I Hope you enjoyed using Twitint!"
        sys.exit()

if __name__ == "__main__":
    main()

