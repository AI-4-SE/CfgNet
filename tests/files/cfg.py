import pandas as pd
from sklearn.cluster import KMeans


k, p = 1, 2


class Test:
    def __init__(self, x):
        self.x = x

    def update(self, z):
        self.x = z


bin_cols = ["is_male"]

z = "test"
z = "hello"


a = 3
if bin_cols:
    a = 4
else:
    a = 5


def outer_func(a):
    if a == 5:
        a = 6

    def inner_func(a):
        if a == 6:
            a = 7

    inner_func()


dataset = pd.read_csv("test.csv")
x = dataset.iloc[:, [3, 4]].values


for i in range(3):
    kmeans = KMeans(n_clusters=i)

for j in range(1, 5):
    kmeans = KMeans(n_clusters=j)

for c in range(1, 10, 2):
    kmeans = KMeans(n_clusters=c)
