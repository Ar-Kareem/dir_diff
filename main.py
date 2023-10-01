import os
from functools import reduce
from pathlib import Path
from datetime import datetime
import json
from collections import namedtuple


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
            'version': 'v1',
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

_wrap_entry = namedtuple( 'DirEntryWrapper', 'isLeafDir name size mtime' )
def _myscantree( rootdir, follow_links=False, reldir='' ):
    visited = set()
    rootdir = os.path.normpath(rootdir)
    try:
        current_scan_count = 0
        with os.scandir(rootdir) as it:
            for entry in it:
                current_scan_count += 1
                if entry.is_dir():
                    if not entry.is_symlink() or follow_links:
                        absdir = os.path.relpath(entry.path)
                        if absdir in visited: 
                            continue 
                        else: 
                            visited.add(absdir)
                        yield from _myscantree( entry.path, follow_links, os.path.join(reldir,entry.name) )
                else:
                    st = entry.stat()
                    yield _wrap_entry( 
                        False,
                        os.path.join(reldir,entry.name), 
                        # entry.is_symlink(),
                        st.st_size,
                        st.st_mtime,
                    )
        if current_scan_count == 0:  # fix bug where empty folders are not included
            yield _wrap_entry( 
                True,
                reldir, 
                # entry.is_symlink(),
                0,
                0,
            )
    except PermissionError:
        print('PermissionError', rootdir)
        pass
        # for path, dirs, files in os.walk(rootdir):
        #     for name in files:
        #         yield _wrap_entry( 
        #             os.path.join(reldir,name), 
        #             # entry.is_symlink(),
        #             os.stat(os.path.join(path,name)).st_size,
        #             os.stat(os.path.join(path,name)).st_mtime,
        #         )
        #     for name in dirs:
        #         yield from _myscantree( os.path.join(path,name), follow_links, os.path.join(reldir,name) )

class _NestedDict(dict):
    def __missing__(self, key):
            self[key] = _NestedDict()
            return self[key]

def get_directory_structure_v2(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    TOP_LEVEL_NAME = 'root'
    rootdir = Path(rootdir).resolve()
    res = _NestedDict()
    res["INFO"] = {
        'rootdir': str(rootdir),
        'timestamp': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        'time': datetime.timestamp(datetime.now()),
        'version': 'v2',
    }
    for item in _myscantree(rootdir):  # returns individual files or empty directories
        if item.isLeafDir:  # directory that is empty needs special treatment
            folders = item.name.split(os.sep)
            folders = [TOP_LEVEL_NAME] + [f for f in folders if f]
            parent = reduce(lambda d, k: d[k], folders[:-1], res)  # get the parent folder by recursive dict.get for all folders until leaf
            parent[folders[-1]] = {}
            continue
        mtime = datetime.fromtimestamp(item.mtime).strftime("%y/%m/%d %H:%M:%S")
        folders = item.name.split(os.sep)
        folders = [TOP_LEVEL_NAME] + [f for f in folders if f]
        parent = reduce(lambda d, k: d[k], folders[:-1], res)  # get the parent folder by recursive dict.get for all folders until leaf
        parent[folders[-1]] = json.dumps((item.size, mtime))
    return res

class Node:
    def __init__(self, name, old_path=None, new_path=None, parent=None, compare_settings={}):
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
        self.compare_settings = compare_settings
        self._get_stats()

    @staticmethod
    def get_files_and_dirs(path):
        files: list[str] = []
        dirs: list[str] = []
        for name, value in path.items():
            if value is None or isinstance(value, str):
                size, mtime = json.loads(value) if value is not None else ('N/A', 'N/A')
                files.append(name + ' | ' + str(size) + ' | ' + str(mtime))  # concat to string to simplify comparison
            else:
                dirs.append(name)
        return set(files), set(dirs)

    def get_del_new_common_file_splits(self):
        old_files = [x[::-1].split(' | ', 2)[::-1] for x in self.old_files]
        new_files = [x[::-1].split(' | ', 2)[::-1] for x in self.new_files]
        compare_size, compare_mtime = self.compare_settings.get('size', True), self.compare_settings.get('mtime', True)
        old_files_formatted = [x[0] + (x[1] if compare_size else '') + (x[2] if compare_mtime else '') for x in old_files]
        new_files_formatted = [x[0] + (x[1] if compare_size else '') + (x[2] if compare_mtime else '') for x in new_files]
        old_files_formatted_set = set(old_files_formatted)
        new_files_formatted_set = set(new_files_formatted)

        deleted_files = [real for real, formatted in zip(self.old_files, old_files_formatted) if formatted not in new_files_formatted_set]
        new_files = [real for real, formatted in zip(self.new_files, new_files_formatted) if formatted not in old_files_formatted_set]
        # for common we can either use old or new files, only makes a difference if compare_settings ignores size or mtime, we use new files
        common_files = [real for real, formatted in zip(self.new_files, new_files_formatted) if formatted in old_files_formatted_set]
        return deleted_files, new_files, common_files


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
        r = self.get_del_new_common_file_splits()
        self.stats['files']['old_only'] = len(r[0])
        self.stats['files']['new_only'] = len(r[1])
        self.stats['files']['common'] = len(r[2])
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

def get_tree(old_path, new_path, compare_settings, root_name=''):
    root = Node(root_name, old_path=old_path, new_path=new_path, compare_settings=compare_settings)
    _build_tree(root, compare_settings)
    root._get_stats_deep()
    return root

def _build_tree(node, compare_settings):
    combined = set()
    if node.old_path is not None:
        combined |= set(node.old_path.keys())
    if node.new_path is not None:
        combined |= set(node.new_path.keys())
    combined = sorted(list(combined))
    for name in combined:
        old_path = node.old_path[name] if (node.old_path is not None and name in node.old_path.keys()) else None
        new_path = node.new_path[name] if (node.new_path is not None and name in node.new_path.keys()) else None

        if isinstance(old_path, str):  # if it is a file
            old_path = None
        if isinstance(new_path, str):  # if it is a file
            new_path = None
        if old_path is None and new_path is None:
            continue

        child = Node(name, old_path=old_path, new_path=new_path, parent=node, compare_settings=compare_settings)
        node.children.append(child)
        _build_tree(child, compare_settings)


if __name__=='__main__':
    import json
    res = get_directory_structure_v2("M:/")
    with open("result.json", 'w') as json_file:
        json.dump(res, json_file, indent=2)
