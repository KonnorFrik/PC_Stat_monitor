import psutil
from psutil._common import bytes2human
from collections import namedtuple


class CPU:
    @staticmethod
    def get_load_percent_per_cpu() -> list:
        return psutil.cpu_percent(percpu=True)

    @staticmethod
    def get_frequency_per_cpu() -> dict:
        current_frequency = dict()
        freq_data = psutil.cpu_freq(percpu=True)
        for ind in range(psutil.cpu_count(logical=True)):
            current_frequency[ind] = {name: getattr(freq_data[ind], name) for name in freq_data[ind]._fields if name != 'min'}

        return current_frequency

    @staticmethod
    def get_cpu_count() -> int:
        return psutil.cpu_count(logical=True)


class MEMORY:
    def __init__(self):
        self.total_ram = psutil.virtual_memory()[0]
        self.total_swap = psutil.swap_memory()[0]
        self.total_mem_bytes_for_human = bytes2human(psutil.virtual_memory()[0])

    @staticmethod
    def get_used_memory() -> int:
        return psutil.virtual_memory()[3]

    @staticmethod
    def get_used_memory_bytes_for_human() -> str:
        return bytes2human(psutil.virtual_memory()[3])

    def get_total_memory(self) -> int:
        return self.total_ram

    def get_total_memory_bytes_for_human(self) -> str:
        return self.total_mem_bytes_for_human

    def get_total_swap_byte_for_human(self) -> str:
        return bytes2human(self.total_swap)

    @staticmethod
    def get_used_swap_bytes_for_human() -> str:
        return bytes2human(psutil.swap_memory()[1])

    @staticmethod
    def get_user_ram_percent() -> float:
        return psutil.virtual_memory()[2]


class NETWORK:

    def __init__(self):
        self.this_ip_field = 'laddr'
        self.remote_ip_field = 'raddr'
        self.status_field = 'status'
        self.pid_field = 'pid'
        self.proc_info = "proc_info"
        self.valid_fields = [self.this_ip_field, self.remote_ip_field, self.status_field]
        self.network_stat = namedtuple('net_stat', ['pid', 'from_ip', 'remote_ip', 'proc_name', 'proc_username', 'status'])

    def get_all_fields(self) -> list:
        return self.valid_fields + [self.proc_info]

    # old
    def get_net_stat_(self, protocol: str = 'tcp4') -> dict:
        result = dict()
        data = psutil.net_connections(kind=protocol)
        all_procs = {p.pid: p.info for p in psutil.process_iter(['name', 'username', 'pid'])}
        for count in range(len(data)):
            elem = data[count]

            this_ip = getattr(elem, self.this_ip_field)
            remote_ip = getattr(elem, self.remote_ip_field)
            status = getattr(elem, self.status_field)
            info = all_procs[getattr(elem, 'pid')] if getattr(elem, 'pid') is not None else None

            # result[count] = {name: getattr(elem, name) for name in self.all_fields if name != self.proc_info}
            result[count] = {
                self.this_ip_field: this_ip,
                self.remote_ip_field: remote_ip,
                self.status_field: status,
                self.proc_info: info
            }

        return result

    def get_net_stat(self, protocol: str) -> tuple:
        result = list()
        data = psutil.net_connections(kind=protocol)
        all_procs = {p.pid: p.info for p in psutil.process_iter(['name', 'username', 'pid'])}
        for count in range(len(data)):
            elem = data[count]

            pid = getattr(elem, 'pid')
            this_ip = getattr(elem, self.this_ip_field)
            remote_ip = getattr(elem, self.remote_ip_field)
            process_name = all_procs[pid]['name'] if pid is not None else None
            process_username = all_procs[pid]['username'] if pid is not None else None
            status = getattr(elem, self.status_field)

            result.append(self.network_stat(pid=pid, from_ip=this_ip, remote_ip=remote_ip, proc_name=process_name, proc_username=process_username, status=status))
        return tuple(result)


if __name__ == '__main__':
    # stats = NETWORK().get_net_stat(protocol='tcp4')
    # for obj in stats.values():
    #     print(obj)
    stats = list()
    res = NETWORK().get_net_stat(protocol='tcp4')
    stats.append(res)
    print(res)
    for item in res:
        print(item)
        print(getattr(item, 'from_ip'))
    # print(stats[0])
    # print(len(stats[0]))
    # print()
    # print(getattr(stats[0][0], 'pid'))
    # print(type(getattr(stats[0][0], 'pid')))
