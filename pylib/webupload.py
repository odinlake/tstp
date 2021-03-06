import cgitb; cgitb.enable()
import lib.log as log
log.set_level('SILENT')
log.set_templog("web.log")

from collections import defaultdict
import cgi
import cPickle as pickle
import os
import re
import sys
import traceback

from db import do
from lib.xls import read_xls, write_xls
from lib.dataparse import expload_field
from webobject import StoryTheme, Story, Theme, TSTPEvent
from webphp import php_get, FILES, get_pending_path, get_userfile_path
import webobject


def cancel_pending_events():
    fn = get_pending_path()
    try:
        os.unlink(fn)
    except (IOError, OSError):
        pass
    

def get_pending_events():
    fn = get_pending_path()
    try:
        with open(fn, "rb") as fh:
            return pickle.load(fh)["events"]
    except (IOError, KeyError):
        return []
    
    
def save_pending_events(events):
    fn = get_pending_path()
    with open(fn, "wb+") as fh:
        pickle.dump({ "events": events }, fh, 1)


def commit_pending_events():
    events = get_pending_events()
    TSTPEvent.commit_many(events)
    cancel_pending_events()


def read_various_text(filename, name):
    import lib.dataparse

    if name.endswith("th.txt"):
        objs = list(lib.dataparse.read_themes_from_txt(filename))
        themes = sorted(set(o.name for o in objs))
        existing = Theme.load(names = themes)
        key = lambda o: o.name

    elif name.endswith("st.txt"):
        objs = list(lib.dataparse.read_stories_from_txt(filename))
        sids = sorted(set(o.name for o in objs))
        existing = Story.load(names = sids)
        key = lambda o: o.name

    else:
        raise ValueError, "unknown file type: %s" % name
    
    exist_lu = {}
    events = []
    
    for obj in existing:
        exist_lu[key(obj)] = obj

    for obj_new in objs:
        obj_old = exist_lu.get(key(obj_new), None)
        events.extend(obj_new.make_edit_events(obj_old))

    return events, 1, len(objs)



def read_storythemes(filename):
    weights = {
        "Choice Theme": "choice",
        "Major Theme": "major",
        "Minor Theme": "minor",
        "Absent Theme": "absent",
    }
    headers = [
        "StoryID", 
        "Keyword", 
        "FieldName", 
        "Comment",
    ]
    relations, sheetcount, rowcount = read_xls(filename, headers)
    
    sids = sorted(set(x[0].lower() for x in relations))
    themes = sorted(set(x[1] for x in relations))
    existing = StoryTheme.load(name1s = sids)
    exist_lu = {}
    events = []
    
    for st in existing:
        exist_lu[(st.name1, st.name2)] = st
        
    for sid, kw, fieldname, motivation in relations:
        try:
            weight = weights[fieldname]
        except KeyError:
            if weight not in weights.values():
                raise IOError("Unexpected FieldName: %s" % fieldname)
        
        sid = sid.lower()
        st = exist_lu.get((sid, kw), None)
        
        if st is None:
            # add insert event
            st = StoryTheme.create(sid, kw, weight, motivation)
            events.extend(st.make_insert_events())
        else:
            if st.weight != weight:
                # edit field/weight
                events.append(st.make_edit_event("weight", weight))
            if st.motivation != motivation:
                # edit motivation
                events.append(st.make_edit_event("motivation", motivation))

    return events, sheetcount, rowcount


def read_stories(filename):
    headers = [
        "StoryID", 
        "Title", 
        "ReleaseDate", 
        "Description",
    ]
    stories, sheetcount, rowcount = read_xls(filename, headers)
    
    sids = sorted(set(x[0].lower() for x in stories))
    existing = Story.load(names = sids)
    exist_lu = {}
    events = []
    
    for st in existing:
        exist_lu[st.name] = st
        
    for sid, title, releasedate, description in stories:
        sid = sid.lower()
        st_old = exist_lu.get(sid, None)
        st_new = Story.create(
            name = sid,
            title = title,
            date = releasedate,
            description = description,
        )
        events.extend(st_new.make_edit_events(st_old))

    return events, sheetcount, rowcount


def read_themes(filename):
    headers = [
        "Keyword", 
        "Implications", 
        "Definition", 
    ]
    themes, sheetcount, rowcount = read_xls(filename, headers)
    
    keywords = sorted(set(x[0] for x in themes))
    existing = Theme.load(names = keywords)
    exist_lu = {}
    events = []
    
    for st in existing:
        exist_lu[st.name] = st
        
    for keyword, parents, description in themes:
        st_old = exist_lu.get(keyword, None)
        st_new = Theme.create(
            name = keyword,
            description = description,
            parents = parents,
        )
        events.extend(st_new.make_edit_events(st_old))

    return events, sheetcount, rowcount


def expload_compact_storythemes(filename):
    """
    Compact format has many comma-separated themes in each cell and comments in brackets.
    """
    headers = [
        "StoryID",
        "Choice Themes",
        "Major Themes",
        "Minor Themes",
    ]
    relations, sheetcount, rowcount = read_xls(filename, headers)
    sids = sorted(set(x[0].lower() for x in relations))
    errors = []
    themerows = []

    for row in relations:
        sid = row[0]

        for idx, hdr in enumerate(headers):
            if idx < 1:
                continue

            fn = hdr.strip("s")
            field = row[idx]

            try:
                themes = list(expload_field(field))
            except AssertionError as e:
                errors.append(e.message)
                continue

            for kw, com, imp, cap in themes:
                themerows.append(
                    (sid, fn, kw, com)
                )

    if errors:
        return "<b>Parsing Errors:<b><br>" + "<br>".join(errors)

    st_headers = [
        "StoryID",
        "FieldName",
        "Keyword",
        "Comment",
    ]

    path = get_userfile_path("userstorythemes.xls")
    write_xls(path, st_headers, themerows)

    return """
    Download the result here:
    <A href="download.php?what=userstorythemes&fmt=xls">userstorythemes.xls</A>
    """

    
def handle_upload():
    submit = php_get("submit")
    
    if submit == "cancel":
        cancel_pending_events()
      
    elif submit == "commit":
        commit_pending_events()
    
    elif submit == "submitfile":
        ftype = php_get("fieldType")
        meta = FILES["fieldFile"]
        filename = meta["tmp_name"]
        name = meta["name"]
        events = None
        message = None

        log.info("Handling %s file upload: %s", ftype, filename)
        
        if ftype == "varioustxt":
            events, sheetcount, rowcount = read_various_text(filename, name)
        elif ftype == "storythemes":
            events, sheetcount, rowcount = read_storythemes(filename)
        elif ftype == "compactstorythemes":
            message = expload_compact_storythemes(filename)
        elif ftype == "storydefinitions":
            events, sheetcount, rowcount = read_stories(filename)
        elif ftype == "themedefinitions":
            events, sheetcount, rowcount = read_themes(filename)
        else:
            message = "Type %s is not yet supported" % ftype 
        
        if message is None and events is not None:
            save_pending_events(events)
            message = "" if events else "Nothing to do."
            message += " Found %s changes in %s sheets and %s rows." % (
                len(events),
                sheetcount,
                rowcount,
            )

        return message


if __name__ == '__main__':
    try:
        result = handle_upload()
        if isinstance(result, str):
            print result
    
    except IOError, e:
        print "<pre>", e, "</pre>"
        
    except:
        raise # TODO remove in prod
        pass


