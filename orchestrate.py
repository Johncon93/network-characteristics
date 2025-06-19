import json
import requests
import datetime
import os

""" SDN
server_list: list[str] = [
    "192.168.88.100",
    "192.168.88.101",
]
"""

server_list: list[str] = [
    "192.168.88.100",
    "192.168.88.101",
]

test_types: dict = {
    "low": {  # 10 packets per second
        "time_seconds": 60,
        "interval_seconds": 0.1,
    },
    "medium": {  # 20 packets per second
        "time_seconds": 60,
        "interval_seconds": 0.05,
    },
    "high": {  # 100 packets per second
        "time_seconds": 60,
        "interval_seconds": 0.01,
    },
    "very_high": {  # Immediate
        "time_seconds": 60,
        "interval_seconds": 0.002,
    },
}


def generate_timestamp() -> str:
    """
    Generate a timestamp in the format YYYY-MM-DD HH:MM:SS
    """
    return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def conduct_test(
    test_server: str, target_server: str, time: int, interval: float
) -> dict | None:

    # 0.01 = 200 packets per second
    # 30 seconds = 6000 packets
    # 60 seconds = 12000 packets
    # 3600 seconds = 720000 packets
    payload: dict = {
        "host": target_server,
        "time": time,
        "interval": interval,
    }

    response = requests.post(f"http://{test_server}:5000/netc", json=payload)

    if not response:
        return None

    return response.json()


def write_individual_test_results(
    test_server: str, target_server: str, response: dict, timestamp: str, test_type: str
) -> None:

    try:

        filename: str = f"{timestamp}_{test_type}_{test_server}_{target_server}.json"
        with open(filename, "w") as file:
            json.dump(response, file, indent=4)
    except Exception as e:
        print(f"Error writing results for {test_server} to {target_server}: {e}")


def prepare_tests(test_server: str, test: str, test_values: dict) -> list[dict] | list:

    test_results: list = []
    for server in server_list:
        if server == test_server:
            continue

        print(f"Conducting {test} test from {test_server} to {server}")
        print(f"Test values: {test_values}")
        response: dict | None = conduct_test(
            test_server=test_server,
            target_server=server,
            time=test_values["time_seconds"],
            interval=test_values["interval_seconds"],
        )
        if not response:
            continue
        response["test_type"] = test
        response["test_server"] = test_server
        response["target_server"] = server
        write_individual_test_results(
            test_server=test_server,
            target_server=server,
            response=response,
            timestamp=generate_timestamp(),
            test_type=test,
        )
        test_results.append(response)

    return test_results


def main() -> None:

    start_time: str = generate_timestamp()
    test_results: list = []
    for server in server_list:
        for test in test_types:
            # Prepare and conduct tests
            if not server:
                continue

            test_result: list[dict] | list = prepare_tests(
                server, test=test, test_values=test_types[test]
            )

            if not test_result:
                continue

            test_results.extend(test_result)

    with open(f"{start_time}_test_results.json", "w") as file:
        json.dump(test_results, file, indent=4)


if __name__ == "__main__":
    main()
