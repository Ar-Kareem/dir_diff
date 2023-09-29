import os
from functools import reduce
from pathlib import Path
from datetime import datetime

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    TOP_LEVEL_NAME = 'root'
    rootdir = Path(rootdir).resolve()
    start = len(str(rootdir))
    res = {
        'INFO': {
            'rootdir': str(rootdir),
            'timestamp': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'time': datetime.timestamp(datetime.now()),
        },
        TOP_LEVEL_NAME: {},
    }
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        folders = [TOP_LEVEL_NAME] + [f for f in folders if f]
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], res)
        parent[folders[-1]] = subdir
    return res

class Node:
    def __init__(self, name, old_path=None, new_path=None, parent=None):
        assert old_path is not None or new_path is not None, 'both paths are None'
        self.name = name
        self.parent = parent
        self.children: list[Node] = []
        self.old_path = old_path
        self.old_files, self.old_dirs = self.get_files_and_dirs(old_path) if old_path is not None else (set(), set())
        self.new_path = new_path
        self.new_files, self.new_dirs = self.get_files_and_dirs(new_path) if new_path is not None else (set(), set())

        self.full_name = self.name if self.parent is None else self.parent.full_name + '/' + self.name
        self.stats = {
            'files': {'old_only': float('nan'), 'new_only': float('nan'), 'common': float('nan')},
            'dirs': {'old_only': float('nan'), 'new_only': float('nan'), 'common': float('nan')}
        }
        self.stats_deep = None

    @staticmethod
    def get_files_and_dirs(path):
        files = []
        dirs = []
        for name, value in path.items():
            if value is None:
                files.append(name)
            else:
                dirs.append(name)
        return set(files), set(dirs)

    def has_exclusive_new_content(self):
        assert self.stats_deep is not None, 'stats_deep is None'
        return self.old_path is None or self.stats_deep['files']['new_only'] > 0 or self.stats_deep['dirs']['new_only'] > 0

    def has_exclusive_old_content(self):
        assert self.stats_deep is not None, 'stats_deep is None'
        return self.new_path is None or self.stats_deep['files']['old_only'] > 0 or self.stats_deep['dirs']['old_only'] > 0

    def is_same(self):
        if self.new_path is None or self.old_path is None:
            return False
        assert self.stats_deep is not None, 'stats_deep is None'
        # todo make simpler with AND
        return (self.stats_deep['files']['old_only'], self.stats_deep['files']['new_only'], self.stats_deep['dirs']['old_only'], self.stats_deep['dirs']['new_only']) == (0, 0, 0, 0)

    def _get_stats(self):
        self.stats['files']['old_only'] = len(self.old_files - self.new_files)
        self.stats['files']['new_only'] = len(self.new_files - self.old_files)
        self.stats['files']['common'] = len(self.old_files & self.new_files)
        self.stats['dirs']['old_only'] = len(self.old_dirs - self.new_dirs)
        self.stats['dirs']['new_only'] = len(self.new_dirs - self.old_dirs)
        self.stats['dirs']['common'] = len(self.old_dirs & self.new_dirs)
        if self.old_path is None:
            self.stats['files']['old_only'] = float('nan')
            self.stats['dirs']['old_only'] = float('nan')
            self.stats['files']['common'] = float('nan')
            self.stats['dirs']['common'] = float('nan')
        if self.new_path is None:
            self.stats['files']['new_only'] = float('nan')
            self.stats['dirs']['new_only'] = float('nan')
            self.stats['files']['common'] = float('nan')
            self.stats['dirs']['common'] = float('nan')

    def _get_stats_deep(self):
        self.stats_deep = {
            'files': {'old_only': 0, 'new_only': 0, 'common': 0},
            'dirs': {'old_only': 0, 'new_only': 0, 'common': 0}
        }
        # make sure children stats are up to date
        for child in self.children:
            child._get_stats_deep()
        # sum children stats
        if self.old_path is not None:
            self.stats_deep['files']['old_only'] = self.stats['files']['old_only'] + sum([child.stats_deep['files']['old_only'] for child in self.children])
            self.stats_deep['dirs']['old_only'] = self.stats['dirs']['old_only'] + sum([child.stats_deep['dirs']['old_only'] for child in self.children])
        if self.new_path is not None:
            self.stats_deep['files']['new_only'] = self.stats['files']['new_only'] + sum([child.stats_deep['files']['new_only'] for child in self.children])
            self.stats_deep['dirs']['new_only'] = self.stats['dirs']['new_only'] + sum([child.stats_deep['dirs']['new_only'] for child in self.children])
        if self.new_path is not None and self.old_path is not None:
            self.stats_deep['files']['common'] = self.stats['files']['common'] + sum([child.stats_deep['files']['common'] for child in self.children])
            self.stats_deep['dirs']['common'] = self.stats['dirs']['common'] + sum([child.stats_deep['dirs']['common'] for child in self.children])

    def __repr__(self):
        return self.full_name

    def get_print_line(self, indent=0):
        result = ' ' * indent
        if self.new_path is None:
            result += '(DEL)'
        if self.old_path is None:
            result += '(NEW)'
        if self.new_path is not None and self.old_path is not None:
            result += '(...)'
        result += ' ' + f'{self.name:<10}'
        # add deep stats
        if self.is_same():
            result += '  SAME'
        else:
            result += ' <:({} | {})'.format(self.stats_deep['files']['old_only'], self.stats_deep['dirs']['old_only'])
            result += ' >:({} | {})'.format(self.stats_deep['files']['new_only'], self.stats_deep['dirs']['new_only'])
        return result

def get_tree(old_path, new_path, root_name=''):
    root = Node(root_name, old_path=old_path, new_path=new_path)
    root._get_stats()
    _build_tree(root)
    root._get_stats_deep()
    return root

def _build_tree(node):
    combined = set()
    if node.old_path is not None:
        combined |= set(node.old_path.keys())
    if node.new_path is not None:
        combined |= set(node.new_path.keys())
    combined = sorted(list(combined))
    for name in combined:
        old_path = node.old_path[name] if (node.old_path is not None and name in node.old_path.keys()) else None
        new_path = node.new_path[name] if (node.new_path is not None and name in node.new_path.keys()) else None
        if old_path is None and new_path is None:
            continue

        child = Node(name, old_path=old_path, new_path=new_path, parent=node)
        child._get_stats()
        node.children.append(child)
        _build_tree(child)


if __name__=='__main__':
    import json
    res = get_directory_structure("M:/")
    with open("result.json", 'w') as json_file:
        json.dump(res, json_file, indent=2)
