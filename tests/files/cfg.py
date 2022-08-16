from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import yaml
import numpy as np
from sklearn.neighbors import NearestNeighbors


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

for s in range(1, 10, 2):
    kmeans = KMeans(n_clusters=s)


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


def extract_knn_patch(queries, pc, n_neighbors):
    knn_search = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto')
    knn_search.fit(pc)
    knn_idx = knn_search.kneighbors(queries, return_distance=False)
    k_patches = np.take(pc, knn_idx, axis=0)  # M, K, C
    return k_patches


C_range = np.geomspace(start=1e-7, stop=1e7)

for count, value in enumerate(C_range):
    lr_l2_C = LogisticRegression(penalty='l2', solver='liblinear', C=value)
