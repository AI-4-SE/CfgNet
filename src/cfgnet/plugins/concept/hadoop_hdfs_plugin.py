import os
from cfgnet.plugins.file_type.hadoop_plugin import HadoopPlugin


class HadoopHdfsPlugin(HadoopPlugin):
    def __init__(self):
        super().__init__("hadoop-hdfs")

    def is_responsible(self, abs_file_path: str) -> bool:
        file_name = os.path.basename(abs_file_path)
        return any(
            file_name == name for name in ["hdfs-site.xml", "hdfs-default.xml"]
        )
