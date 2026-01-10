import os 
import subprocess

def run_sudo(cmd, password):
    subprocess.run(
        f"sudo -S sh -c '{cmd}'",
        shell=True,
        input=password + "\n",
        text=True,
        check=True,
    )

def shaping(download_mbps, upload_mbps, qdisc, password):
    """
    HTB-based shaping with AQM.
    Rates are in Mbps.

    Supported queuing disciplines:
      pfifo, bfifo, red, gred, pie, codel, fq_codel, fq, cake
    """
    run_sudo(
        f"tc qdisc del dev veth2 root 2>/dev/null || true && "
        f"tc qdisc add dev veth2 root handle 1: htb default 10 && "
        f"tc class add dev veth2 parent 1: classid 1:10 htb "
        f"rate {download_mbps}Mbit ceil {download_mbps}Mbit && "
        f"tc qdisc add dev veth2 parent 1:10 {qdisc}",
        password,
    )

    run_sudo(
        f"tc qdisc del dev veth4 root 2>/dev/null || true && "
        f"tc qdisc add dev veth4 root handle 1: htb default 10 && "
        f"tc class add dev veth4 parent 1: classid 1:10 htb "
        f"rate {upload_mbps}Mbit ceil {upload_mbps}Mbit && "
        f"tc qdisc add dev veth4 parent 1:10 {qdisc}",
        password,
    )

def latency(latency_ms, password):
    """
    Add base latency to veth6 using netem.
    latency_ms is in milliseconds.
    If latency_ms == 0, netem is removed.
    """
    if latency_ms == 0:
        run_sudo(
            "tc qdisc del dev veth6 root 2>/dev/null || true",
            password,
        )
    else:
        run_sudo(
            f"tc qdisc del dev veth6 root 2>/dev/null || true && "
            f"tc qdisc add dev veth6 root netem delay {latency_ms}ms",
            password,
        )