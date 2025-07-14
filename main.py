from matplotlib import pyplot as plt
import csv
from datetime import datetime
from dataclasses import dataclass


@dataclass
class priceInfo:
    date: str  # ideally lets make this datetime
    price: float


prediction_days = 365 * 3
sample_period = 30
start_period = 30
end_period = 180

prices = []
differences = []

best_diff = 999999999
best_index = 0
best_period = 0
breakindex = 999999999999999999

# make an autodownloader if btc.csv does not exist
# possibly using selenium or requests
# could use different csv source if possible

with open('btc.csv', newline='') as csvfile:
    # what is spam reader
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')

    i = -1
    started = False
    for row in spamreader:
        i += 1
        if i == 0:
            continue
        date = row[0].split(',')[0]
        if date == "2014-01-01":
            started = True  # start date - set after priceusd first appears - required
        # if date == "2020-01-01": breakindex = i # end date - optional
        if not started:
            continue
        # doge: 60, litecoin: 62, btc: 68
        price = row[0].split(',')[68]
        if price == '':
            continue
        price = float(price)
        priceinfo = priceInfo(date, price)
        currentprice = price
        startdate = date
        prices.append(priceinfo)

for sample_period in range(start_period, end_period):
    count = 0  # what for
    currentset = []
    currentprices = []
    currentdates = []
    del currentset[:]
    del currentprices[:]
    del currentdates[:]
    del differences[:]
    i = len(prices) - sample_period - 2
    while i < len(prices) - 1:
        i += 1
        count += 1
        currentset.append(prices[i])
        currentprices.append(prices[i].price)
        currentdates.append(prices[i].date)
    currentprices.pop()
    currentdates.pop()
    for i in range(sample_period + 1):
        if i == 0:
            continue
        lastprice = currentset[i - 1].price
        thisprice = currentset[i].price
        increase = thisprice - lastprice
        price_diff_percent = increase / lastprice * 100
        differences.append(price_diff_percent)

    startpoint = len(prices) - sample_period * 2
    done = False
    while not done:
        if startpoint < 0:
            break

        if startpoint > breakindex:
            startpoint -= sample_period
            continue

        thesedifferences = []
        del thesedifferences[:]
        # get price differences for this period
        for i in range(sample_period + 1):
            if i == 0:
                continue
                # we might not have to do this if the range is modified
            index = startpoint + i
            lastprice = prices[index - 1].price
            thisprice = prices[index].price
            increase = thisprice - lastprice
            price_diff_percent = increase / lastprice * 100
            thesedifferences.append(price_diff_percent)

        # see how close they match to the current period
        tot_percent_diff = 0
        for j, difference in enumerate(differences):
            percent_diff = difference - thesedifferences[j]
            tot_percent_diff += percent_diff

        avg_diff = tot_percent_diff / sample_period
        avg_diff = abs(avg_diff)
        if avg_diff < best_diff:
            best_diff = avg_diff
            best_index = startpoint
            best_period = sample_period
            best_current = list(currentprices)
            best_currentdates = list(currentdates)

        startpoint -= sample_period

currentprices = list(best_current)
currentdates = list(best_currentdates)
i = best_index - 1
j = -1
bestprices = []
del bestprices[:]
bestdates = []
del bestdates[:]
while i < best_index + best_period - 1:
    i += 1
    j += 1
    bestprices.append(prices[i].price)
    bestdates.append(prices[i].date)
bestfuture = []
bestfutureprices = []
bestfuturedates = []
currentfutureprices = []
currentfuturedates = []
best_differences = []
i = -1

while i < prediction_days - 1:
    i += 1
    index = best_index + best_period + i
    if index > len(prices) - 1:
        break
    #print(best_index, best_period, i, len(prices))
    futureprice = prices[best_index + best_period + i]
    bestfuture.append(futureprice)
    bestfutureprices.append(futureprice.price)
    bestfuturedates.append(futureprice.date)
    lastprice = prices[best_index + best_period + i - 1].price
    thisprice = prices[best_index + best_period + i].price
    increase = thisprice - lastprice
    price_diff_percent = increase / lastprice * 100
    best_differences.append(price_diff_percent)
currentfuture = []
lastprice = currentprices[best_period - 1]
for j, future in enumerate(bestfuture):
    bestprice = future.price
    futureprice = bestprice
    if j == 0:
        futureprice = lastprice
    else:
        futureprice = lastprice + lastprice * (best_differences[j] / 100)
    lastprice = futureprice
    currentfutureprices.append(futureprice)
    mydate = datetime.strptime(startdate, "%Y-%m-%d")
    ts = mydate.timestamp()
    realts = ts + 60 * 60 * 24 * j
    realdate = datetime.fromtimestamp(realts)
    realdate = str(realdate).split(' ')[0]
    currentfuturedates.append(str(realdate))


allcurrentdates = currentdates + currentfuturedates
allcurrentprices = currentprices + currentfutureprices
allbestdates = bestdates + bestfuturedates
allbestprices = bestprices + bestfutureprices

print(bestdates[0])

# ik what you're trying to do here but we should use built in functions for this
peak = 0
bottom = 999999999999999999999999
peakdate = ''
bottomdate = ''
lastdate = ''
lastprice = 0

i = best_period
while i < best_period + prediction_days - 1:
    i += 1
    if i > len(allcurrentdates) - 1:
        break
    if allcurrentprices[i] > peak:
        peak = allcurrentprices[i]
        peakdate = allcurrentdates[i]
    if allcurrentprices[i] < bottom:
        bottom = allcurrentprices[i]
        bottomdate = allcurrentdates[i]
    lastdate = allcurrentdates[i]
    lastprice = allcurrentprices[i]

print("Peak:", peakdate, peak)
print("Bottom:", bottomdate, bottom)
print("Final:", lastdate, lastprice)

fig, ax1 = plt.subplots()
ax1.plot(allcurrentdates, allcurrentprices, color='red')
ax2 = ax1.twinx()
ax2.plot(allcurrentdates, allbestprices, color='blue')
plt.axvline(x=best_period, color='green')
plt.show()
