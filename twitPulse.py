import snscrape.modules.twitter as twitter
import pprint
import datetime
import matplotlib.pyplot as plt

TODAY = datetime.datetime.now()


def plotPulse(keyword, days):
    """This is a script that plots the occurrence of a word in Tweets with respect to days
    example useage: plotPulse("wwg1wga", 30)
    """
    startDate = TODAY - datetime.timedelta(days=days)
    tomorrow = TODAY + datetime.timedelta(days=1)
    tweets = {}
    for i, tweet in enumerate(
        twitter.TwitterSearchScraper(
            f'{keyword} since:{startDate.date()} until:{tomorrow.date()} lang:"en" '
        ).get_items()
    ):
        date = tweet.date.date()
        if date not in tweets:
            tweets[date] = 1
        else:
            tweets[date] += 1

    del tweets[TODAY.date()]  # today is a partial day
    pprint.pprint(tweets)

    plt.title(f"Occurances of '{keyword.upper()}' on Twitter")
    plt.plot_date(tweets.keys(), tweets.values(), linestyle="solid")
    plt.tick_params(axis="x", which="major", labelsize=6)
    plt.tight_layout()
    plt.show()
