from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
import pc_stats


class Color:
    WHITE = (255 / 255, 255 / 255, 255 / 255, 1)
    BLACK = (0 / 255, 0 / 255, 0 / 255, 1)
    GREY_ad = (173 / 255, 173 / 255, 173 / 255, 1)      # ad 3 times
    GREY_7c = (124 / 255, 124 / 255, 124 / 255, 1)
    GREY_c8 = (200 / 255, 200 / 255, 200 / 255, 1)
    RED = (190 / 255, 0 / 255, 0 / 255, 1)
    YELLOW = (170 / 255, 170 / 255, 0 / 255, 1)
    GREEN = (40 / 255, 180 / 255, 0, 1)


class MainBoxLayout(BoxLayout):
    pass


class Network_field(GridLayout):
    child = []
    spacing_ = 7
    cols_ = 1

    ip_splitter = ':'
    from_feild = f"F{ip_splitter} "
    to_filed = f"T{ip_splitter} "

    ip = 'ip'
    port = 'port'

    my_ip = 'laddr'
    re_ip = 'raddr'
    pid = 'pid'
    process_info = 'proc_info'
    process_name = 'name'
    username = 'username'
    status = 'status'

    ip_pos = 0
    port_pos = 1
    normal_len = 2

    no_info_msg = "X"
    no_ip = 'X.X.X.X'
    no_port = "XXX"

    def __init__(self, **kwargs):
        super(Network_field, self).__init__(cols=self.cols_, spacing=self.spacing_, size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter('height'))

    def place_all_child(self, childs: list[Button | Label]):
        for obj in childs:
            self.add_widget(obj)
            self.child.append(obj)

    def update_network_info(self, all_stats: dict):
        if len(self.child) != 0:
            self.clear_widgets(self.child)
            # for obj in self.child:
            #     self.remove_widget(obj)

        childs = list()
        for obj in all_stats.values():
            pid = str(obj[self.process_info][self.pid]) if obj[self.process_info] is not None else self.no_info_msg
            ip_from = self.from_feild + obj[self.my_ip][self.ip_pos] + self.ip_splitter + str(obj[self.my_ip][self.port_pos]) if len(obj[self.my_ip]) == self.normal_len else self.try_to_get_ip(obj[self.my_ip])
            ip_to = self.to_filed + obj[self.re_ip][self.ip_pos] + self.ip_splitter + str(obj[self.re_ip][self.port_pos]) if len(obj[self.re_ip]) == self.normal_len else self.try_to_get_ip(obj[self.re_ip])
            proc_name = obj[self.process_info][self.process_name] if obj[self.process_info] is not None else self.no_info_msg
            proc_username = obj[self.process_info][self.username] if obj[self.process_info] is not None else self.no_info_msg
            status = obj[self.status]
            childs.append(NetworkMainBox(pid=pid, ip_from=ip_from, ip_to=ip_to, proc_name=proc_name, proc_username=proc_username, status=status))

        self.place_all_child(childs)

    def try_to_get_ip(self, stat: tuple) -> str:
        if len(stat) == 0:
            return self.no_info_msg
        try:
            ip = getattr(stat, self.ip)
        except AttributeError:
            ip = self.no_ip

        try:
            port = str(getattr(stat, self.port))
        except AttributeError:
            port = self.no_port

        return ip + self.ip_splitter + port


class NetworkMainBox(BoxLayout):
    def __init__(self, pid: str, ip_from: str, ip_to: str, proc_name: str, proc_username: str, status: str, **kwargs):
        super(NetworkMainBox, self).__init__(**kwargs)
        self.pid_lab.text = pid
        self.ip_from_lab.text = ip_from
        self.ip_to_lab.text = ip_to
        self.process_name_lab.text = proc_name
        self.process_username_lab.text = proc_username
        self.status_lab.text = status


class CPU_field(BoxLayout):
    cpu_handler = pc_stats.CPU

    load_min = 50
    load_max = 85

    freq_current = 'current'
    freq_max = 'max'

    def update_cpu_load_percent(self, *a):
        stats = self.cpu_handler.get_load_percent_per_cpu()
        for ind in range(len(stats)):
            label_name = f"core_load_{ind}"
            load_percent = stats[ind]
            getattr(self, label_name).text = f"{load_percent}%"
            self.update_load_color(label_name, load_percent)

    def update_load_color(self, label_name: str, val: int):
        if val < self.load_min:
            getattr(self, label_name).background_color = Color.GREEN
        elif (val > self.load_min) and (val < self.load_max):
            getattr(self, label_name).background_color = Color.YELLOW
        elif val > self.load_max:
            getattr(self, label_name).background_color = Color.RED

    def update_cpu_frequency(self, *a):
        stats = self.cpu_handler.get_frequency_per_cpu()
        for key, stat in stats.items():
            getattr(self, f"core_freq_{key}").text = f"{round(stat[self.freq_current])}/{round(stat[self.freq_max])}"


class MEM_field(BoxLayout):
    mem_handler = pc_stats.MEMORY()

    swap_total = mem_handler.get_total_swap_byte_for_human()

    ram_perc_min = 30
    ram_perc_max = 85

    def update_ram_memory_info(self, *a):
        used = self.mem_handler.get_used_memory_bytes_for_human()
        total = self.mem_handler.get_total_memory_bytes_for_human()
        self.mem_info.text = f"RAM: {used}/{total}"
        self.update_ram_color(self.mem_handler.get_user_ram_percent())

    def update_ram_color(self, percent_used: float):
        if percent_used < self.ram_perc_min:
            self.mem_info.background_color = Color.GREEN
        elif (percent_used > self.ram_perc_min) and (percent_used < self.ram_perc_max):
            self.mem_info.background_color = Color.YELLOW
        elif percent_used > self.ram_perc_max:
            self.mem_info.background_color = Color.RED

    def update_swap_memory_info(self, *a):
        used = self.mem_handler.get_used_swap_bytes_for_human()
        total = self.mem_handler.get_total_swap_byte_for_human()
        # self.swap_info.text = f"SWAP: {used}/1Gb"
        self.swap_info.text = f"SWAP: {used}/{self.swap_total}"


class MainApp(App):
    def __init__(self):
        super().__init__()
        self.update_interval = 1
        self.clock = Clock
        self.network_handler = pc_stats.NETWORK()

    def create(self):
        self.main_lay = MainBoxLayout()

    def network_updates(self, *a):
        stats = self.network_handler.get_net_stat()
        self.main_lay.network_field.update_network_info(stats)

    def start_updates(self):
        self.clock.schedule_interval(self.main_lay.mem_box.update_ram_memory_info, self.update_interval)
        self.clock.schedule_interval(self.main_lay.mem_box.update_swap_memory_info, self.update_interval)

        self.clock.schedule_interval(self.main_lay.cpu_box.update_cpu_load_percent, self.update_interval)
        self.clock.schedule_interval(self.main_lay.cpu_box.update_cpu_frequency, self.update_interval)

        self.clock.schedule_interval(self.network_updates, self.update_interval)

    def build(self):
        self.create()
        self.start_updates()
        return self.main_lay


if __name__ == "__main__":
    Window.clearcolor = Color.GREY_7c
    ap = MainApp()
    ap.run()

