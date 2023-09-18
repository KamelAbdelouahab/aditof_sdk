
import numpy as np
import multiprocessing
import coloredlogs, logging
import time
logging.basicConfig()
log = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)
coloredlogs.install()
import queue

class StreamAggregator(multiprocessing.Process):
    def __init__(self, q_in, q_out, width=640, height=480):
        super().__init__()
        self.queue_in   = q_in
        self.queue_out  = q_out
        self.num_queues = len(self.queue_in)
        self.data_out   = np.zeros((height, self.num_queues*width, 3), dtype=np.uint8)
        self.width = width
        self.height = height
        log.info(f"Aggregating {self.num_queues} streams")
        log.info(f"Output data shape: {self.data_out.shape}")
        log.info(f"thread StreamAggregator Ready !")
    
    def run(self):
        log.info("Running ...")
        while True:
            log.debug("Got a frame")
            start = time.time()
            for i in range(self.num_queues):
                # try:
                self.data_out[:, i*self.width:(i+1)*self.width, :] = self.queue_in[i].get()
                # except queue.Empty:
                #     log.warning("Queue Empty")                
            end = time.time()
            log.debug(f"Copy time = {1000*(end-start):.2f}ms")
            self.queue_out.put(self.data_out)
            log.debug("Aggregated ")
        