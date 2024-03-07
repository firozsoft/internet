import base64
import logging
import urllib.error
import urllib.request

from sources import urls

# Configure logging
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
# /Configure logging

data = set()  # Initialize an empty set to store filtered data

for url in urls:
    try:
        with urllib.request.urlopen(url) as response:
            try:
                # Decode response if it's base64 encoded
                encoded_response = base64.b64decode(response.read()).decode("utf-8")
            except UnicodeDecodeError:
                # If not base64 encoded, use the response as is
                encoded_response = response.read()

            # Decoded response and Split into lines and filter relevant lines
            for line in encoded_response.splitlines():
                if line.startswith("ss:/") and ("🇺🇸" in line or "🇬🇧" in line):
                    data.add(line)
    except urllib.error.URLError as e:
        # Log URL and error message if there's a URL error
        logger.error(f"Error accessing {url}: {e}")

# Join filtered data lines into a single string
filtered_data = "\n".join(data)

# Write b64encoded data to file
with open("./ss.txt", "wb") as fl:
    fl.write(base64.b64encode(filtered_data.encode()))
