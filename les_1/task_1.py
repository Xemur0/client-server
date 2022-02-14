import ipaddress
import subprocess

from les_1.task_2 import RangePing


class HostingPing(RangePing):
    def host_ping(self, ip_addresses):
        reachable = []
        unreachable = []

        for ip in ip_addresses:
            address = str(ipaddress.ip_address(ip))
            result = subprocess.run(["ping", "-n", "1", address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                print(f'{ip} Узел доступен')
                reachable.append(ip)
            else:
                print(f'{ip} Узел недоступен')
                unreachable.append(ip)

        return reachable, unreachable
