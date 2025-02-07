import os
from pathlib import Path
from typing import Optional, Tuple, Type, TypeVar

import httpx
import yaml
from pydantic import BaseModel, Field, create_model

BaseModelChildType = TypeVar("BaseModelChildType", bound=BaseModel)


class DormAI(object):
    InputData: Type[BaseModelChildType]
    OutputData: Type[BaseModelChildType]
    ContextData: Type[BaseModelChildType]

    def __init__(
        self,
        dormai_config_path: Optional[Path] = None,
        pipe_id: Optional[str] = None,
        **kwargs,
    ):
        super(DormAI, self).__init__()
        if dormai_config_path is None:
            dormai_config_path = Path.cwd() / "dormai.yml"
        self.dormai_config_path = dormai_config_path
        self.dormai_config = yaml.safe_load(Path(dormai_config_path).read_text())

        if "ENV" not in self.dormai_config:
            raise RuntimeError("Variable 'ENV' not found in dormai.yml")

        if pipe_id is None:
            pipe_id = os.environ.get("DORMINT_PIPE_ID")
        if pipe_id is None:
            raise RuntimeError(
                "No DORMINT_PIPE_ID found neither in ENVIRON nor inline."
            )
        self.pipe_id = str(pipe_id)

        self.settings = {
            env_key: os.environ.get(env_key, "")
            if env_dtype == "string"
            else int(os.environ.get(env_key, 0))
            for env_key, env_dtype in self.dormai_config.get("ENV", {}).items()
        }

        self.client = httpx.Client(**kwargs)

        if DormAI.InputData is None:
            DormAI.InputData = create_model(
                "InputData",
                **{
                    inp_name: ((str if inp_dtype == "string" else int), Field(...))
                    for inp_name, inp_dtype in self.dormai_config.get(
                        "INPUTS", {}
                    ).items()
                },
                extra='allow'
            )

        if DormAI.OutputData is None:
            DormAI.OutputData = create_model(
                "OutputData",
                **{
                    out_name: ((str if out_dtype == "string" else int), Field(...))
                    for out_name, out_dtype in self.dormai_config.get(
                        "OUTPUTS", {}
                    ).items()
                },
                extra='allow'
            )

        if DormAI.ContextData is None:
            DormAI.ContextData = create_model(
                "ContextData",
                **{
                    ctx_name: ((str if ctx_dtype == "string" else int), Field(...))
                    for ctx_name, ctx_dtype in self.dormai_config.get(
                        "CONTEXT", {}
                    ).items()
                },
                extra='allow'
            )

    def send_event(self, output: "DormAI.OutputData", context: "DormAI.ContextData"):
        resp = self.client.post(
            f"https://api.agents.dormint.io/api/event/{self.pipe_id}",
            json={"data": output.model_dump(), "context": context.model_dump()},
        )
        resp.raise_for_status()

    def receive_event(self) -> Tuple["DormAI.InputData", "DormAI.ContextData"]:
        resp = self.client.get(f"https://api.agents.dormint.io/api/event/{self.pipe_id}")
        resp.raise_for_status()
        result = resp.json()
        return self.InputData.model_validate(
            result["data"]
        ), self.ContextData.model_validate(result["context"])
