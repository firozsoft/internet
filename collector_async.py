import asyncio
import base64
import logging
from pathlib import Path

import aiohttp
from sources import urls

# Configure logging
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
# /Configure logging

western_counties = (
    "🇺🇸",
    "🇬🇧",
    "🇹🇷",
    # "🇩🇪",
    # "🇫🇷",
    "🇳🇱",
    "🇦🇪",
)


async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            return await response.read()
    except aiohttp.ClientError as e:
        # Log URL and error message if there's a URL error
        msg = f"Error accessing {url}: {e}"
        logger.exception(msg)


async def parse_data(session, url):
    data = await fetch_url(session, url)
    try:
        # Decode data if it's base64 encoded
        return base64.b64decode(data).decode("utf-8")
    except UnicodeDecodeError:
        # If not base64 encoded, use the data as is
        return data.decode("utf-8")
    except Exception as e:
        # Log URL and error message if there's a URL error
        msg = f"Error parsing data from {url}: {e}"
        logger.exception(msg)


async def main(urls):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [parse_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    filtered_data = [
        line
        for result in results
        if result
        for line in result.splitlines()
        if line.startswith("ss://") and any(True for flag in western_counties if flag in line)
    ]

    unique_configs = set()
    for line in filtered_data:
        try:
            ip_port = line.split("@")[1].split("#")[0]
            if any(True for config in unique_configs if ip_port in config):
                continue
            unique_configs.add(line)
        except Exception as err:
            msg = f"{err}"
            logger.exception(msg)
    return unique_configs


if __name__ == "__main__":
    filtered_data = asyncio.run(main(urls))

    # Write b64encoded data to file
    with Path("./ss.txt").open("w") as fl:
        fl.write("\n".join(filtered_data))

    logger.info("Reading sources has been completed successfully!")
