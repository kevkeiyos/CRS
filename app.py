from flask import Flask, request, render_template
import nltk
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dictionary import Dictionary
import sys
from twython import Twython


app = Flask(__name__, static_url_path='/static')

app.secret_key = "nothing"

nltk.download('stopwords')

set(stopwords.words('english'))

# twitter creds
APP_KEY = 'jvGdO8lPTLlYRJJshTzhK4pvw'
APP_SECRET = 'Jv0BhsZAHglNITS4qKmvhcQppLxtzhfpj4CYXAyrShLxsxVrnV'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

class SentimentScore:
    def __init__(self, positive_tweets, negative_tweets, neutral_tweets):

        self.positive_tweets = positive_tweets
        self.negative_tweets = negative_tweets
        self.neutral_tweets = neutral_tweets

        self.neg = len(negative_tweets)
        self.pos = len(positive_tweets)
        self.neut = len(neutral_tweets)

dictionaryN = Dictionary('negative-words.txt')

dictionaryP = Dictionary('positive-words.txt')

def sentiment(tweet):

    negative_score = 0
    positive_score = 0

    tokenizer = nltk.tokenize.TweetTokenizer()
    tweet_words = tokenizer.tokenize(tweet)

    for word in tweet_words:
        negative_score += dictionaryN.check(word)

    for word in tweet_words:
        positive_score += dictionaryP.check(word)

    if negative_score > positive_score:
        return 'negative'
    elif negative_score == positive_score:
        return 'neutral'
    else:
        return 'positive'

def sentiment_analysis(tweets):

    negative_tweets = []
    positive_tweets = []
    neutral_tweets = []

    for tweet in tweets:

        res = sentiment(tweet['text'])

        if res == 'negative':
            negative_tweets.append(tweet['text'])
        elif res == 'positive':
            positive_tweets.append(tweet['text'])
        else:
            neutral_tweets.append(tweet['text'])

    return SentimentScore(positive_tweets, negative_tweets, neutral_tweets)

@app.route("/")
def index():
	return render_template("home.html")

@app.route('/', methods=['POST'])
def post():
    stop_words = stopwords.words()
    text = request.form['text'].lower()

    doc = ' '.join([word for word in text.split() if word not in stop_words])

    sentiment_intensity_analysis = SentimentIntensityAnalyzer() #init the sentiment analyzer
    score = sentiment_intensity_analysis.polarity_scores(text=doc)
    compound = round((1 + score['compound'])/2, 2)

    return render_template('home.html', result=compound, text=text)


@app.route("/root", methods=["POST", "GET"])
def root():

    if request.method == "POST":

        user_timeline = twitter.get_user_timeline(screen_name=request.form['twitter_username'], count = 100)

        return render_template("result.html", result=sentiment_analysis(user_timeline), username=request.form['twitter_username'])
    else:
        return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
	app.run(port=5000, debug=True, threaded=True)