import pymongo

from flask import Blueprint, render_template, current_app

from app.models.proxy import Proxy
from app.permissions import admin_permission

proxy = Blueprint('proxies', __name__)


@proxy.route('/')
@admin_permission.require(403)
def index():
    """
    Proxy management page
    """
    """
        Index page.
        """
    cursor = Proxy.find()
    proxies = [[c.hostname, c.hostAddress, c.status, c.lastCheck, c.createTime] for c in cursor]
    current_app.logger.info('Found %s proxies' % len(proxies))
    return render_template('public/proxies_overview.html', proxies=proxies)
    # return render_template('public/blank.html')
