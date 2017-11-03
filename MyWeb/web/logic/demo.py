# -*- coding:utf-8 -*-

import tornado.web
import hashlib
import urllib
import json
import copy
import time
from datetime import datetime
from bson import ObjectId
import tornado,cStringIO

from mongo_util import MongoIns;mongo_util = MongoIns()
from tornado import httpclient
from tornado import httputil
from kpages import srvcmd
from kpages import url,ContextHandler
from tornado.web import RequestHandler, ErrorHandler
from logic import receive
from logic import reply

class BaseHandler(ContextHandler,tornado.web.RequestHandler):
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Origin, No-Cache, X-Requested-With, If-Modified-Since, Pragma, Last-Modified, Cache-Control, Expires, Content-Type, X-E4M-With")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

	def options(self, *args, **kwargs):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Origin, No-Cache, X-Requested-With, If-Modified-Since, Pragma, Last-Modified, Cache-Control, Expires, Content-Type, X-E4M-With")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

	def getAccessToken(self):
		access_token = ''
		expires_in = 0
		login_client = httpclient.HTTPClient()
		try:
			response = login_client.fetch('https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx31da8356c59d346a&secret=f2bebe6ddf0635ed4121301eb69b5d4d')
			body = response.body
			body = json.loads(body)
			if body:
				access_token = body.get('access_token','')
				expires_in = int(body.get('expires_in',0))
				self.access_token = access_token
		except httpclient.HTTPError as e:
			print("Error: "+str(e))
		except Exception as e:
			print("Error: "+str(e))
		finally:
			login_client.close()
		return dict(access_token = access_token, expires_in = expires_in)

	def setMenu(self, menu):
		#https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN
		#import pdb;pdb.set_trace()
		url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token="+self.access_token
		print url
		menu = menu.encode('utf-8')
		url_request = urllib.urlopen(url=url, data = menu )
		back = url_request.read()
		return back

	def setMenu2(self, menu):
		#https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN
		menu_client = httpclient.HTTPClient()
		#import pdb;pdb.set_trace()
		url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token="+self.access_token
		print url
		menu = menu.encode('utf-8')
		#url_request = urllib.urlopen(url=url, data = menu )
		request = httpclient.HTTPRequest(url, method = "POST",body= urllib.urlencode(json.loads(menu)))#urllib.urlencode()
		back = "{}"
		print back
		try:
			response = menu_client.fetch(request)
			back = response.body
			print back
		except Exception as e:
			print("Error: "+str(e))
		finally:
			menu_client.close()

		return back




@url(r"/update")
class UpdateToken(BaseHandler):
	"""此处专门负责获取和存储Token"""
	def get(self):
		token = self.getAccessToken()
		print token
		kwargs = {}
		if token:
			kwargs = token
			ts = time.time()
			addon = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ts))
			kwargs['ts'] = ts
			kwargs['addon'] = addon
			MongoIns().m_insert("access_token",**kwargs)
			self.write(dict(status = True, msg = "获取Token成功!"))
		else:
			self.write(dict(status = False, msg = "Toekn获取失败!"))



@url(r"/menu")
class Test1(BaseHandler):
	"""渲染demo界面"""
	def post(self):
		menu = self.get_argument("menu","{}")
		#menu = json.loads(menu)
		if menu:
			self.getAccessToken()
			back = self.setMenu(str(menu))
			if back:
				print back
			back = json.loads(back)
			if back and int(back.get('errcode',-1)) == 0:
				self.write(dict(msg = "设置成功了...", status = True))
			elif back:
				self.write(dict(msg = back.get('errmsg','error'), status = False))
			else:
				self.write(dict(msg = "error", status = False))
		else:
			self.write(dict(msg = "error", status = False))




@url(r'/demo')
class Test2(BaseHandler):
	"""docstring for ClassName"""
	def get(self):
		print self.request.arguments,'GET'
		signature = self.get_argument('signature','')
		timestamp = self.get_argument('timestamp','')
		nonce = self.get_argument('nonce','')
		echostr = self.get_argument('echostr','')
		token = u"ljk123"
		array = [token, timestamp, nonce]
		print 'array',array
		array.sort()
		print 'array',array
		sha1 = hashlib.sha1()
		map(sha1.update, array)
		hashcode = sha1.hexdigest()
		print hashcode,signature
		if hashcode == signature:
			self.write(echostr)
		else:
			self.write('success')


	def post(self):
		print self.request.arguments,'POST'
		body = self.request.body
		print "Handle Post webdata is ", body
		recMsg = receive.parse_xml(body)
		back = ""
		if isinstance(recMsg, receive.Msg):
			toUser = recMsg.FromUserName
			fromUser = recMsg.ToUserName
			if recMsg.MsgType == 'text':
				content = "test"
				replyMsg = reply.TextMsg(toUser, fromUser, content)
				back = replyMsg.send()
			if recMsg.MsgType == 'image':
				mediaId = recMsg.MediaId
				replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
				back = replyMsg.send()
		elif isinstance(recMsg, receive.EventMsg):
			toUser = recMsg.FromUserName
			fromUser = recMsg.ToUserName
			if recMsg.Event == 'CLICK':
				if recMsg.Eventkey == 'mpGuide':
					content = u"编写中，尚未完成".encode('utf-8')
					replyMsg = reply.TextMsg(toUser, fromUser, content)
					back = replyMsg.send()
				else:
					content = u"编写中，尚未完成".encode('utf-8')
					replyMsg = reply.TextMsg(toUser, fromUser, content)
					back = replyMsg.send()
		else:
			print "暂且不处理"
			back = reply.Msg().send()
		print back
		self.write(back)


		
