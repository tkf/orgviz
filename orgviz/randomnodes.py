import random
import datetime


class RandomDatetime(object):

    def __init__(self, datewidth=7):
        self.datewidth = datewidth
        self.now = datetime.datetime.now()

    def datetime(self):
        delta = datetime.timedelta(random.randrange(- self.datewidth,
                                                    self.datewidth + 1))
        return self.now + delta

    def date(self):
        return datetime.date(*self.datetime().timetuple()[:3])


def node(level, heading, scheduled=None, deadline=None, closed=None,
         clock=None):
    datestr = lambda x: x.strftime('<%Y-%m-%d %a>')
    yield '*' * level
    yield ' '
    yield heading
    yield '\n'
    if scheduled or deadline or closed:
        yield ' ' * level
    for (name, date) in [('CLOSED', closed),
                         ('DEADLINE', deadline),
                         ('SCHEDULED', scheduled)]:
        if date:
            yield ' '
            yield name
            yield ': '
            yield datestr(date)
    if scheduled or deadline or closed:
        yield '\n'


def makeorg(num):
    heading_pops = ['aaa', 'bbb', 'ccc']
    true_or_false = [True, False]
    rd = RandomDatetime()
    for i in range(num):
        kwds = {}
        if i == 0:
            kwds['level'] = 1
        else:
            kwds['level'] = random.randrange(1, 4)
        kwds['heading'] = random.choice(heading_pops)
        for sdc in ['scheduled', 'deadline', 'closed']:
            if random.choice(true_or_false):
                kwds[sdc] = rd.date()
        for s in node(**kwds):
            yield s


def writeorg(file, *args, **kwds):
    file.writelines(makeorg(*args, **kwds))


def run(num):
    import sys
    writeorg(sys.stdout, num)
