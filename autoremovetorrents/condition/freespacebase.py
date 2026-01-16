# 文件名: autoremovetorrents/condition/freespacebase.py

from .sortbase import ConditionWithSort

class FreeSpaceConditionBase(ConditionWithSort):
    def __init__(self, settings):
        ConditionWithSort.__init__(self, settings['action'])
        self._min = settings['min'] * (1 << 30) # 将配置的 GiB 转换为字节 (Bytes)
        
        # --- 修改点 1: 读取配置 ---
        # 读取用户在 config.yml 里写的 seeding_time (单位: 秒)
        # 如果用户没写，默认为 0 (即不限制)
        self._min_seeding_time = settings.get('seeding_time', 0)

    def apply(self, free_space, torrents):
        torrents = list(torrents)
        # 先按用户设定的规则排序 (比如按做种时间、大小等排序)
        ConditionWithSort.sort_torrents(self, torrents)
        
        for torrent in torrents:
            if free_space < self._min:
                # --- 修改点 2: 增加保护逻辑 ---
                # 在决定删除之前，先检查这个种子的做种时间够不够。
                # 如果做种时间 < 设定值，绝对不删，直接跳过，保留它。
                if torrent.seeding_time < self._min_seeding_time:
                    self.remain.add(torrent)
                    continue # 跳过当前循环，去看下一个种子
                # ---------------------------

                # 如果时间够了，且空间依然不足，那就删掉它
                free_space += torrent.size
                self.remove.add(torrent)
            else:
                # 空间够了，剩下的都保留
                self.remain.add(torrent)
