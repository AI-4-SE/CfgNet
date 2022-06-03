from keras.layers.core import Dropout
from keras.layers import Dense
import tensorflow as tf

writer = tf.python_io.TFRecordWriter("path/to/file")

with tf.Graph().as_default():
    q = tf.SparseConditionalAccumulator(
        tf.float32, name="Q", shape=tf.TensorShape([1, 5, 2, 8])
    )

spec = tf.python.trainingserver_lib.ClusterSpec({"ps": ["1"], "worker": ["2"]})
simple_resolver = tf.contrib.cluster_resolver.python.training.cluster_resolver.SimpleClusterResolver(
    spec
)

estm = tf.estimator.experimental.RNNEstimator(
    head=tf.estimator.RegressionHead(),
    sequence_feature_columns=["test"],
    units=[32, 16],
    cell_type="lstm",
)


dimension = Dense(512)

orientation = Dropout(0.5)
