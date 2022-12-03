"""This is file has two scripts that plot the occurrence of a word in Tweets with respect to days.
There is a single and a multithreaded version.  The multithreaded version is considerably faster for 
searches over many days.

Note that very common terms, like "trump" are impossibly long for even one day.
"""
from snscrape.modules.twitter import TwitterSearchScraper
import pprint
import datetime
import matplotlib.pyplot as plt
import threading

TODAY = datetime.datetime.now()


class scrapeThread(threading.Thread):
    """A thread that scrapes Twitter tiven a search string counting the results.
    The counts are stored in a dictionary with the day being the key
    """
    def __init__(self, searchString):
        threading.Thread.__init__(self)
        self.searchString = searchString
        self.search = None
        self.tweets = {}

    def run(self):
        search = TwitterSearchScraper(self.searchString).get_items()
        for tweet in search:
            date = tweet.date.date()
            if date not in self.tweets:
                self.tweets[date] = 1
            else:
                self.tweets[date] += 1


def plotPulseMT(keyword, days):
    """This is a script that plots the occurrence of a word in Tweets with respect to days
    example useage: plotPulseMT("wwg1wga", 30)
    This spawns a thread for each day.
    """
    startDate = TODAY - datetime.timedelta(days=1)
    endDate = TODAY + datetime.timedelta(days=1)
    threads = []
    for _ in range(days):
        searchString = (
            f' {keyword} since:{startDate.date()} until:{endDate.date()} lang:"en" '
        )
        threadName = str(startDate.date())
        thread = scrapeThread(searchString)
        thread.start()
        threads.append(thread)
        endDate = startDate
        startDate = endDate - datetime.timedelta(days=1)

    # wait for all the threads to finish
    for thread in threads:
        thread.join()

    # combine the results
    results = {}
    for thread in threads:
        for day in thread.tweets:
            if not day in results:
                results[day] = thread.tweets[day]
            else:
                results[day] += thread.tweets[day]

    del results[TODAY.date()]  # today is a partial day, delete this data
    pprint.pprint(results)

    plt.title(f"Occurances of '{keyword.upper()}' on Twitter")
    plt.plot_date(results.keys(), results.values(), linestyle="solid")
    plt.tick_params(axis="x", which="major", labelsize=6)
    plt.tight_layout()
    plt.show()


def plotPulseST(keyword, days):
    """This is a script that plots the occurrence of a word in Tweets with respect to days
    example useage: plotPulseST("wwg1wga", 30)
    This single threaded example is not recommended over the multithreaded version.
    It is only retained because it is simple to read.  It does the same thing, but one
    day at a time.
    """
    startDate = TODAY - datetime.timedelta(days=days)
    tomorrow = TODAY + datetime.timedelta(days=1)
    tweets = {}
    search = TwitterSearchScraper(
        f' {keyword} since:{startDate.date()} until:{tomorrow.date()} lang:"en" '
    ).get_items()
    for tweet in search:
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog="twitPulse", description="Count occurances of a keyword in twitter and plot versus days"
    )
    parser.add_argument("-d", "--day", type=int, default=1, help="The days to search (default=1)")
    parser.add_argument("-k", "--keyword", required=True, help="The keyword to search for")
    args = parser.parse_args()

    if args.day == 1:
        plotPulseST(args.keyword, args.day)
    else:
        plotPulseMT(args.keyword, args.day)
