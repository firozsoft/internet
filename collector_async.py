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

western_counties = (
    # "US-",
    "GB-",
    "AE-",
)


async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            return await response.read()
    except aiohttp.ClientError as e:
        logger.error("Error accessing %s: %s", url, e)
        return None


async def parse_data(session, url):
    data = await fetch_url(session, url)
    if data is None:
        return None
    try:
        return base64.b64decode(data).decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8")
    except Exception as e:
        logger.error("Error parsing data from %s: %s", url, e)
    return None


async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [parse_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    filtered_lines = []
    for result in results:
        if result:
            for line in result.splitlines():
                if line.startswith("ss://") and any(flag in line for flag in western_counties):
                    filtered_lines.append(line)

    unique_configs = set()
    for line in filtered_lines:
        try:
            ip_port = line.split("@")[1].split("#")[0]
            if any(ip_port in config for config in unique_configs):
                continue
            unique_configs.add(line)
        except Exception as err:
            logger.error("Failed to extract IP/Port: %s", err)
    return unique_configs


if __name__ == "__main__":
    filtered_configs = asyncio.run(main(urls))
    with Path("./ss.txt").open("w", encoding="utf-8") as fl:
        fl.write("\n".join(filtered_configs))
    logger.info("Reading sources has been completed successfully!")
