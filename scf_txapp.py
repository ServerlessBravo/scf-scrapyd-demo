import sys
import os
from time import sleep
from datetime import datetime

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)

from twisted.internet import reactor
from scrapyd.launcher import ScrapyProcessProtocol
from scrapyd.interfaces import IEnvironment
from scrapyd.utils import get_crawl_args, native_stringify_dict
from scrapy.utils.project import get_project_settings
from scrapyd.config import Config
from scrapy.utils.misc import load_object
from scrapyd import get_application
from zope.interface import implementer
from scrapyd.interfaces import ISpiderScheduler, IJobStorage
from twisted.python import log


def get_application(config=None):
    if config is None:
        config = Config()
    apppath = config.get('application', 'scrapyd.app.application')
    appfunc = load_object(apppath)
    return config, appfunc(config)


@implementer(ISpiderScheduler)
class ScfScrapydScheduler:

    def __init__(self, config, app):
        self.update_projects()
        self.project_settings = get_project_settings()
        self.runner = config.get('runner', 'scrapyd.runner')
        self.app = app
        self.processes = {}
        self.finished = app.getComponent(IJobStorage)

    def schedule(self, project, spider_name, priority=0.0, **spider_args):
        message = spider_args.copy()
        message['_project'] = project
        message['_spider'] = spider_name

        self._spawn_process(message, '1_core')

    def _spawn_process(self, message, slot):
        msg = native_stringify_dict(message, keys_only=False)
        project = msg['_project']
        args = [sys.executable, '-m', self.runner, 'crawl']
        args += get_crawl_args(msg)
        e = self.app.getComponent(IEnvironment)
        env = e.get_environment(msg, slot)
        env = native_stringify_dict(env, keys_only=False)
        pp = ScrapyProcessProtocol(slot, project, msg['_spider'],
                                   msg['_job'], env)
        pp.deferred.addBoth(self._process_finished, slot)
        reactor.spawnProcess(pp, sys.executable, args=args, env=env)
        self.processes[slot] = pp

    def _process_finished(self, _, slot):
        log.msg("job finished")
        process = self.processes.pop(slot)
        process.end_time = datetime.now()
        self.finished.add(process)
        
    def list_projects(self):
        return ['default']

    def update_projects(self):
        pass


config, application = get_application()
application.setComponent(ISpiderScheduler, ScfScrapydScheduler(config, application))
