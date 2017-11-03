# -*- coding:utf-8 -*-
"""
    index action demo
    author comger@gmail.com
"""
import tornado,cStringIO

from inspect import isclass, ismethod, getmembers
from unittest import TestCase, TextTestRunner,TestSuite
from kpages import url, ContextHandler,get_modules
from kpages.utest import load_testcase,load_testsuites_bypath



class BaseHandler(ContextHandler,tornado.web.RequestHandler):
    pass


@url(r"/ppo")
class IndexHandler(BaseHandler):
    """ 获取所有单元测试, 并可以按树状查看"""
    def get(self):
        
        suites = []
        ms = get_modules(__conf__.UTEST_DIR)
        for m in ms:
            #import pdb;pdb.set_trace()
            m_name = m.__name__.split('.')[-1]
            s = dict(_id= len(suites), name= m_name, code = m.__name__, parent='root',doc=m.__doc__, level=0)
            suites.append(s)

            cases = load_testcase(m_name)
            for case,cls in cases.items():
                
                sc = dict(_id= len(suites),name=case.split('.')[-1], code=case, parent=s['_id'], doc=cls.__doc__,level=1)
                suites.append(sc)

                for n, m in getmembers(cls):
                    if n.startswith("test") and ismethod(m):
                        sf = dict(_id= len(suites), name=n,code="{0}.{1}".format(case, n), parent=sc['_id'], doc=m.__doc__, level=2)
                        suites.append(sf)
                        


        self.render('test/index.html', suites=suites)


    
    def post(self):
        code = self.get_argument('code','')
        code = code.replace('utest.', '') or None
        suites = load_testsuites_bypath(code)
        out = cStringIO.StringIO()
        results = TextTestRunner(stream=out,verbosity=0).run(TestSuite(suites))

        resultmap = {}
        results.errors.extend(results.failures)

        for error in results.errors:
            module = error[0].__module__
            cls = error[0].__class__.__name__
            _code = '{}.{}.{}'.format(module,cls,error[0]._testMethodName)
            resultmap[_code] = error[1]

        self.write(dict(data=resultmap))

