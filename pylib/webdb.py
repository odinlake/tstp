from collections import defaultdict
import webobject
import textwrap


OBJECT_COLLECTIONS = {
    r"tos\dx\d\d": "Star Trek: The Original Series",
    r"tas\dx\d\d": "Star Trek: The Animated Series",
    r"tng\dx\d\d": "Star Trek: The Next Generation",
    r"ds9\dx\d\d": "Star Trek: Deep Space 9",
    r"voy\dx\d\d": "Star Trek: Voyager",
    r"ent\dx\d\d": "Star Trek: Enterprise",
    r"bbf\dx\d\d": "Babylon 5",
}


SUPPORTED_OBJECTS = {
    "storydefinitions": webobject.Story,
    "themedefinitions": webobject.Theme,
    "storythemes": webobject.StoryTheme,
}


def get_metatheme_data():
    """
    Returns
    -------
    leaf_data: { leaf_theme => [(sid1, weight1), ...], ...},
    meta_data: { meta_theme => [(sid1, weight1), ...], ...},
    parents: { theme => [parent1, ...] },
    children: { theme => [child1, ...] },
    toplevel: [ theme1, ...],
    """
    themes = webobject.Theme.load()
    storythemes = webobject.StoryTheme.load()
    parent_lu = {}
    child_lu = defaultdict(set)
    toplevel = set()
    meta_data = defaultdict(set)
    leaf_data = defaultdict(set)
    ret_meta_data = {}
    ret_leaf_data = {}
    ret_child_lu = {}

    for theme in themes:
        parents = [ t.strip() for t in theme.parents.split(",") if t.strip() ]
        parent_lu[theme.name] = parents

        for parent in parents:
            child_lu[parent].add(theme.name)

        if not parents:
            toplevel.add(theme.name)

    for st in storythemes:
        theme = st.name2
        theme_stack = [ theme ]
        item = (st.name1, st.weight)
        leaf_data[theme].add(item)
        first = True

        while theme_stack:
            theme = theme_stack.pop()

            if not first:
                meta_data[theme].add(item)

            first = False

            if theme in parent_lu:
                theme_stack.extend(parent_lu[theme])

    for key, items in meta_data.iteritems():
        ret_meta_data[key] = sorted(items)

    for key, items in leaf_data.iteritems():
        ret_leaf_data[key] = sorted(items)

    for key, items in child_lu.iteritems():
        ret_child_lu[key] = sorted(items)

    toplevel = sorted(toplevel)
    return ret_leaf_data, ret_meta_data, parent_lu, ret_child_lu, toplevel


def get_defenitions(target):
    """
    Returns
    -------
    [ (...), ... ]
    Table rows with the headers in the first row.
    """
    klass = SUPPORTED_OBJECTS[target]
    remap = {
        "name": target[:5],
        "name1": "story",
        "name2": "theme",
    }
    
    objs = klass.load()
    headers = [ f for f in klass.fields if "category" not in f ]
    rows = [ [remap.get(f, f) for f in headers] ]
    
    for obj in objs:
        row = []
        for field in headers:
            row.append(unicode(getattr(obj, field)).encode("utf-8"))
        rows.append(row)

    return rows


def get_defenitions_text(target):
    """
    Returns
    -------
    Same as get_defenitions but in this project's special text format.
    """
    klass = SUPPORTED_OBJECTS[target]
    objs = klass.load()
    return get_defenitions_text_for_objects(objs)


def get_defenitions_text_for_objects(objs, empty_storythemes_headers = False):
    if not objs:
        return ""

    o0 = objs[0]
    target, klass = next((k, v) for k, v in SUPPORTED_OBJECTS.iteritems() if isinstance(o0, v))
    headers = [ f for f in klass.fields if "category" not in f ]
    grouped = defaultdict(list)
    lines = []

    for obj in objs:
        obj_name = getattr(obj, headers[0])
        grouped[obj_name].append(obj)

    for obj_name in sorted(grouped):
        lines.append(obj_name)
        lines.append("=" * len(obj_name))
        lines.append("")

        if target != "storythemes":
            for obj in grouped[obj_name]:
                for field in headers[1:]:
                    lines.append(":: " + field.capitalize())
                    for txt in getattr(obj, field).split("\n\n"):
                        lines.append(textwrap.fill(txt, 78))
                        lines.append("")

        if target == "storythemes" or empty_storythemes_headers:
            for field in [ "choice", "major", "minor" ]:
                lines.append(":: " + field.capitalize() + " Themes")
                items = []

                if not empty_storythemes_headers:
                    for obj in grouped[obj_name]:
                        if obj.weight == field:
                            items.append("%s [%s]" % (obj.name2, obj.motivation))

                items.sort()
                lines.extend(item + "," for item in items)
                lines.append("")

        lines.append("")

    return "\n".join(lines)


if __name__ == '__main__':
    get_metatheme_data()



