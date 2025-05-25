import subprocess
import argparse
import re
import json
import time
import signal


def validate_host(host: str) -> bool:

    ip_match: bool = re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", host)

    if not ip_match:
        return False

    return True


def ping(host: str, test_time: int = 10, interval: float = 0.2) -> dict | None:

    rtt: dict = {}
    packet_loss: str = ""
    packets_transmitted: str = ""
    packets_received: str = ""
    wait_updates: list[str] = ["25%", "50%", "75%", "100%"]
    try:

        """
        os_output: str = subprocess.check_output(
            ["ping", "-c", "10", "-f", "-i", '', host], universal_newlines=True
        )
        """
        proc = subprocess.Popen(
            ["ping", "-f", "-i", str(interval), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        try:
            quarter_wait_time: float = test_time / 4

            for i in range(4):
                time.sleep(quarter_wait_time)
                print(f"{wait_updates[i]} completed")

            proc.send_signal(signal.SIGINT)
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()

        os_output = proc.stdout.read()

        for line in os_output.split("\n"):

            if "packet loss" in line:
                packet_loss = line.split(",")[2].split(" ")[1].replace("%", "")
                packets_transmitted = line.split(",")[0].split(" ")[0]
                packets_received = line.split(",")[1].split(" ")[1]

            if "round-trip" in line or "rtt" in line:

                rtt_line: str = line.split("=")[1].split("/")
                rtt: dict = {
                    "rtt_min": rtt_line[0].strip(),
                    "rtt_avg": rtt_line[1],
                    "rtt_max": rtt_line[2],
                    "rtt_mdev": rtt_line[3].split(" ")[0],
                    "ipg": rtt_line[4].split(" ")[1],
                    "ewma": rtt_line[5],
                }

        if not rtt or not packet_loss:
            return None

        return rtt | {
            "packet_loss": packet_loss,
            "packets_transmitted": packets_transmitted,
            "packets_received": packets_received,
        }

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
                send_rate_split: list = line.split("sec")
                send_rate_split = send_rate_split[1].split()
                if len(send_rate_split) < 2:
                    continue
                send_rate: str = send_rate_split[2]
                throughput["send_rate"] = send_rate

            if "receiver" in line:
                receive_rate_split: list = line.split("sec")
                receive_rate_split = receive_rate_split[1].split()
                if len(receive_rate_split) < 2:
                    continue
                receive_rate: str = receive_rate_split[2]
                throughput["receive_rate"] = receive_rate

        if not throughput:
            return None

        return throughput

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


def measure_network_performance(
    host: str, test_time: int = 10, interval: float = 0.2
) -> dict | None:

    ping_result: dict | None = ping(host, test_time, interval)

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
    parser.add_argument(
        "--time",
        "-t",
        type=int,
        default=10,
        help="Time in seconds to run the test (default: 10 seconds)",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=0.2,
        help="Interval in seconds between ping requests (default: 0.2 seconds)",
    )

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

    results: dict | None = measure_network_performance(
        host, test_time=args.time, interval=args.interval
    )

    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()
