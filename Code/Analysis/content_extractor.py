# coding: utf8
"""
  The text extractor module. It uses several heuristics to score
  content in dom like link density, punctuations, classes and more.
  Structure heavily inspired by the Readability project https://code.google.com/archive/p/arc90labs-readability/
"""
from bs4 import BeautifulSoup, Comment, Tag, NavigableString
import copy
import zipfile
import tempfile
import shutil
import os
import re
import json
import sys

"""
  CONSTANTS
"""
REGEXPS = {
    "unlikelyCandidates": re.compile(r"hidden|banner|breadcrumbs|combx|comment|community|cover-wrap|disqus|extra|foot|header|legends|menu|related|remark|replies|rss|shoutbox|sidebar|skyscraper|social|sponsor|supplemental|ad-break|agegate|pagination|pager|popup|yom-remote|ad", re.I),
    "okMaybeItsACandidate": re.compile(r"and|article|body|column|main|shadow", re.I),
    "positive": re.compile(r"article|body|content|entry|hentry|h-entry|main|page|pagination|post|text|blog|story", re.I),
    "negative": re.compile(r"hidden|^hid$| hid$| hid |^hid |banner|combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|share|shoutbox|sidebar|skyscraper|sponsor|shopping|tags|tool|widget", re.I),
    "extraneous": re.compile(r"print|archive|comment|discuss|e[\-]?mail|share|reply|all|login|sign|single|utility", re.I),
    "byline": re.compile(r"byline|author|dateline|writtenby|p-author", re.I),
    "normalize": re.compile(r"\s{2,}"),
    "videos": re.compile(r"\/\/(www\.)?(dailymotion|youtube|youtube-nocookie|player\.vimeo)\.com", re.I),
    "nextLink": re.compile(r"(next|weiter|continue|>([^\|]|$)|»([^\|]|$))", re.I),
    "prevLink": re.compile(r"(prev|earl|old|new|<|«)", re.I),
    "whitespace": re.compile(r"^\s*/"),
    "hasContent": re.compile(r"\S$/"),
    "hasTextContent": re.compile(r"\S"),
}

DEFAULT_TAGS_TO_SCORE = ["section", "h2",
                         "h3", "h4", "h5", "h6", "p", "td", "pre"]
NUM_OF_TOP_CANDIDATES = 5


"""
  UTILS
"""

def inner_html(node):
    return node.encode_contents()


def get_children(node):
    if node == None:
        return []
    return list(filter(lambda x: is_tag(x), list(node.children)))


def get_ancestors(node, maxDepth=0):
    i = 0
    ancestors = []
    while node != None and node.parent != None:
        ancestors.append(node.parent)
        i += 1
        if maxDepth and i == maxDepth:
            break
        node = node.parent
    return ancestors


def has_single_p_inside_element(element):
    ch = get_children(element)
    if len(ch) != 1 or ch[0].name != 'p':
        return False
    has_content = [c for c in element.contents
                   if type(c) == NavigableString and re.search(REGEXPS['hasTextContent'], c) != None]
    return not any(has_content)


def has_child_block_elements(element):
    DIV_TO_P_ELEMS = ["a", "blockquote", "dl", "div",
                      "img", "ol", "p", "pre", "table", "ul", "select"]
    hasBlock = False
    for node in get_children(element):
        hasBlock = node.name in DIV_TO_P_ELEMS or has_child_block_elements(
            node)
    return hasBlock


def is_empty_candidate(node):
    return node.name == 'div' or node.name == 'section' or node.name == 'header' \
        or node.name == 'h1' or node.name == 'h2' or node.name == 'h3' \
        or node.name == 'h4' or node.name == 'h5' or node.name == 'h6'


def is_element_without_content(node):
    return len(node.get_text().strip()) == 0 and (len(node.contents) == 0 or
                                                  len(node.contents) == len(node.find_all('br')) + len(node.find_all('hr')))


def remove_and_get_next(node):
    nxt_node = get_next_node(node, True)
    node.extract()
    return nxt_node


def get_next_node(node, ignoreSelfAndKids=False):
    if(not ignoreSelfAndKids and first_element_child(node)):
        return first_element_child(node)

    if next_element_sibling(node):
        return next_element_sibling(node)

    node = node.parent
    while node and not next_element_sibling(node):
        node = node.parent

    return node and next_element_sibling(node)


def get_class_name(node):
    if 'class' not in node.attrs:
        return ""
    return str.join(' ', node.get('class'))


def get_id_str(node):
    if not node.get('id'):
        return ""
    return node.get('id')


def get_role_attr(node):
    if not node.get('role'):
        return ""
    return node.get('role')


def is_tag(item):
    return item != None and type(item) == Tag


def first_element_child(n):
    el = False
    for c in n.children:
        if not el and is_tag(c):
            el = c
            break
    return el


def next_element_sibling(n):
    el = False
    for c in n.next_siblings:
        if not el and is_tag(c):
            el = c
            break
    return el


""" Content score helpers """

def get_link_density(element):
    """
    Get the density of links as a percentage of the content
    This is the amount of text that is inside a link divided by the total text in the node
    """
    txt_len = len(element.get_text())
    if txt_len == 0:
        return 0

    link_len = 0
    links = element.find_all('a')
    for l in links:
        link_len += len(l.get_text())

    return link_len / txt_len

def was_score_initialized(node):
    return node.get('data-contentscore') != None


def get_score(node):
    if not node.get('data-contentscore'):
        return 0
    return int(node['data-contentscore'])


def set_score(node, score):
    if type(score) == 'str':
        score = int(score)
    node['data-contentscore'] = str(score)


def get_class_weight(node):
    # TODO: Add flag conditional, might not be needed after first pass
    weight = 0

    className = get_class_name(node)
    if className.strip() != "":
        if re.search(REGEXPS['negative'], className) != None:
            weight -= 25
        if re.search(REGEXPS['positive'], className) != None:
            weight += 25

    idstr = get_id_str(node)
    if idstr != "":
        if re.search(REGEXPS['negative'], idstr) != None:
            weight -= 25
        if re.search(REGEXPS['positive'], idstr) != None:
            weight += 25

    return weight


def initialize_node(node):
    set_score(node, 0)
    if node.name == 'div':
        set_score(node, get_score(node) + 5)
    elif node.name in ['pre', 'td', 'blockquote']:
        set_score(node, get_score(node) + 3)
    elif node.name in ['address', 'ol', 'ul', 'dl', 'dd', 'dt', 'li', 'form']:
        set_score(node, get_score(node) - 3)
    elif node.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'th']:
        set_score(node, get_score(node) - 5)
    else:
        pass

    set_score(node, get_score(node) + get_class_weight(node))


"""
  DOC PREP
"""

def remove_scripts(doc):
    nodes = doc.find_all('script')
    for n in nodes: n.extract()

    no_scripts = doc.find_all('noscript')
    for n in no_scripts: n.extract()

    head = doc.find('head')
    for el in head(text=lambda text: isinstance(text, Comment)):
        el.extract()

    return doc

"""
Replaces 2 or more successive <br> elements with a single <p>.
"""
def replace_brs(elem, doc):
    all_brs = elem.find_all('br')

    for br in all_brs:
        if not br: continue
        nxt = br.next_element
        replaced = False

        while nxt != None and is_tag(nxt.next_element) and nxt.next_element.name == 'br':
            replaced = True
            nxt = nxt.next_element
            brSibl = nxt.next_element
            nxt.extract()
            nxt = brSibl

        if replaced:
            p = doc.new_tag('p')
            br.replace_with(p)

            if p.next_element != None:
                nxt = p.next_element
                while nxt != None:
                    if type(nxt) == Tag and \
                    nxt.name == 'br' and \
                    nxt.next_element != None and \
                    type(nxt.next_element) == Tag and \
                    nxt.next_element.name == 'br':
                        break;

                    sibl = nxt.next_element
                    if sibl:
                        p.append(sibl)
                    nxt = sibl

    return doc

def prep_document(doc):
    styles = doc.find_all('style')
    for n in styles: n.extract()

    body = doc.body
    doc = replace_brs(body, doc)

    return doc

def check_byline(node, match_string):
    pass

"""
  Main parser
"""


def get_article(doc):
    FLAG_STRIP_UNLIKELYS = True

    page = doc.body
    if not page:
        return None

    page_cache = inner_html(page)

    stripUnlinkelyCandidates = FLAG_STRIP_UNLIKELYS
    elementsToScore = []
    node = page

    while node != None:
        matchString = get_class_name(
            node) + " " + get_id_str(node) + " " + get_role_attr(node)
        # TODO: checkByline(node)

        # Remove Unlikely Candidates
        if stripUnlinkelyCandidates:
            if re.search(REGEXPS['unlikelyCandidates'], matchString) \
                    and not re.search(REGEXPS['okMaybeItsACandidate'], matchString) \
                    and node.name != 'body' and node.name != 'a':
                # print('debug: Removing unlikely candidate - ', matchString)
                node = remove_and_get_next(node)
                continue

        #Remove DIV, SECTION, and HEADER nodes without any content(e.g. text, image, video, or iframe).
        if is_empty_candidate(node) and is_element_without_content(node):
            node = remove_and_get_next(node)
            continue

        if node.name in DEFAULT_TAGS_TO_SCORE:
            elementsToScore.append(node)

        if node.name == 'div':
            if has_single_p_inside_element(node):
                new_node = get_children(node)[0]
                node.replace_with(new_node)
                node = new_node
                elementsToScore.append(node)

            if has_child_block_elements(node):
                node.name = 'p'
                elementsToScore.append(node)

        node = get_next_node(node)

    candidates = []
    for elToScore in elementsToScore:
        if elToScore.parent == None:
            continue

        innerText = elToScore.get_text().strip()
        if len(innerText) < 25:
            continue

        ancestors = get_ancestors(elToScore, 3)
        if len(ancestors) == 0:
            continue

        content_score = 0

        # add a point for the paragraph itself as a base
        content_score += 1

        # add points for any commas in the paragraph
        content_score += len(innerText.split(','))

        content_score += min(len(innerText)//100, 3)

        for level, ances in enumerate(ancestors):
            if ances.name == '' or ances.name == '[document]':
                continue

            if not was_score_initialized(ances):
                initialize_node(ances)
                candidates.append(ances)

            if level == 0:
                score_divider = 1
            elif level == 1:
                score_divider = 2
            else:
                score_divider = level * 3

            set_score(ances, get_score(ances) +
                      get_score(ances) // score_divider)

    top_candidates = []
    for c in top_candidates:
        adjusted_score = int(get_score(c) * (1 - get_link_density()))
        set_score(c, adjusted_score)

    top_candidates = sorted(
        candidates, key=lambda x: get_score(x), reverse=True)
    top_candidates = top_candidates[:NUM_OF_TOP_CANDIDATES]

    if len(top_candidates) == 0:
        return doc.body.get_text()

    txt = [re.sub(REGEXPS['normalize'], " ", n.get_text())
           for n in top_candidates]
    # debug, see simplified cleaned html
    #txt = [n for n in top_candidates]
    return txt[0]


def parse(file_path):
    with open(file_path) as fp:
        soup = BeautifulSoup(fp, "lxml")
        try:
            doc = copy.copy(soup)

            doc = remove_scripts(soup)
            doc = prep_document(doc)
            content = get_article(doc)
            return content
        except Exception as e:
            return None

def extract_content_from_html(file_name):
    """
    Open html fuke and extract content
    """
    return parse(file_name)
