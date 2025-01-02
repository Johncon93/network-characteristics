# network-characteristics

This script has been created to benchmark network performance between nodes within a virtualised network containing traditional, SDN, and Hybrid-SDN infrastructure.

Each node initiates the script upon creation and begins listening for HTTP POST and Iperf3 requests which trigger a series of network-based performance tests between other nodes. 


### Installation

#### GNS3 Ubuntu Node Setup

```
cd ~
python3 -m venv venv
source venv/bin/activate
git clone https://github.com/Johncon93/network-characteristics.git
cd network-characteristics/
python3 -m netc.install
python3 -m netc
```

### Example Usage

Tests are initiated by sending a POST request to a node and providing a target host within the payload.

#### Example Response:
```
{
  "packet_loss": "0",
  "receive_rate": "587",
  "rtt_avg": "2.470",
  "rtt_max": "3.679",
  "rtt_mdev": "1.066",
  "rtt_min": "0.945",
  "send_rate": "588"
}
```

#### Test a Node Using Curl:
``` 
curl -X POST http://192.168.0.231:5000/netc -H "Content-Type: application/json" -d '{"host":"192.168.0.53"}' 
```

#### Test a Node Using Requests:
```python 
import requests
import json

def conduct_test(test_server: str, target_server: str) -> dict | None:

    payload: dict = {
        "host": target_server,
    }

    response = requests.post(f"http://{test_server}:5000/netc", json=payload)

    if not response:
        return None

    return response.json()


result: dict | None = conduct_test(
    test_server="192.168.0.181", target_server="192.168.0.53"
)
```

#### Test Servers Using a Basic Orchestrator:
```python
import json
import requests


server_list: list[str] = [
    "192.168.0.53",
    "192.168.0.181",
]


def conduct_test(test_server: str, target_server: str) -> dict | None:

    payload: dict = {
        "host": target_server,
    }

    response = requests.post(f"http://{test_server}:5000/netc", json=payload)

    if not response:
        return None

    return response.json()


def prepare_tests(test_server: str) -> list[dict] | list:

    test_results: list = []
    for server in server_list:
        if server == test_server:
            continue

        response: dict | None = conduct_test(
            test_server=test_server, target_server=server
        )
        if not response:
            continue

        response["test_server"] = test_server
        response["target_server"] = server

        test_results.append(response)

    return test_results


def main() -> None:

    test_results: list = []
    for server in server_list:
        test_result: list[dict] | list = prepare_tests(server)

        if not test_result:
            continue

        test_results.extend(test_result)

    with open("test_results.json", "w") as file:
        json.dump(test_results, file)


if __name__ == "__main__":
    main()
```
