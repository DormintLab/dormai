import os
from typing import Optional
from pathlib import Path
import yaml
from pydantic import BaseModel, create_model, Field


class DormAI(object):
    def __init__(self,
                 dormai_config_path: Optional[Path] = None,
                 pipe_id: Optional[str] = None):
        super(DormAI, self).__init__()
        if dormai_config_path is None:
            dormai_config_path = Path.cwd() / "dormai.yml"
        self.dormai_config_path = dormai_config_path
        self.dormai_config = yaml.safe_load(Path(dormai_config_path).read_text())

        if "ENV" not in self.dormai_config:
            raise RuntimeError(f"Variable 'ENV' not found in dormai.yml")

        if pipe_id is None:
            pipe_id = os.environ.get("DORMINT_PIPE_ID")
        if pipe_id is None:
            raise RuntimeError("No DORMINT_PIPE_ID found neither in ENVIRON nor inline.")
        self.pipe_id = str(pipe_id)

        self.settings = {env_key: os.environ.get(env_key, "") if env_dtype == "string" else int(os.environ.get(env_key, 0))
                         for env_key, env_dtype in self.dormai_config.get("ENV", {}).items()}
        self.InputData = create_model("InputData",
                                      **{
                                          inp_name: ((str if inp_dtype == "string" else int),
                                                     Field(...))
                                          for inp_name, inp_dtype in self.dormai_config.get("INPUTS", {}).items()
                                      })

        self.OutputData = create_model("InputData",
                                       **{
                                           out_name: ((str if out_dtype == "string" else int),
                                                      Field(...))
                                           for out_name, out_dtype in self.dormai_config.get("OUTPUTS", {}).items()
                                       })

        self.ContextData = create_model("ContextData",
                                        **{
                                            ctx_name: ((str if ctx_dtype == "string" else int),
                                                       Field(...))
                                            for ctx_name, ctx_dtype in self.dormai_config.get("CONTEXT", {}).items()
                                        })
