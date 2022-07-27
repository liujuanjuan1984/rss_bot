from rss.config import DB_NAME, RSS_GROUPS
from rss.modules import RssDB

db = RssDB(DB_NAME, False, False)


print("🤖 Rss Rum to Xin bot 7000104017 🤖")
print("=== 每个种子网络的订阅数 ===")
counts = {}
for group_id in RSS_GROUPS:
    resp = db.count_rss_by_group(group_id)
    print(f"{group_id} : {resp}")

""" 
countsit = sorted(counts.items(), key=lambda x: x[1], reverse=True)
for name, n in countsit:
    print(n, name)
"""

print("🥂 共计", 0, "个用户使用 bot🥂")
