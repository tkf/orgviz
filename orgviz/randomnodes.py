import random
import datetime

from .utils.date import timedeltastr, total_seconds


class RandomDatetime(object):

    def __init__(self, pre_days=30, post_days=30, hour_min=6, hour_max=21):
        self.pre_days = pre_days
        self.post_days = post_days
        self.hour_min = hour_min
        self.hour_max = hour_max
        self.now = datetime.datetime.now()
        self.zero = datetime.datetime(*self.now.timetuple()[:3])

    def datetime(self, pre=None, post=None):
        pre = self.pre_days if pre is None else pre
        post = self.post_days if post is None else post
        delta = datetime.timedelta(
            random.randrange(- pre, post + 1),
            random.randrange(self.hour_min, self.hour_max) * 60 * 60)
        return self.zero + delta

    def date(self, **kwds):
        return datetime.date(*self.datetime(**kwds).timetuple()[:3])

    def datetimerange(self, **kwds):
        return self._start_end(self.datetime(**kwds), self.datetime(**kwds))

    def daterange(self, **kwds):
        return self._start_end(self.datetime(**kwds), self.datetime(**kwds))

    @staticmethod
    def _start_end(d1, d2):
        if total_seconds(d1 - d2) < 0:
            return (d1, d2)
        else:
            return (d2, d1)


def node(level, heading, todo=None, scheduled=None, deadline=None,
         closed=None, clock=[], tags=[], datelist=[], rangelist=[]):
    active_datestr = lambda x: x.strftime('<%Y-%m-%d %a>')
    inactive_datestr = lambda x: x.strftime('[%Y-%m-%d %a %H:%M]')
    yield '*' * level
    yield ' '
    if todo:
        yield todo
        yield ' '
    yield heading
    if tags:
        yield '  :{0}:'.format(':'.join(tags))
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
    for (clock_start, clock_end) in clock:
        yield ' ' * (level + 1)
        yield 'CLOCK: '
        yield inactive_datestr(clock_start)
        yield '--'
        yield inactive_datestr(clock_end)
        yield ' => '
        yield timedeltastr(clock_end - clock_start)
        yield '\n'
    for date in datelist:
        yield inactive_datestr(date)
        yield '\n'
    for (start, end) in rangelist:
        yield inactive_datestr(start)
        yield '--'
        yield inactive_datestr(end)
        yield '\n'


def makeorg(num, **kwds):
    heading_pops = ['aaa', 'bbb', 'ccc']
    tags_pops = ['work', 'boss', 'notes', 'action', '@home', '@work']
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
                kwds['closed'] = rd.datetime(post=0)
                kwds['todo'] = 'DONE'
        for sdc in ['scheduled', 'deadline']:
            if random.choice(true_or_false):
                kwds[sdc] = rd.date()
        if random.choice(true_or_false):
            kwds['clock'] = clock = []
            for _ in range(random.randrange(1, 5)):
                start = rd.datetime(post=0)
                end = start + datetime.timedelta(
                    0, random.randrange(30, 180) * 60)
                clock.append((start, end))
        if random.choice(true_or_false):
            kwds['tags'] = [random.choice(tags_pops)]
        if random.choice(true_or_false):
            if random.choice(true_or_false):
                kwds['datelist'] = [
                    rd.datetime()
                    for _ in range(random.randrange(1, 5))]
            else:
                kwds['rangelist'] = [
                    rd.datetimerange()
                    for _ in range(random.randrange(1, 5))]
        for s in node(**kwds):
            yield s


def writeorg(file, *args, **kwds):
    file.writelines(makeorg(*args, **kwds))


def run(num):
    import sys
    writeorg(sys.stdout, num)
