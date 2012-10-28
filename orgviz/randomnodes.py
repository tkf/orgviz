import random
import datetime


class RandomDatetime(object):

    def __init__(self, pre_days=30, post_days=30):
        self.pre_days = pre_days
        self.post_days = post_days
        self.now = datetime.datetime.now()

    def datetime(self, pre=None, post=None):
        pre = pre or self.pre_days
        post = post or self.post_days
        delta = datetime.timedelta(random.randrange(- pre, post + 1))
        return self.now + delta

    def date(self, **kwds):
        return datetime.date(*self.datetime(**kwds).timetuple()[:3])


def node(level, heading, todo=None, scheduled=None, deadline=None,
         closed=None, clock=None):
    active_datestr = lambda x: x.strftime('<%Y-%m-%d %a>')
    inactive_datestr = lambda x: x.strftime('[%Y-%m-%d %a]')
    yield '*' * level
    yield ' '
    if todo:
        yield todo
        yield ' '
    yield heading
    yield '\n'
    if scheduled or deadline or closed:
        yield ' ' * level
    for (name, date, datestr) in [('CLOSED', closed, inactive_datestr),
                                  ('DEADLINE', deadline, active_datestr),
                                  ('SCHEDULED', scheduled, active_datestr)]:
        if date:
            yield ' '
            yield name
            yield ': '
            yield datestr(date)
    if scheduled or deadline or closed:
        yield '\n'


def makeorg(num, **kwds):
    heading_pops = ['aaa', 'bbb', 'ccc']
    true_or_false = [True, False]
    rd = RandomDatetime(**kwds)
    for i in range(num):
        kwds = {}
        if i == 0:
            kwds['level'] = 1
        else:
            kwds['level'] = random.randrange(1, 4)
        kwds['heading'] = random.choice(heading_pops)
        if random.choice(true_or_false):
            if random.choice(true_or_false):
                kwds['todo'] = 'TODO'
            else:
                kwds['closed'] = rd.date(post=0)
                kwds['todo'] = 'DONE'
        for sdc in ['scheduled', 'deadline']:
            if random.choice(true_or_false):
                kwds[sdc] = rd.date()
        for s in node(**kwds):
            yield s


def writeorg(file, *args, **kwds):
    file.writelines(makeorg(*args, **kwds))


def run(num):
    import sys
    writeorg(sys.stdout, num)
