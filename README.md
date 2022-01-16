# vznncv-pyocd-builder

Helper project to build [Mbed CLI 1](https://github.com/ARMmbed/mbed-cli)
and [Mbed CLI 2](https://github.com/ARMmbed/mbed-tools) as standalone executable files.

## Usage

1. Install requirements:

    - python 3.8 or higher
    - tox

2. Run `./build.sh mbed-cli` to build mbed-cli 1 tool. Alternatively, you can run
   `./build.sh mbed-cli-git-only` to build `mbed-cli` version that support only `git`. It eliminates problems
   of `mbed-cli` usage on a host that doesn't have Mercurial (`hg` command).

3. Run `./build.sh mbed-tools` to build mbed-cli 2 tool.

4. After build an executable files will be available in a `dist` folder.

## TODO:

- add CI/CD for automatic builds and releases
- add simple tests to check result file
