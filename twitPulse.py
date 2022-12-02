from snscrape.modules.twitter import TwitterSearchScraper
import pprint
import datetime
import matplotlib.pyplot as plt
import threading

TODAY = datetime.datetime.now()


class scrapeThread(threading.Thread):
    def __init__(self, threadID, searchString):
        threading.Thread.__init__(self)
        self.threadID = threadID
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
        thread = scrapeThread(threadName, searchString)
        thread.start()
        threads.append(thread)
        endDate = startDate
        startDate = endDate - datetime.timedelta(days=1)

    # what for all the threads to finish
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

    del results[TODAY.date()]  # today is a partial day
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
