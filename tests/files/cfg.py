from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import yaml


k, p = 1, 2


class Test:
    def __init__(self, x=5):
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


for i in range(3):
    kmeans = KMeans(n_clusters=i)

for j in range(1, 5):
    kmeans = KMeans(n_clusters=j)

for c in range(1, 10, 2):
    kmeans = KMeans(n_clusters=c)


def create_kmeans(solver="lbfgs"):
    logistic_reg = LogisticRegression(solver=solver)
    return logistic_reg


anchors = [x for x in range(5, 10)]
anchors = [x for x in range(1, 10, 2)]
anchors = [x for x in range(3)]

opts = yaml.safe_load(open("test.yaml"))

kwargs = {
    "min_samples_leaf": 1,
    "max_leaf_nodes": 2
}
