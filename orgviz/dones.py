#!/usr/bin/env python
"""org archive to html table converter"""

import os
import datetime


def minute_to_str(m):
    """
    >>> minute_to_str(70)
    '01:10'
    >>> minute_to_str(200)
    '03:20'
    """
    return '%02d:%02d' % (m // 60, m % 60)


def rootname_from_archive_olpath(node):
    """
    Find rootname from ARCHIVE_OLPATH property.
    Return None if not found.
    """
    olpath = node.Property('ARCHIVE_OLPATH')
    if olpath:
        olpathlist = olpath.split('/', 1)
        if len(olpathlist) > 1:
            (rootname, dummy) = olpathlist
        else:
            rootname = olpath
        return rootname
    return None


def find_rootname(node):
    """
    Find rootname given node
    """
    rootname = rootname_from_archive_olpath(node)
    if not rootname:
        n = node
        p = node.Parent()
        while p != None:
            n = p
            p = p.Parent()
        # n is root node
        rootname = rootname_from_archive_olpath(n) or n.Heading()
    return rootname


def key_row_from_node(node):
    """
    Return three tuple (key, row) whose elemens are
    key object for sorting table and dictionary which has following
    keywords: heading, closed, scheduled, effort, clocksum, rootname.
    """
    heading = node.Heading()
    # find rootname
    rootname = find_rootname(node)
    if heading == rootname:
        rootname = ""
    # calc clocksum if CLOCK exists
    clocksum = ''
    clocklist = node.Clock()
    if clocklist:
        clocksum = sum([k for (i,j,k) in clocklist])
    closed = node.Closed()
    scheduled = node.Scheduled()
    effort = node.Property('Effort')
    row = dict(
        heading = heading,
        closed = closed and closed.strftime('%a %d %b %H:%M'),
        scheduled = scheduled and scheduled.strftime('%a %d %b %H:%M'),
        effort = effort and minute_to_str(effort),
        clocksum = clocksum and minute_to_str(clocksum),
        rootname = rootname,
        )
    return (closed, row)


def unique_name_from_paths(pathlist):
    namelist = []
    for path in pathlist:
        name = os.path.basename(path)
        if name in namelist:
            name_orig = name
            i = 1
            while name not in namelist:
                name = "%s <%d>" % (name_orig, i)
                i += 1
        namelist.append(name)
    return namelist


def sameday(dt1, dt2):
    return (isinstance(dt1, datetime.date) and
            isinstance(dt2, datetime.date) and
            dt1.year == dt2.year and
            dt1.month == dt2.month and
            dt1.day == dt2.day)


def table_add_oddday(key_table):
    """
    Add oddday key in each rows of key_table *IN PLACE*.
    Note that key should be a ``datetime.date`` object.
    """
    previous = None
    odd = True
    for (key, row) in key_table:
        this = key
        if not sameday(this, previous):
            odd = not odd
        row['oddday'] = odd
        previous = this


def get_data(orgnodes_list, orgpath_list, done):
    """
    Get data for rendering jinja2 template. Data is dictionary like this:

    table: list of `row`
        list of row generated by ``row_from_node``
    orgpathname_list: list of `orgpathname`
        orgpathname: dict
            contains `orgpath` and `orgname`.
            `orgname` is short and unique name for `orgpath`.
    title: str
        a title

    """
    key_table = []
    orgname_list = unique_name_from_paths(orgpath_list)
    for (nodelist, orgname) in zip(orgnodes_list, orgname_list):
        for node in nodelist:
            if node.Todo() == done:
                (key, row) = key_row_from_node(node)
                if key:
                    row['orgname'] = orgname
                    key_table.append((key, row))
    orgpathname_list = [
        dict(orgpath=orgpath, orgname=orgname)
        for (orgpath, orgname) in zip(orgpath_list, orgname_list)]
    key_table.sort(reverse=True)
    table_add_oddday(key_table)
    table = [row for (key, row) in key_table]
    return dict(table=table, orgpathname_list=orgpathname_list,
                title='Recently archived tasks')
