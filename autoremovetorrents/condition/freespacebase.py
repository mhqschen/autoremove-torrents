# -*- coding:utf-8 -*-
from .sortbase import ConditionWithSort

class FreeSpaceConditionBase(ConditionWithSort):
    def __init__(self, settings):
        ConditionWithSort.__init__(self, settings['action'])
        self._min = settings['min'] * (1 << 30) # 将 GiB 转换为 Bytes
        
        # --- 修改点 1: 初始化配置 ---
        
        # 1. 获取全局默认限制
        # 如果配置文件里没写 seeding_time，则默认为 0（表示无限制，随时可删）
        self._global_seeding_time = settings.get('seeding_time', 0)
        
        # 2. 获取针对特定 Tracker 的规则
        # 如果没配置，默认为空字典
        self._tracker_rules = settings.get('seeding_time_per_tracker', {})

    def apply(self, free_space, torrents):
        torrents = list(torrents)
        ConditionWithSort.sort_torrents(self, torrents)
        
        for torrent in torrents:
            if free_space < self._min:
                # --- 修改点 2: 判定逻辑 ---
                
                # 步骤 A: 设定初始阈值
                # 默认情况下，当前种子需要满足全局设置的时间
                required_time = self._global_seeding_time
                
                # 步骤 B: 检查是否有特定 Tracker 的“覆盖规则”
                current_tracker = str(torrent.tracker).lower()
                
                for keyword, specific_time in self._tracker_rules.items():
                    if keyword.lower() in current_tracker:
                        # 发现当前种子属于特殊站点！
                        # 使用特定规则的时间，覆盖掉全局默认时间
                        required_time = specific_time
                        break # 找到规则后停止查找
                
                # 步骤 C: 执行最终判定
                # 如果当前做种时间 < 要求的最低时间（无论是全局的还是特例的）
                if torrent.seeding_time < required_time:
                    # 保护该种子，不删除
                    self.remain.add(torrent)
                    continue 
                
                # -----------------------
                
                # 如果代码走到这里，说明：
                # 1. 空间不足
                # 2. 且种子的做种时间已经超过了 required_time (或者 required_time 是 0)
                # 结论：可以删除
                free_space += torrent.size
                self.remove.add(torrent)
            else:
                # 空间足够，不需要删
                self.remain.add(torrent)
