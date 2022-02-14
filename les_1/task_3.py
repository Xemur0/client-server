from tabulate import tabulate

from les_1.task_1 import HostingPing


class TabulatePingTab(HostingPing):
    def host_range_ping_tab(self, list_ip):
        table = {"Reachable": list_ip[0], "Unreachable": list_ip[1]}
        print(tabulate(table, headers="keys"))


#
if __name__ == "__main__":
    obj = TabulatePingTab()
    obj.host_range_ping_tab(obj.host_ping(obj.host_range_ping(['192.168.0.5', '127.0.0.1', '8.8.4.4', '1.1.1.1-3', '172.21.41.128-172.21.41.132'])))
