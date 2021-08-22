def collect_package_data(pkg_info: dict, pkg_name: str, metadata: bool = False):
    import PyInstaller.utils.hooks

    binaries = pkg_info.setdefault('binaries', [])
    datas = pkg_info.setdefault('datas', [])
    hiddenimports = pkg_info.setdefault('hiddenimports', [])

    # collect data
    if metadata:
        datas += PyInstaller.utils.hooks.copy_metadata(pkg_name)
    datas += PyInstaller.utils.hooks.collect_data_files(
        pkg_name,
        include_py_files=False,
        excludes=['**/*.pyi', '**/*.typed', '**/tests/**', '**/test/**']
    )
    # collect binaries
    binaries += PyInstaller.utils.hooks.collect_data_files(
        pkg_name,
        include_py_files=True,
        includes=['**/*.dll', '**/*.dylib', '**/*.so', ],
    )
    # collect package modules
    hiddenimports += PyInstaller.utils.hooks.collect_submodules(pkg_name)

    return pkg_info


def collect_sources(*names):
    import importlib
    import inspect
    import os.path

    result = []
    for name in names:
        obj = importlib.import_module(name)
        file = os.path.abspath(inspect.getfile(obj))
        dst_dir = '/'.join(name.split('.')[:-1])
        result.append((file, dst_dir))
    return result


def _cleanup_data(data_list):
    import os.path

    added_paths = set()
    filtered_data_list = []
    for name, path, mark in data_list:
        path_abs = os.path.abspath(path)
        if path_abs in added_paths:
            continue
        filtered_data_list.append((name, path, mark))
        added_paths.add(path)
    data_list[:] = filtered_data_list


def deduplicate_data(analysis):
    _cleanup_data(analysis.datas)
    _cleanup_data(analysis.binaries)
    return analysis
