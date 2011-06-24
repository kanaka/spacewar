import random


# Upper half of gauss distribution
def half_gauss(start, end):
    found = 0
    while not found:
        num = random.gauss(start, (end-start)/3.0)
        if num >= start and num <= end:
            found = 1
    return num

counts = {}
for i in range(10,30):
    counts[i] = 0    

for i in range(100):
    counts[int(half_gauss(10, 30))] += 1

for i in range(10,30):
    print i, counts[i]
