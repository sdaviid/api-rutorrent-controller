import requests
from threading import Thread
import time
from utils.encode import(
    b64encode,
    hash_torrent
)
from app.core.database import(
    SessionLocal
)
from app.models.domain.server import(
    Server
)
import random

class ruTorrentData(object):
    def __init__(self, client, data):
        self.client = client
        self.data = data
        self.name = None
        self.size = None
        self.downloaded = None
        self.speed_down = None
        self.speed_up = None
        self.seeders = None
        self.peers = None
        self.output_path = None
        self.handler()
    def handler(self):
        if self.data:
            try:
                self.name = self.data[4]
                self.size = self.data[5]
                self.downloaded = self.data[8]
                self.speed_down = self.data[12]
                self.output_path = self.data[25]
            except Exception as err:
                print(f'ruTorrentData.handler exception - {err}')
    def update(self, data):
        self.data = data
        self.handler()
    def __repr__(self):
        return f'Torrent ("{self.name}" - {self.size}/{self.downloaded})'


class ruTorrentClient(Thread):
    def __init__(self, name, base, user, password):
        Thread.__init__(self)
        self.name = name
        self.base = base
        self.user = user
        self.password = password
        self.active = False
        self.torrents = {}
        self.server_free_space = None
        self.server_used_space = None
        self.server_total_space = None
        self.server_cpu_load = None
        self.alive = False
    def gen_header(self):
        authorization = b64encode(f'{self.user}:{self.password}')
        if authorization:
            return {
                'Authorization': f'Basic {authorization}'
            }
        return False
    def has_hash(self, hash):
        return True if hash in list(self.torrents.keys()) else False
    def kill(self):
        self.alive = False
    def run(self):
        self.alive = True
        while self.alive == True:
            avoid = self.connect()
            avoid = self.get_torrents()
            time.sleep(3)
    def connect(self):
        url = f'{self.base}/plugins/httprpc/action.php'
        headers = self.gen_header()
        if headers:
            try:
                payload = {
                    'mode': 'list',
                    'cmd': 'd.throttle_name=',
                    'cmd': 'd.custom=chk-state',
                    'cmd': 'd.custom=chk-time',
                    'cmd': 'd.custom=sch_ignore',
                    'cmd': 'cat="$t.multicall=d.hash=,t.scrape_complete=,cat={#}"',
                    'cmd': 'cat="$t.multicall=d.hash=,t.scrape_incomplete=,cat={#}"',
                    'cmd': 'd.custom=x-pushbullet',
                    'cmd': 'cat=$d.views=',
                    'cmd': 'd.custom=seedingtime',
                    'cmd': 'd.custom=addtime'
                }
                response = requests.post(url, data=payload, headers=headers)
                if response.status_code == 200:
                    self.active = True
                    self.status_server()
                return response
            except Exception as err:
                print(f'ruTorrent.connect exception - {err}')
        return False
    def get_torrents(self):
        torrents = self.connect()
        if isinstance(torrents, requests.models.Response):
            if torrents.status_code == 200:
                data = torrents.json().get('t', {})
                hash_keys = list(data.keys())
                for key in hash_keys:
                    if key in self.torrents:
                        self.torrents[key].update(data.get(key, {}))
                    else:
                        self.torrents.update({key: ruTorrentData(self, data.get(key, {}))})
                return True
        return False
    def get_files_from(self, hash):
        url = f'{self.base}/plugins/httprpc/action.php'
        headers = self.gen_header()
        if headers:
            try:
                payload = {
                    'mode': 'fls',
                    'hash': hash,
                    'cmd': 'f.prioritize_first=',
                    'cmd': 'f.prioritize_last='
                }
                response = requests.post(url, data=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
            except Exception as err:
                print(f'ruTorrent.get_files_from exception - {err}')
        return False
    def status_server(self):
        if self.active:
            url_space = f'{self.base}/plugins/diskspace/action.php'
            url_cpu = f'{self.base}/plugins/cpuload/action.php'
            try:
                response_space = requests.get(url_space, headers=self.gen_header())
                response_cpu = requests.get(url_cpu, headers=self.gen_header())
                if response_space.status_code == 200 and response_cpu.status_code == 200:
                    self.server_free_space = response_space.json().get('free', 0)
                    self.server_total_space = response_space.json().get('total', 0)
                    self.server_used_space = (response_space.json().get('total', 0) - response_space.json().get('free', 0))
                    self.server_cpu_load = response_cpu.json().get('load', 0)
            except Exception as err:
                print(f'ruTorrentClient.status_server exception - {err}')
    def add_torrent(self, path):
        if self.active:
            url = f'{self.base}/php/addtorrent.php'
            print(path)
            payload = {'torrent_file': open(path, 'rb')}
            try:
                response = requests.post(url, files=payload, headers=self.gen_header())
                if response.status_code == 200:
                    return True
            except Exception as err:
                print(f'ruTorrentClient.add_torrent exception - {err}')
        return False



class ruTorrentManager(Thread):
    def __init__(self, session):
        Thread.__init__(self)
        self.servers = []
        self.session = session
    def run(self):
        while True:
            temp_list_servers = Server.list_all(session=self.session)
            if temp_list_servers:
                for server in temp_list_servers:
                    if self.has_id(server.id) == False:
                        self.add_server(id=server.id, name=server.name, base=server.base, user=server.user, password=server.password)
            time.sleep(10)
    def add_server(self, id, name, base, user, password):
        temp = ruTorrentClient(name, base, user, password)
        if temp.connect():
            avoid = temp.start()
            self.servers.append({'id': id, 'name': name, 'server': temp})
    def has_id(self, id):
        for server in self.servers:
            if server.get('id', False) == id:
                return True
        return False
    def pick_server(self):
        return random.choice(self.servers)
    def find_hash(self, hash):
        for server in self.servers:
            if hash in server['server'].torrents:
                return server['server'].torrents[hash]
        return False
    def get_files_by_hash(self, hash):
        for server in self.servers:
            if server['server'].has_hash(hash):
                files = server['server'].get_files_from(hash)
                torrent = server['server'].torrents[hash]
                return {'files': files, 'torrent': torrent}
        return False



manager = ruTorrentManager(session=SessionLocal())
manager.start()

def get_ruTorrentManager():
    return manager