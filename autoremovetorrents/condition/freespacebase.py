# -*- coding:utf-8 -*-
from .sortbase import ConditionWithSort

class FreeSpaceConditionBase(ConditionWithSort):
    def __init__(self, settings):
        ConditionWithSort.__init__(self, settings['action'])
        self._min = settings['min'] * (1 << 30) # 将 GiB 转换为 Bytes
        
        # --- 修改点 1: 读取特定 Tracker 的规则 ---
        # 读取配置中的 seeding_time_per_tracker 字典
        # 如果没配置，默认为空字典 {}
        self._tracker_rules = settings.get('seeding_time_per_tracker', {})

    def apply(self, free_space, torrents):
        torrents = list(torrents)
        ConditionWithSort.sort_torrents(self, torrents)
        
        for torrent in torrents:
            if free_space < self._min:
                # --- 修改点 2: 针对特定 Tracker 进行检查 ---
                
                should_protect = False # 默认不保护
                
                # 获取当前种子的 Tracker 地址（转为字符串以防万一）
                # 注意：torrent.tracker 通常返回域名或 announce URL
                current_tracker = str(torrent.tracker).lower()

                # 遍历我们在配置文件里写的规则
                # keyword 是你在配置里写的 (如 'hdsky')
                # min_time 是对应的时间 (如 86400)
                for keyword, min_time in self._tracker_rules.items():
                    # 如果配置的关键字出现在了种子的 Tracker URL 里
                    if keyword.lower() in current_tracker:
                        # 且做种时间还不够
                        if torrent.seeding_time < min_time:
                            should_protect = True # 标记为“受保护”
                        break # 找到匹配的站点了，停止查找其他规则

                if should_protect:
                    # 如果受保护，绝对不删，直接跳过
                    self.remain.add(torrent)
                    continue 
                # ---------------------------------------

                # 如果没被保护（要么没匹配到站点，要么时间够了），则执行删除
                free_space += torrent.size
                self.remove.add(torrent)
            else:
                self.remain.add(torrent)
