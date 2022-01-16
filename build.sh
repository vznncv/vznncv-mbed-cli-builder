#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

#
# Utility functions
#

function log() {
    echo "$*" >&2
}

function log_info() {
    log "INFO: $*"
}

function log_error() {
    log "ERROR: $*"
}

function get_latest_package_version() {
    export PKG_NAME="$1"
    python3 <<EOS
import urllib.request
import json
import os

PYOCD_PKG_URL = f'https://pypi.org/pypi/{os.environ["PKG_NAME"]}/json'
response = urllib.request.urlopen(PYOCD_PKG_URL)
assert response.code == 200
data = json.load(response)
latest_version = data['info']['version']
print(latest_version)
EOS
}

function resolve_tool_version() {
    local tool_pkg_name="$1"
    local tool_pkg_version="$2"

    if [[ -z "$tool_pkg_version" ]]; then
        log_info "resolve ${tool_pkg_name} version"
        tool_pkg_version=$(get_latest_package_version "${tool_pkg_name}")
    fi
    log_info "set ${tool_pkg_name} version to $tool_pkg_version"
    echo "$tool_pkg_version"
}

#
# CLI
#

#
# parse CLI
#
function show_help() {
    log "Build mbed cli tools as standalone executable"
    log ""
    log "Usage ./$(basename "$0") {mbed-cli,mbed-cli-git-only,mbed-tools}[=<version>]"
    log ""
}

TARGET_TOOLS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
    -h | --help)
        show_help
        exit 0
        ;;
    *)
        TARGET_TOOLS+=("$1")
        shift
        ;;
    esac
done

if [[ "${#TARGET_TOOLS[@]}" -eq 0 ]]; then
    log_error "no targets are specified"
    log ""
    show_help
    exit 1
elif [[ "${#TARGET_TOOLS[@]}" -gt 1 ]]; then
    log_error "multiple are specified: ${TARGET_TOOLS[*]}"
    log ""
    show_help
    exit 1
fi
TARGET_NAME=$(sed -E 's/^([^=]+)=*(.*)$/\1/' <<<"${TARGET_TOOLS[0]}")
TARGET_VERSION=$(sed -E 's/^([^=]+)=*(.*)$/\2/' <<<"${TARGET_TOOLS[0]}")
TARGET_TOX="pyinstaller"

if [[ "$TARGET_NAME" == "mbed-cli" ]]; then
    TARGET_BUILD_DIR="$SCRIPT_DIR/mbed_cli_1"
    TARGET_VERSION_VAR_NAME="MBED_CLI_VERSION"
elif [[ "$TARGET_NAME" == "mbed-cli-git-only" ]]; then
    TARGET_BUILD_DIR="$SCRIPT_DIR/mbed_cli_1"
    TARGET_VERSION_VAR_NAME="MBED_CLI_VERSION"
    TARGET_NAME="mbed-cli"
    TARGET_TOX="pyinstaller-git-only"
elif [[ "$TARGET_NAME" == "mbed-tools" ]]; then
    TARGET_BUILD_DIR="$SCRIPT_DIR/mbed_cli_2"
    TARGET_VERSION_VAR_NAME="MBED_TOOLS_VERSION"
else
    log_error "unknown tool name: $TARGET_NAME"
    exit 1
fi

log_info "build $TARGET_NAME"
TARGET_VERSION=$(resolve_tool_version "$TARGET_NAME" "$TARGET_VERSION")
declare "$TARGET_VERSION_VAR_NAME=$TARGET_VERSION"
# shellcheck disable=SC2163
export "$TARGET_VERSION_VAR_NAME"
(
    cd "$TARGET_BUILD_DIR"
    tox -e "$TARGET_TOX"
)

# copy result to global dist directory
ARTIFACTS_FOLDER="$SCRIPT_DIR/dist"
if [[ ! -e "$ARTIFACTS_FOLDER" ]]; then
    mkdir "$ARTIFACTS_FOLDER"
fi
ARTIFACTS_TOTAL=0
while read -r line; do
    artifact_name=$(basename "$line")
    log_info "copy $artifact_name into \"$ARTIFACTS_FOLDER\" folder"
    cp "$line" "$ARTIFACTS_FOLDER/"
    ARTIFACTS_TOTAL=$((ARTIFACTS_TOTAL + 1))
done <<<"$(find "$TARGET_BUILD_DIR/dist" -maxdepth 1 -type f)"
if [[ "$ARTIFACTS_TOTAL" -lt 1 ]]; then
    log_error "no result artifacts are found!"
    exit 1
fi

log_info "complete"
