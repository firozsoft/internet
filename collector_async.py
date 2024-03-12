import asyncio
import base64
import logging

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
    "🇬🇧", "🇺🇸", 
    #"🇩🇪", "🇫🇷", "🇳🇱"
)


async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
    except aiohttp.ClientError as e:
        # Log URL and error message if there's a URL error
        logger.error(f"Error accessing {url}: {e}")


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
        logger.error(f"Error parsing data from {url}: {e}")


async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [parse_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        filtered_data = {
            line
            for result in results
            if result
            for line in result.splitlines()
            if line.startswith("ss://")
            and any(True for flag in western_counties if flag in line)
        }

        # Write b64encoded data to file
        with open("./ss.txt", "wb") as fl:
            fl.write(base64.b64encode("\n".join(filtered_data).encode()))


if __name__ == "__main__":
    asyncio.run(main(urls))
