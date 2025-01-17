import subprocess
import argparse
import re
import json


def validate_host(host: str) -> bool:

    ip_match: bool = re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", host)

    if not ip_match:
        return False

    return True


def ping(host: str) -> dict | None:

    rtt: dict = {}
    packet_loss: float = 0.0
    try:
        os_output: str = subprocess.check_output(
            ["ping", "-c", "10", host], universal_newlines=True
        )

        for line in os_output.split("\n"):

            if "packets" in line:
                packet_loss = line.split(",")[2].split(" ")[1].replace("%", "")
            if "round-trip" in line or "rtt" in line:

                rtt_line: str = line.split("=")[1].split("/")

                rtt: dict = {
                    "rtt_min": rtt_line[0].strip(),
                    "rtt_avg": rtt_line[1],
                    "rtt_max": rtt_line[2],
                    "rtt_mdev": rtt_line[3].split(" ")[0],
                }

        if not rtt or not packet_loss:
            return None

        return rtt | {"packet_loss": packet_loss}

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def iperf(cmd_stream: list[str]) -> dict | None:

    throughput: dict = {}
    try:
        os_output: str = subprocess.check_output(cmd_stream, universal_newlines=True)

        iperf_output: list[str] = os_output.split("\n")
        for line in iperf_output:
            line_numbers: list[str] = [x for x in line.split(" ") if x.isdigit()]
            if "sender" in line:
                send_rate: str = line_numbers[1]
                throughput["send_rate"] = send_rate

            if "receiver" in line:
                receive_rate: str = line_numbers[1]
                throughput["receive_rate"] = receive_rate

        if not throughput:
            return None

        return throughput

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def measure_network_performance(host: str) -> dict | None:

    ping_result: dict | None = ping(host)

    # -b 0 -u will be for UDP & -R for reverse
    iperf_result: dict | None = iperf(["iperf3", "-c", host])

    if ping_result and iperf_result:
        results = {**ping_result, **iperf_result}
    else:
        results = None

    return results


def main() -> None:

    parser = argparse.ArgumentParser(description="NetC - Network Checker")

    parser.add_argument("--host", "-H", help="Target network host")

    args = parser.parse_args()

    if not args.host:
        print(
            "No host provided, please pass an IPV4 address using the --host flag\n e.g. python3 -m netc.test --host 192.168.1.100"
        )
        exit()

    host: str = args.host

    if not validate_host(host):
        print("Invalid host provided, please pass a valid IPV4 address")
        exit()

    results: dict | None = measure_network_performance(host)

    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()
