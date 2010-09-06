# -*- coding: utf-8 -*-
import os.path
import re
from urlparse import urljoin
from datetime import datetime
from mimetypes import guess_type
from fnmatch import fnmatch
from werkzeug import cached_property
from flask import url_for


Default = None


class Entry(object):
    """This class wraps file or folder. It is an abstract class, but it returns
    derived class. You can make an instance such as::

        folder = Entry("/home/someone/public_html")
        assert isinstance(foler, Folder)
        file = Entry("/home/someone/public_html/favicon.ico")
        assert isinstance(file, File)
    """

    HIDDEN = re.compile("^\.")

    def __new__(cls, path, root=None, autoindex=None):
        """Returns a file or folder instance."""
        if cls is not Entry:
            return object.__new__(cls)
        abspath = os.path.join(root, path)
        if os.path.isdir(abspath):
            return Folder(path, root)
        elif os.path.isfile(abspath):
            return File(path, root)
        else:
            raise IOError("'{0}' does not exists.".format(fullpath))

    def __init__(self, path, root=None, autoindex=None):
        """Initializes an entry instance."""
        self.path = path
        if root:
            self.root = root
        else:
            self.root = os.path.abspath(os.path.curdir)
        self.abspath = os.path.join(self.root, self.path)
        self.name = os.path.basename(self.abspath)
        self.hidden = bool(self.HIDDEN.match(self.name))
        self.autoindex = autoindex

    @property
    def parent(self):
        if self.is_root():
            return None
        return Entry(os.path.dirname(self.path), self.root, self.autoindex)

    def is_root(self):
        return os.path.samefile(self.abspath, self.root)

    @property
    def modified(self):
        """Returns modified time of this."""
        return datetime.fromtimestamp(os.path.getmtime(self.abspath))

    @classmethod
    def add_icon_rule(cls, icon, rule=None):
        """Adds a new icon rule globally."""
        cls.icon_map.append((icon, rule))

    @classmethod
    def add_icon_rule_by_name(cls, icon, name):
        cls.add_icon_rule(icon, lambda ent: ent.name == name)

    @classmethod
    def add_icon_rule_by_class(cls, icon, _class):
        cls.add_icon_rule(icon, lambda ent: isinstance(ent, _class))

    def guess_icon(self):
        """Guesses an icon from itself."""
        def get_icon_url():
            try:
                if self.autoindex:
                    icon_map = self.autoindex.icon_map + self.icon_map
                else:
                    icon_map = self.icon_map
                for icon, rule in icon_map:
                    if not rule and callable(icon):
                        matched = icon = icon(self)
                    else:
                        matched = rule(self)
                    if matched:
                        return icon
            except AttributeError:
                pass
            try:
                return self.default_icon
            except AttributeError:
                raise GuessError("There is no matched icon.")
        return urljoin(url_for("silkicon", filename=""), get_icon_url())


class File(Entry):

    EXTENSION = re.compile("\.(.+)$")

    default_icon = "page_white.png"
    icon_map = []

    def __init__(self, path, root=None, autoindex=None):
        super(File, self).__init__(path, root, autoindex)
        self.size = os.path.getsize(self.abspath)
        try:
            self.ext = re.search(self.EXTENSION, self.name).group(1)
        except AttributeError:
            self.ext = None

    def to_html(self):
        text = "".join(self.readlines())
        text = text.decode("utf-8")
        try:
            if self.ext in ("markdown", "md"):
                from markdown import Markdown
                return Markdown().convert(text)
        except ImportError:
            pass
        return "<pre>{0}</pre>".format(text)

    def readlines(self):
        return self.stream.readlines()

    @cached_property
    def stream(self):
        return open(self.abspath)

    @cached_property
    def mimetype(self):
        return guess_type(self.abspath)

    @classmethod
    def add_icon_rule_by_ext(cls, icon, ext):
        cls.add_icon_rule(icon, lambda ent: ent.ext == ext)

    @classmethod
    def add_icon_rule_by_mimetype(cls, icon, mimetype):
        rule = lambda ent: fnmatch(guess_type(ent.name)[0] or "", mimetype)
        cls.add_icon_rule(icon, rule)


class Folder(Entry):

    default_icon = "folder.png"
    icon_map = []

    def __new__(cls, path, root=None, autoindex=None):
        if cls is not Folder:
            return object.__new__(cls)
        elif root and os.path.samefile(os.path.join(root, path), root):
            return RootFolder(path, root, autoindex)
        return object.__new__(cls)

    def browse(self, sort_by="name", order=1, show_hidden=False):
        def compare(ent1, ent2):
            def asc():
                if sort_by != "modified" and type(ent1) is not type(ent2):
                    return 1 if type(ent1) is File else -1
                else:
                    try:
                        return cmp(getattr(ent1, sort_by),
                                   getattr(ent2, sort_by))
                    except AttributeError:
                        return cmp(getattr(ent1, "name"),
                                   getattr(ent2, "name"))
                    #return -order
            return asc() * order
        if not self.is_root():
            yield ParentFolder(self)
        entries = os.listdir(self.abspath)
        entries = (Entry(os.path.join(self.path, name),
                         self.root, self.autoindex) for name in entries)
        entries = sorted(entries, cmp=compare)
        for ent in entries:
            if show_hidden or not ent.hidden:
                yield ent

    def get_readme(self, readme_filename="README"):
        readmes = [p for p in os.listdir(self.abspath) \
                   if p.startswith(readme_filename)]
        if readmes:
            return self.get_file(readmes[0])
        raise IOError("{0} folder has no readme file.".format(self.name))

    def get_file(self, filename):
        return File(os.path.join(self.abspath, filename))


class ParentFolder(Folder):

    default_icon = "arrow_turn_up.png"
    icon_map = []

    def __init__(self, child_folder):
        path = os.path.join(child_folder.path, "..")
        super(ParentFolder, self).__init__(path, child_folder.root,
                                                 child_folder.autoindex)


class RootFolder(Folder):

    default_icon = "server.png"
    icon_map = []

    def __init__(self, path, root, autoindex=None):
        super(RootFolder, self).__init__(".", root, autoindex)


class GuessError(RuntimeError): pass

