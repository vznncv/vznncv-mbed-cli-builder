def collect_runtime_hooks():
    import os.path
    runtime_hooks = os.path.abspath('runtime_hooks')
    result = []
    if not os.path.exists(runtime_hooks):
        return result
    for dir_entry in os.scandir(runtime_hooks):
        if dir_entry.is_dir() or not dir_entry.name.endswith('.py'):
            continue
        result.append(dir_entry.path)
    return result


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
        # excludes=['*.pyi', '**/tests/**', '**/test/*']
    )
    # collect package modules
    hiddenimports += PyInstaller.utils.hooks.collect_submodules(pkg_name)

    return pkg_info


def read_required_packages_from_requirements():
    import os
    import re
    import os.path
    import importlib.metadata

    requirements_path = os.path.join(os.getcwd(), 'requirements.txt')
    result = []
    with open(requirements_path, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'^(?P<lib_name>[\w_-]+)', line)
            if m is None:
                raise ValueError(f"Invalid package: {line}")

            try:
                distribution = importlib.metadata.distribution(m.group('lib_name'))
            except importlib.metadata.PackageNotFoundError as e:
                if 'platform_system' in line:
                    continue
                else:
                    raise
            top_level_files = set()
            for file_info in distribution.files:
                top_level_files.add(file_info.parts[0])

            pkg_top_level = []
            for pkg_name in distribution.read_text('top_level.txt').splitlines():
                if pkg_name.startswith('test'):
                    continue
                if pkg_name not in top_level_files:
                    continue

                pkg_top_level.append(pkg_name)
            result.extend(pkg_top_level)
    return result


def collect_package_data_from_requirements():
    top_level_packages = read_required_packages_from_requirements()
    pkg_info = {}
    for top_level_package in top_level_packages:
        collect_package_data(pkg_info, top_level_package)
    return pkg_info


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


if __name__ == '__main__':
    # local testing
    import json

    print(json.dumps(collect_package_data_from_requirements(), indent=4))
    from PyInstaller.building.build_main import Analysis

    pkg_info = collect_package_data_from_requirements()
    a = Analysis(['mbed_cli.py'],
                 pathex=[],
                 binaries=pkg_info['binaries'],
                 datas=pkg_info['datas'],
                 hiddenimports=pkg_info['hiddenimports'],
                 hookspath=[],
                 hooksconfig={},
                 runtime_hooks=collect_runtime_hooks(),
                 excludes=[],
                 win_no_prefer_redirects=False,
                 win_private_assemblies=False,
                 cipher=None,
                 noarchive=False)
