import asyncio
import time
from pathlib import Path


# Function to parse the server list file
def parse_server_list(file_path):
    servers = []
    with Path.open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            if line.strip():
                server_info = line.strip().split("#")[0].split("@")[-1].split(":")
                servers.append((server_info[0], server_info[1]))  # (IP, Port)
    return servers


async def wait_host_port(host, port, duration=10, delay=2):
    """Repeatedly try if a port on a host is open until duration seconds passed.

    Parameters
    ----------
    host : str
        host ip address or hostname
    port : int
        port number
    duration : int, optional
        Total duration in seconds to wait, by default 10
    delay : int, optional
        delay in seconds between each try, by default 2

    Returns
    -------
    awaitable bool

    """
    tmax = time.time() + duration
    while time.time() < tmax:
        try:
            _reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=5)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            if delay:
                await asyncio.sleep(delay)
    return False


# Main function to run the pings
async def main(file_path):
    servers = parse_server_list(file_path)
    tasks = [wait_host_port(ip, port) for ip, port in servers]
    results = await asyncio.gather(*tasks)
    available_servers = [
        f"{ip}:{port}" for result, (ip, port) in zip(results, servers, strict=False) if result
    ]
    with Path.open(file_path) as source:
        good_servers = [
            line for line in source.readlines() for ip_port in available_servers if ip_port in line.strip()
        ]

        with Path.open(file_path, "w") as source2:
            source2.write("".join(good_servers))


# Execute the script
if __name__ == "__main__":
    file_path = "ss.txt"  # Path to your server list file
    asyncio.run(main(file_path))
