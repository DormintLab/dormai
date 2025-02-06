import argparse
import asyncio
import json
from pathlib import Path
import httpx
from dormai.async_api import AsyncDormAI


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("pipe_id")
    parser.add_argument("message")
    parser.add_argument("context")
    return parser.parse_args()


async def main(pipe_id: str, message: str, context: str):
    key, value = message.split("=")
    context = json.loads(context)

    async with AsyncDormAI(Path("./dormai.yml"),
                           pipe_id=pipe_id) as dormai:
        data = dormai.OutputData.model_validate({key: value})
        context = dormai.ContextData.model_validate(context)
        print(data.model_dump(), context.model_dump())
        await dormai.send_event(data,
                                context)


if __name__ == "__main__":
    asyncio.run(main(**vars(parse_args())))
