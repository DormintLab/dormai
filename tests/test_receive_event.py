import argparse
import asyncio
from pathlib import Path
from dormai.async_api import AsyncDormAI


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("pipe_id")
    return parser.parse_args()


async def main(pipe_id):
    async with AsyncDormAI(Path("./dormai.yml"),
                           pipe_id=pipe_id) as dormai:
        while True:
            inputs, context = await dormai.receive_event()
            if inputs is None:
                continue
            print("Inputs: ", inputs, "\n",
                  "Context: ", context)


if __name__ == "__main__":
    asyncio.run(main(**vars(parse_args())))
