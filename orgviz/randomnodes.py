import random
import datetime


class RandomDatetime(object):

    def __init__(self, pre_days=30, post_days=30):
        self.pre_days = pre_days
        self.post_days = post_days
        self.now = datetime.datetime.now()

    def datetime(self, pre=None, post=None):
        pre = self.pre_days if pre is None else pre
        post = self.post_days if post is None else post
        delta = datetime.timedelta(random.randrange(- pre, post + 1))
        return self.now + delta

    def date(self, **kwds):
        return datetime.date(*self.datetime(**kwds).timetuple()[:3])


def timedeltastr(timedelta):
    hour = timedelta.seconds // 60 // 60
    min = timedelta.seconds // 60 - (hour * 60)
    return '{0:02d}:{1:02d}'.format(timedelta.days * 24 + hour, min)


def node(level, heading, todo=None, scheduled=None, deadline=None,
         closed=None, clock=[], tags=[]):
    active_datestr = lambda x: x.strftime('<%Y-%m-%d %a>')
    inactive_datestr = lambda x: x.strftime('[%Y-%m-%d %a]')
    inactive_datetimestr = lambda x: x.strftime('[%Y-%m-%d %a %H:%M]')
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
        yield inactive_datetimestr(clock_start)
        yield '--'
        yield inactive_datetimestr(clock_end)
        yield ' => '
        yield timedeltastr(clock_end - clock_start)
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
                kwds['closed'] = rd.date(post=0)
                kwds['todo'] = 'DONE'
        for sdc in ['scheduled', 'deadline']:
            if random.choice(true_or_false):
                kwds[sdc] = rd.date()
        if random.choice(true_or_false):
            kwds['clock'] = clock = []
            for _ in range(random.randrange(1, 5)):
                delta = datetime.timedelta(0, (6 - rd.now.hour) * 60 * 60)
                rd.now = rd.now + delta
                start = rd.datetime(post=0)
                start = start + datetime.timedelta(
                    0, random.randrange(0, 13) * 60 * 60)
                end = start + datetime.timedelta(
                    0, random.randrange(1, 5) * 60 * 60)
                clock.append((start, end))
        if random.choice(true_or_false):
            kwds['tags'] = [random.choice(tags_pops)]
        for s in node(**kwds):
            yield s


def writeorg(file, *args, **kwds):
    file.writelines(makeorg(*args, **kwds))


def run(num):
    import sys
    writeorg(sys.stdout, num)
