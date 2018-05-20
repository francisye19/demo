from datetime import datetime

from app.extensions import mdb
from app.mongosupport import Model


@mdb.register
class Proxy(Model):
    __collection__ = 'proxies'
    structure = {
        'hostname': unicode,
        'hostAddress': int,
        'status': int,
        'lastCheck': datetime,
        'createTime': datetime,
    }

    required_fields = ['hostname', 'hostAddress']
    default_values = {'hostname': 'proxy', 'lastCheck': datetime.now, 'createTime': datetime.now}
    indexes = [{'fields': ['hostAddress'], 'unique': True}]
