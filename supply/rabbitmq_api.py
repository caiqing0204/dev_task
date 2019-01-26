# -*- coding:utf-8 -*-

import urllib,urllib2
import simplejson
import base64
from dev_task.celery import rabbitmq_password, rabbitmq_user,rabbitmq_host


class MQManage(object):
    def __init__(self):
        self._conn = None
        self._host = None
        self._username = None
        self._password = None
        self._vhost = '/'

    def create_connection(self,host,username,password):
        try:
            self._username = username
            self._password = password
            url = "http://"+host + ":15672/api/whoami"
            self._host = "http://"+host
            userInfo = "%s:%s" % (username, password)
            userInfo = base64.b64encode(userInfo.encode('UTF-8'))
            auth = 'Basic ' + userInfo#必须的
            request = urllib2.Request(url)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', auth)
            response = urllib2.urlopen(request)
            self._conn = auth
        except Exception, e:
            return None

    def set_user_vhost(self, vhost='/', configure='.*', write='.*', read='.*'):
        try:
            url = self._host + ':15672/api/permissions/%2F/'
            url += self._username
            body = {}
            body['username'] = self._username
            body['vhost'] = vhost
            body['configure'] = configure
            body['write'] = write
            body['read'] = read
            data = simplejson.dumps(body)
            request = urllib2.Request(url, data)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            request.get_method = lambda: "PUT"
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            response = urllib2.urlopen(request)
            res = response.read()
            return res
        except Exception, e:
            # print str(e)
            return None

    def list_users(self):
        try:
            url = self._host + ":15672/api/users"
            request = urllib2.Request(url)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            response = urllib2.urlopen(request)
            return response.read()
        except Exception, e:
            return None

    def list_queues(self):
        try:
            url = self._host + ":15672/api/queues"
            request = urllib2.Request(url)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            response = urllib2.urlopen(request)
            return response.read()
        except Exception, e:
            return None

    def list_exchanges(self):
        try:
            url = self._host + ":15672/api/exchanges"
            request = urllib2.Request(url)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            response = urllib2.urlopen(request)
            exchanges = response.read()
            return exchanges
        except Exception, e:
            return None

    def list_connections(self):
        try:
            url = self._host + ":15672/api/connections"
            request = urllib2.Request(url)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            response = urllib2.urlopen(request)
            exchanges = response.read()
            return exchanges
        except Exception, e:
            return None

    def show_connection_detail(self,connection):
        try:
            con = urllib.quote_plus( connection,safe='(,),' )
            url = self._host + ':15672/api/channels/'+ con
            url = url.replace('+','%20')
            request = urllib2.Request( url )
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            response = urllib2.urlopen(request)
            detail = response.read()
            return detail
        except Exception, e:
            print str(e)
            return None

    def clear_exchanges(self):
        exchanges = self.list_exchanges()
        for exchange in exchanges:
            self.del_exchange(exchange_name=exchange['name'])

    def clear_queues(self):
        queues = self.list_queues()
        for queue in queues:
            self.del_queue(queue_name=queue['name'])

    def del_exchange(self, exchange_name):
        try:
            url = self._host + ':15672/api/exchanges/%2F/'
            url += exchange_name
            body = {}
            body['vhost'] = self._vhost
            body['name'] = exchange_name
            data = simplejson.dumps(body)
            request = urllib2.Request(url, data)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            request.get_method = lambda: "PUT"
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            response = urllib2.urlopen(request)
            res = response.read()
            return res
        except Exception, e:
            return None

    def del_queue(self, queue_name ):
        try:
            url = self._host + ':15672/api/queues/%2F/'
            url += queue_name
            body = {}
            body['vhost'] = self._vhost
            body['name'] = queue_name
            data = simplejson.dumps(body)
            request = urllib2.Request(url, data)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            request.get_method = lambda: "DELETE"
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            response = urllib2.urlopen(request)
            res = response.read()
            return res
        except Exception, e:
            return None

    def add_vhost(self, vhost_name):
        try:
            url = self._host + ":15672/api/vhosts/"
            url = url + vhost_name
            body = {}
            body['name'] = vhost_name
            data = simplejson.dumps(body)
            request = urllib2.Request(url, data)
            request.add_header('content-type', 'application/json')
            request.add_header('authorization', self._conn)
            request.get_method = lambda: "PUT"
            urllib2.build_opener(urllib2.HTTPHandler)
            response = urllib2.urlopen(request)
            res = response.read()
            return None
        except Exception, e:
            print str(e)
            return None


if __name__ == '__main__':
    mq = MQManage()
    mq.create_connection(rabbitmq_host,rabbitmq_user, rabbitmq_password)
    queuelist = mq.list_queues()
    print queuelist
