import getopt
import sys
import tweepy
import time
import datetime
import ConfigParser
import json
import unicodedata

global ricerca
global TweetId
global TweetText
global LastTweetId
global verbose
global Config
global configfile

verbose = False
Config = ConfigParser.ConfigParser()


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
    print bcolors.HEADER + "TwitInt v0.9 - by Fabrizio 'Fabrimagic' Monaco"
    print
    print
    print bcolors.OKGREEN + "Usage python tweetfab [Options]"
    print
    print "Options:"
    print "-h, --help           Show help message and exit"
    print "-v, --verbose        Enable verbose output"
    print "-s, --string         Specify a search string"
    print "-r, --rate           Print rate limit status (JSON)"
    print "-c, --config         Use configuration file"
    print "-f, --follow         follow users with matching criteria tweets"
    print "-b, --block          block users with matching criteria tweets"
    print "-r, --report         report users with matching criteria as spam"

    sys.exit()

def main():
    TweetId=[]
    TweetText=[]
    LastTweetId=0
    LastTweetText=""
    ricerca = ""
    verbose = False
    configfile = ""
    follow = False
    report = False
    block = False
    logfile =""
    dologging = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:vrc:fbro:", ["help", "string=", "verbose", "rate", "config", "follow", "block", "report", "output"])
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
            temp = str(a)
            ricerca = temp.lower()
        elif o in ("-r", "--rate"):
            PrintRateLimit()
            sys.exit()
        elif o in ("-c", "--config"):
            configfile = a
        elif o in ("-f", "--follow"):
            follow = True
        elif o in ("-b", "--block"):
            block = True
        elif o in ("-r", "--report"):
            report = True
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

    if ricerca == "" or configfile == "":
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
    print bcolors.HEADER + "TwitInt v0.9 - by Fabrizio 'Fabrimagic' Monaco"
    print ""

    if verbose:
        print bcolors.OKBLUE + "[*] Consumer Key = " + bcolors.OKGREEN + configuration.consumer_key
        print bcolors.OKBLUE + "[*] Consumer Secret = " + bcolors.OKGREEN + configuration.consumer_secret
        print bcolors.OKBLUE + "[*] Access Token = " + bcolors.OKGREEN + configuration.access_token
        print bcolors.OKBLUE + "[*] Access Token Secret = " + bcolors.OKGREEN + configuration.access_token_secret
        print""
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
        if dologging:
            out_file.write(str(datetime.datetime.utcnow()) + " [*] Authenticated!\n")

    while True:
        try:
            public_tweets = tweepy.Cursor(api.search, q=ricerca).items(1)
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
            print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] User Id " + bcolors.OKGREEN + str(tweet.user.id)


    if verbose:
        print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] TwitInt Initialized"
        print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Last retrieved tweet id: " + bcolors.OKGREEN + str(LastTweetId)
        print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Last retrieved tweet text: "+ bcolors.OKGREEN + LastTweetText
    if dologging:
        out_file.write(str(datetime.datetime.utcnow()) + " [*] TwitInt Initialized\n")
        out_file.close()

    while True:
        if verbose:
            print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Sleeping 60 seconds"
        time.sleep(60)


        while True:
            try:
                if verbose:
                    print str(datetime.datetime.utcnow()) + " [*] Trying to get new tweets"

                public_tweets = tweepy.Cursor(api.search, q=ricerca, since_id=LastTweetId).items(10)
                break
            except tweepy.RateLimitError:
                print bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] ERROR: Rate Limit error encountered. Sleeping 15 minutes"
                PrintRateLimit()
                time.sleep(61*15)
                print bcolors.WARNING + str(datetime.datetime.utcnow()) + " [*] Retrying..."
                continue
            except tweepy.TweepError:
                print (bcolors.FAIL + str(datetime.datetime.utcnow()) + " [*] ERROR: Failed to establish a new connection")
                sleep(10)
                continue

        if public_tweets:
            try:
                out_file = open(logfile, "a")
            except:
                print "[*] Error while opening logfile"
                sys.exit()

            listatweet = []
            testotmp=""
            for tweet in public_tweets:
                listatweet.append(tweet.id)
                LastTweetId = listatweet[0]
                LastTweetText = tweet.text.lower()
#                testotmp = unicodedata.normalize('NFDK', tweet.text).encode('ascii', 'ignore')
#                testotmp = unicode(tweet.text)

                if int(LastTweetText.find(ricerca)) != -1:
                    if verbose:
                        print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + bcolors.HEADER + " [*] Found new tweet matching selected criteria: " + bcolors.OKGREEN+ tweet.text)
                        print bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] User Id: " + bcolors.OKGREEN + str(tweet.user.id)
                        print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] User Screen Name: " + bcolors.OKGREEN + tweet.user.screen_name)
                    if dologging:
                        out_file.write('------------------------------------------------------------------------------------------\n')
                        out_file.write(str(datetime.datetime.utcnow()))
                        out_file.write(' [*] ')
                        out_file.write(tweet.text.encode('utf8'))
                        out_file.write('\n')
                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] Originating user id: ' + str(tweet.user.id) + '\n')
                        out_file.write(str(datetime.datetime.utcnow()) + ' [*] Originating user screen name: ' + str(tweet.user.screen_name) + '\n')
                    if follow:
                        api.create_friendship(id=tweet.user.id)
                        if verbose:
                            print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + " [*] Just followed User: " + bcolors.OKGREEN + tweet.user.screen_name)
                        if dologging:
                            out_file.write(str(datetime.datetime.utcnow()) + ' [*] Just followed User: ' + str(tweet.user.screen_name) + '\n')
                    if block:
                        api.create.block(id=tweet.user.id)
                        if dologging:
                            out_file.write(str(datetime.datetime.utcnow()) + ' [*] Blocked User: ' + str(tweet.user.screen_name) + '\n')
                        if verbose:
                            print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + ' [*] Blocked User: ' + bcolors.OKGREEN + tweet.user.screen_name)
                    if report:
                        api.report_spam(id=tweet.user.id)
                        if verbose:
                            print (bcolors.OKBLUE + str(datetime.datetime.utcnow()) + ' [*] Reported spam. User: ' + bcolors.OKGREEN + tweet.user.screen_name)
                        if dologging:
                            out_file.write(str(datetime.datetime.utcnow()) + ' [*] Reported spam. User: ' + str(tweet.user.screen_name) + '\n')

            out_file.close()

if __name__ == "__main__":
    main()

