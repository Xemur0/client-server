import ipaddress


class RangePing:
    def host_range_ping(self, ip_addresses):
        ip_list = []
        for ip_address in ip_addresses:
            if "-" in ip_address:
                start, end = ip_address.split("-")
                if "." not in end:
                    end = ".".join(start.split(".")[:-1] + [end])
                start = ipaddress.ip_address(start)
                end = ipaddress.ip_address(end)
                for ip in range(int(start), int(end) + 1):
                    ip_list.append(str(ipaddress.ip_address(ip)))
            else:
                ip_list.append(str(ip_address))
        return ip_list
