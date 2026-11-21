#!/usr/bin/env bash
set -euo pipefail

# Reproducible free/open animation stack for Ubuntu 24.04 / Debian 13.
# Blender is the headless production renderer; Krita and Tahoma2D are
# companion frame-by-frame drawing / cleanup tools.
BLENDER_VERSION="4.5.16"
BLENDER_DIR="/opt/blender-\${BLENDER_VERSION}"
BLENDER_ARCHIVE="blender-\${BLENDER_VERSION}-linux-x64.tar.xz"
BLENDER_URL="https://mirror.blender.org/release/Blender4.5/\${BLENDER_ARCHIVE}"

TAHOMA_VERSION="1.6.3"
TAHOMA_PACKAGE="Tahoma2D-linux-clang.deb"
TAHOMA_URL="https://github.com/tahoma2d/tahoma2d/releases/download/v\${TAHOMA_VERSION}/\${TAHOMA_PACKAGE}"
TAHOMA_SHA256="b12ae63f4580af0b094950a1ff3b6288be5702a9fec0f233b3b271c34f393386"

if [[ "\${EUID}" -ne 0 ]]; then
  echo "Run this script with sudo." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl xz-utils ffmpeg krita \
  libgl1 libxi6 libxrender1 libxkbcommon0 libsm6 libxfixes3 \
  libxkbcommon-x11-0 libx11-6 libxext6 libxxf86vm1

if [[ ! -x "\${BLENDER_DIR}/blender" ]]; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "\${tmp}"' EXIT
  curl --fail --location --retry 3 "\${BLENDER_URL}" -o "\${tmp}/\${BLENDER_ARCHIVE}"
  tar -xJf "\${tmp}/\${BLENDER_ARCHIVE}" -C "\${tmp}"
  extracted="\${tmp}/blender-\${BLENDER_VERSION}-linux-x64"
  test -x "\${extracted}/blender"
  rm -rf "\${BLENDER_DIR}"
  mv "\${extracted}" "\${BLENDER_DIR}"
fi

if ! dpkg-query -W -f='\${Status}' tahoma2d 2>/dev/null | grep -q 'install ok installed'; then
  tmp="$(mktemp -d)"
  trap 'rm -rf "\${tmp}"' EXIT
  curl --fail --location --retry 3 "\${TAHOMA_URL}" -o "\${tmp}/\${TAHOMA_PACKAGE}"
  echo "\${TAHOMA_SHA256}  \${tmp}/\${TAHOMA_PACKAGE}" | sha256sum --check -
  apt-get install -y "\${tmp}/\${TAHOMA_PACKAGE}"
fi

ln -sfn "\${BLENDER_DIR}/blender" /usr/local/bin/blender
echo "Installed animation stack:"
blender --version | head -n 2
krita --version | head -n 1 || true
dpkg-query -W -f='Tahoma2D \${Version}\n' tahoma2d || true
ffmpeg -version | head -n 1
