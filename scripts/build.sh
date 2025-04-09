#!/bin/bash

# Exit on error
set -e
set -x

# Get the latest tag
# LATEST_TAG=$(curl -s https://api.github.com/repos/SagerNet/sing-box/releases/latest | jq -r .tag_name)
LATEST_TAG=$1
echo "Latest tag found: $LATEST_TAG"

# Clone the repository with the latest tag
git clone https://github.com/SagerNet/sing-box --depth 1 --branch "$LATEST_TAG"
cd sing-box

# Set variables (converted from Makefile)
TAGS="with_quic,with_wireguard,with_clash_api,with_gvisor"
export CGO_ENABLED=0
VERSION=$(go run ./cmd/internal/read_tag)

# Build parameters
PARAMS=(-v -trimpath -ldflags "-X 'github.com/sagernet/sing-box/constant.Version=$VERSION' -s -w -buildid=")
MAIN_PARAMS=("${PARAMS[@]}" -tags "$TAGS")
MAIN="./cmd/sing-box"

# Create output directory
mkdir -p ../src/sing_box_cli/bin

# Build for Linux (AMD64)
echo "Building sing-box version $VERSION for Linux AMD64..."
export GOOS=linux
export GOARCH=amd64
go build "${MAIN_PARAMS[@]}" -o sing-box "$MAIN"
cp sing-box ../src/sing_box_cli/bin/

# Build for Windows (AMD64)
echo "Building sing-box version $VERSION for Windows AMD64..."
export GOOS=windows
export GOARCH=amd64
go build "${MAIN_PARAMS[@]}" -o sing-box.exe "$MAIN"
cp sing-box.exe ../src/sing_box_cli/bin/


# Build the project
echo "Building sing-box version $VERSION..."
go build "${MAIN_PARAMS[@]}" "$MAIN"

# Return to original directory
cd ..

echo "Build completed successfully!"
echo "The binaries are located at: $(pwd)/src/sing_box_cli/bin/"

# Clean up
rm -rf sing-box/
