from __future__ import print_function
import cgitb; cgitb.enable()
import log
log.set_level('SILENT')
import urllib
import lib.datastats


log.set_logmode("binary")


def make_link(theme, display=None):
    theme = theme.encode("utf-8")
    url = "http://www.themeontology.org/theme.php?name=%s" % urllib.quote_plus(theme)
    display = display or theme
    return '<A href="%s">%s</A>' % (url, display)


def main():
    parents, children, lforder = lib.datastats.get_theme_tree()
    roots = sorted(th for th, thp in parents.iteritems() if len(thp) == 0)
    leafcount = {}
    arrow = u'\u2190'.encode("utf-8")

    for theme in lforder:
        for parent in parents[theme]:
            count = sum(leafcount.get(ch, 0) for ch in children[parent])
            count2 = sum(1 for ch in children[parent] if len(children[ch]) == 0)
            leafcount[parent] = count + min(1, count2)

    for root in roots:
        rootlink = make_link(root)
        print("<H1>%s</H1>" % rootlink)

        for l2 in children[root]:
            pending = list(children[l2])
            l2link = make_link(l2)
            print("  <H2>%s %s %s</H2>" % (rootlink, arrow, l2link))
            print("  <TABLE>")

            while any(pending):
                pending, current = [], pending
                print("<tr>")
                for theme in current:
                    if theme in leafcount:
                        nn = leafcount[theme]
                        print("<th colspan=%s>%s</th>" % (nn, make_link(theme)))
                        pending.extend(th for th in children[theme] if children[th])
                        acc = [th for th in children[theme] if not children[th]]
                        if acc:
                            pending.append(tuple(acc))
                    else:
                        acc = theme
                        if isinstance(acc, tuple):
                            item = ", ".join(make_link(th) for th in acc[:4])
                            if len(acc) > 4:
                                item += ", ..."
                        else:
                            item = make_link(theme)
                        print("<td>%s</td>" % item)
                        pending.append("")

                print("</tr>")
            print("  </TABLE>")
