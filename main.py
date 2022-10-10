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
    # child = []
    spacing_ = 7
    cols_ = 1

    ip_splitter = ':'
    from_feild = f"F{ip_splitter} "
    to_filed = f"T{ip_splitter} "

    ip = 'ip'
    port = 'port'

    my_ip = 'from_ip'
    re_ip = 'remote_ip'
    pid = 'pid'
    process_info = 'proc_info'
    process_name = 'proc_name'
    process_username = 'proc_username'
    status = 'status'

    ip_pos = 0
    port_pos = 1
    normal_len = 24

    no_info_msg = "X"
    no_ip = 'X.X.X.X'
    no_port = "XXX"

    def __init__(self, **kwargs):
        super(Network_field, self).__init__(cols=self.cols_, spacing=self.spacing_, size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.network_handler = pc_stats.NETWORK()
        self.updates_protocols = list()

    def place_all_child(self, childs: list[Button | Label]):
        for obj in childs:
            self.add_widget(obj)
            # self.child.append(obj)

    def clear_all_childs(self):
        if len(self.children) != 0:
            self.clear_widgets(self.children)

    # old
    def loop_update_(self, *a):
        self.clear_all_childs()

        if len(self.updates_protocols) == 0:
            return

        stats = list()
        for protocol in self.updates_protocols:
            try:
                result = self.network_handler.get_net_stat(protocol=protocol)
                stats.append(result)
            except ValueError:
                continue

        objects = list()
        for stat in stats:
            try:
                objects.append(self.create_labels(stat))
            except Exception as e:
                print(f"IN: 'loop_update' ERR: {e}")

        for obj in objects:
            self.place_all_child(obj)

    #  old
    def update_network_info_(self, all_stats: dict) -> list:
        childs = list()
        for obj in all_stats.values():
            pid = str(obj[self.process_info][self.pid]) if obj[self.process_info] is not None else self.no_info_msg
            ip_from = self.from_feild + obj[self.my_ip][self.ip_pos] + self.ip_splitter + str(obj[self.my_ip][self.port_pos]) if len(obj[self.my_ip]) == self.normal_len else self.try_to_get_ip(obj[self.my_ip])
            ip_to = self.to_filed + obj[self.re_ip][self.ip_pos] + self.ip_splitter + str(obj[self.re_ip][self.port_pos]) if len(obj[self.re_ip]) == self.normal_len else self.try_to_get_ip(obj[self.re_ip])
            proc_name = obj[self.process_info][self.process_name] if obj[self.process_info] is not None else self.no_info_msg
            proc_username = obj[self.process_info][self.username] if obj[self.process_info] is not None else self.no_info_msg
            status = obj[self.status]
            childs.append(NetworkMainBox(pid=pid, ip_from=ip_from, ip_to=ip_to, proc_name=proc_name, proc_username=proc_username, status=status))

        return childs

    def loop_update(self, *a):
        self.clear_all_childs()

        if len(self.updates_protocols) == 0:
            return

        stats = list()
        for protocol in self.updates_protocols:
            result = self.network_handler.get_net_stat(protocol=protocol)
            stats.append(result)
            del result

        objects = list()
        for stat in stats:
            objects.append(self.create_labels(stat))

        for obj in objects:
            self.place_all_child(obj)

    def create_labels(self, all_stats: tuple) -> list:
        childs = list()

        for obj in all_stats:
            try:
                pid = str(getattr(obj, self.pid))

                my_addr = getattr(obj, self.my_ip)
                if len(my_addr) == 2:
                    ip_from = self.from_feild + getattr(my_addr, self.ip) + self.ip_splitter + str(getattr(my_addr, self.port))

                else:
                    ip_from = self.try_to_get_ip(my_addr)

                remote_ip = getattr(obj, self.re_ip)
                if len(remote_ip) == 2:
                    ip_to = self.to_filed + getattr(remote_ip, self.ip) + self.ip_splitter + str(getattr(remote_ip, self.port))

                else:
                    ip_to = self.try_to_get_ip(remote_ip)

                proc_name = process_name if (process_name := getattr(obj, self.process_name)) is not None else self.no_info_msg
                proc_username = username if (username := getattr(obj, self.process_username)) is not None else self.no_info_msg
                status = status_ if (status_ := getattr(obj, self.status)) is not None else self.no_info_msg

                # print(f"{pid=}")
                # print(f"{ip_from=}")
                # print(f"{ip_to}")
                # print(f"{proc_name}")
                # print(f"{proc_username}")
                # print(f"{status}\n")

                childs.append(
                    NetworkMainBox(pid=pid, ip_from=ip_from, ip_to=ip_to, proc_name=proc_name, proc_username=proc_username,
                                   status=status))
            except Exception as e:
                print(f"IN: 'create_labels' ERR: '{e}'")
        return childs

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

    def add_protocol(self, name):
        if name in self.updates_protocols:
            return
        self.updates_protocols.append(name)

    def delete_protocol(self, name):
        try:
            self.updates_protocols.pop(self.updates_protocols.index(name))
        except IndexError:
            return


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


class SwitchButtonsBox(BoxLayout):
    childrens = dict()

    def __init__(self, **kwargs):
        super(SwitchButtonsBox, self).__init__(**kwargs)
        self.network_field_obj = None

    def create_switch_protocol_buttons(self, protocols: list[str]):
        childs = list()
        for name in protocols:
            button = SwitchButton(self, self.network_field_obj, text=name)
            button.protocol = name
            button.bind(on_press=button.switch)
            childs.append(button)

            self.childrens[name] = button

        self.place_all_childs(childs)

    def place_all_childs(self, childs: list):
        if len(childs) <= 0:
            print("No childs for place")
            return
        for obj in childs:
            self.add_widget(obj)

    def check_switch_by_protocol(self, protocol: str):
        if (protocol == 'inet4') and (self.childrens[protocol].is_active is True):
            self.childrens['tcp4'].force_turn_on()
            self.childrens['udp4'].force_turn_on()

        elif (protocol == 'inet4') and (self.childrens[protocol].is_active is False):
            self.childrens['tcp4'].force_turn_off()
            self.childrens['udp4'].force_turn_off()

        elif (protocol == 'inet6') and (self.childrens[protocol].is_active is True):
            self.childrens['tcp6'].force_turn_on()
            self.childrens['udp6'].force_turn_on()

        elif (protocol == 'inet6') and (self.childrens[protocol].is_active is False):
            self.childrens['tcp6'].force_turn_off()
            self.childrens['udp6'].force_turn_off()


class SwitchButton(Button):
    is_active = False

    def __init__(self, parent: SwitchButtonsBox, network_field_obj: Network_field, **kwargs):
        super(SwitchButton, self).__init__(**kwargs)
        self.parent_ = parent
        self.network_field_obj = network_field_obj
        self.init_color()

    def init_color(self):
        if self.is_active:
            self.background_color = Color.GREEN
        elif not self.is_active:
            self.background_color = Color.RED

    def force_turn_on(self):
        self.is_active = True
        self.init_color()
        self.update_network()

    def force_turn_off(self):
        self.is_active = False
        self.init_color()
        self.update_network()

    def switch_state(self):
        if self.is_active:
            self.background_color = Color.RED
            self.is_active = False
        elif not self.is_active:
            self.background_color = Color.GREEN
            self.is_active = True

    def update_network(self):
        if self.is_active:
            self.network_field_obj.add_protocol(self.protocol)
            self.force_update_network_field()
        elif not self.is_active:
            self.network_field_obj.delete_protocol(self.protocol)
            self.force_update_network_field()

    def force_update_network_field(self):
        self.network_field_obj.loop_update()

    def switch(self, *a):
        self.switch_state()
        self.update_network()
        self.parent_.check_switch_by_protocol(self.protocol)


class MainApp(App):
    protocols_list = ['inet4', 'inet6', 'tcp4', 'tcp6', 'udp4', 'udp6']  # not here, but need: 'unix'

    def __init__(self):
        super().__init__()
        self.update_interval = 1
        self.clock = Clock

    def startup(self):
        self.main_lay = MainBoxLayout()
        self.main_lay.switch_buttons_box.network_field_obj = self.main_lay.network_field
        self.main_lay.switch_buttons_box.create_switch_protocol_buttons(self.protocols_list)

    def start_updates(self):
        self.clock.schedule_interval(self.main_lay.mem_box.update_ram_memory_info, self.update_interval)
        self.clock.schedule_interval(self.main_lay.mem_box.update_swap_memory_info, self.update_interval)

        self.clock.schedule_interval(self.main_lay.cpu_box.update_cpu_load_percent, self.update_interval)
        self.clock.schedule_interval(self.main_lay.cpu_box.update_cpu_frequency, self.update_interval)

        self.clock.schedule_interval(self.main_lay.network_field.loop_update, self.update_interval)

    def build(self):
        self.startup()
        self.start_updates()
        return self.main_lay


if __name__ == "__main__":
    Window.clearcolor = Color.GREY_7c
    ap = MainApp()
    ap.run()

