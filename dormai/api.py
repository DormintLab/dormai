from typing import Optional
from pathlib import Path


class DormAI(object):
    def __init__(self,
                 dormai_config_path: Optional[Path] = None,
                 pipe_id: Optional[str] = None):
        super(DormAI, self).__init__()
        self.pipe_id = pipe_id
        self.dormai_config_path = dormai_config_path
