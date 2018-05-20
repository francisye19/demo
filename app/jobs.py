# -*- coding: utf-8 -*-
"""
    jobs
    ~~~~~~~~~~~~~~

    Jobs defined here.

    :copyright: (c) 2016 by fengweimin.
    :date: 16/8/12
"""
import Queue
import os
import threading
import time
from collections import Counter
from datetime import datetime

import schedule
from pymongo import cursor

from app.models import Post
from app.models.proxy import Proxy

post_view_times_counter = Counter()


def update_view_times(app):
    """
    Update view times for posts.
    """
    app.logger.info('Scheduler update_view_times running: %s' % post_view_times_counter)
    d = dict(post_view_times_counter)
    post_view_times_counter.clear()
    for k, v in d.iteritems():
        p = Post.find_one({'_id': k})
        if p:
            try:
                p.viewTimes += v
                p.save()
            except:
                app.logger.exception('Failed when updating the viewTime for album %s' % p._id)


def update_proxy_status(app):
    """
    Update proxy server status
    """
    queue = Queue.Queue()
    # find out proxies from db
    cursor = Proxy.find()
    # proxies = [c.hostname for c in cursor]
    proxies = ['47.74.179.34', '47.74.156.80', '47.74.240.10', '47.74.230.144']
    # address = ['14.215.177.39', '58.205.212.206', '202.38.193.28', '125.216.242.42']
    _thread = 3
    for host in proxies:
        queue.put(host)  # 将IP放入队列中。函数中使用q.get(ip)获取

    def check(i, q):
        while True:
            host = q.get()  # 获取Queue队列传过来的ip，队列使用队列实例queue.put(ip)传入ip，通过q.get() 获得
            print "Thread %s:Pinging %s" % (i, host)
            # data = os.system("ping -c 3 %s > /dev/null 2>&1" % ip)  # 使用os.system返回值判断是否正常
            data = os.system("curl --connect-timeout 5 -x http://%s:3128 https://www.google.com/ncr > "
                             "/dev/null 2>&1" % host)
            status = 0
            if data == 0:
                print "%s:正常运行" % host
                status = 0
            else:
                print "%s:停止工作" % host
                status = -1
            Proxy.update_one({'hostAddress': host}, {'$set': {'status': status}})
            q.task_done()  # 表示queue.join()已完成队列中提取元组数据

    for i in range(_thread):  # 线程开始工作
        run = threading.Thread(target=check, args=(i, queue))  # 创建一个threading.Thread()的实例，给它一个函数和函数的参数
        run.setDaemon(True)  # 这个True是为worker.start设置的，如果没有设置的话会挂起的，因为check是使用循环实现的
        run.start()  # 开始线程的工作
    queue.join()  # 线程队列执行关闭
    print "ping 工作已完成"
    # app.logger.info('')


def run_schedule(app):
    """
    Invoke schedule.
    """
    # For schedule rules please refer to https://github.com/dbader/schedule
    schedule.every(20).minutes.do(update_view_times, app)

    schedule.every(5).seconds.do(update_proxy_status, app)

    while True:
        schedule.run_pending()
        time.sleep(1)


def init_schedule(app):
    """
    Init.
    """
    # http://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode/
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        t = threading.Thread(target=run_schedule, args=(app,))
        # Python threads don't die when the main thread exits, unless they are daemon threads.
        t.setDaemon(True)
        t.start()
