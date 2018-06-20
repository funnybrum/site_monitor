from monitor import DATABASE_FOLDER
from monitor.storage.shelve import ShelveStorage


dbs_to_merge = [
    './properties_glp.db',
    './properties_bis.db',
    './properties.db',
    './prop_gm.db',
]

target = 'merged.db'

merged = {}

for db in dbs_to_merge:
    data = ShelveStorage(db).load()
    merged.update(data)

ShelveStorage(target).save(merged)