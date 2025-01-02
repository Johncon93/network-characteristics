import os
import subprocess
import sys


def install_pip_requirements():

    try:

        if not os.path.isfile("requirements.txt"):
            print("requirements.txt not found")
            sys.exit(1)

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )

        print("Requirements installed successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(e.returncode)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def install_iperf3():
    try:
        subprocess.check_call(["sudo", "apt-get", "update"])

        subprocess.check_call(["sudo", "apt-get", "install", "iperf3"])

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(e.returncode)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    install_pip_requirements()
    install_iperf3()
