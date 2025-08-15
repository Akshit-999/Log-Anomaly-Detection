from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from typing import Tuple
from fetch_logs import tail_file  
import json


class DrainWrapper:
    def __init__(self, depth: int = 4, sim_threshold: float = 0.5):
        cfg = TemplateMinerConfig()

        cfg.profiling_enabled = False
        cfg.drain_depth = depth
        cfg.drain_sim_th = sim_threshold

        self.miner = TemplateMiner(config=cfg)

    def add_log_line(self, logline: str) -> Tuple[str, str]:
        """
        Add logline to the miner and return (template, template_id).
        Always returns the latest generalized template for the cluster.
        """
        result = self.miner.add_log_message(logline)
        cluster_id = result.get("cluster_id")
        template = result.get("template_mined", logline)
        return template, str(cluster_id)


# if __name__ == "__main__":
#     drain = DrainWrapper()

#     log_path = "/Users/akshitagrawal/Desktop/datasets/logproject/synthetic_logs.jsonl"
#     for line in tail_file(log_path):
#         try:
#             log_dict = json.loads(line)
#             log_msg = log_dict.get("log", line)  
#         except json.JSONDecodeError:
#             log_msg = line  

#         template, cluster_id = drain.add_log_line(log_msg)
#         print(template)
