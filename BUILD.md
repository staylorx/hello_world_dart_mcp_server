# Building Hello World MCP Server

This document explains how to build the Hello World MCP Server for multiple platforms and architectures.

## Supported Platforms and Architectures

| Platform | Architecture | Output File |
|----------|-------------|-------------|
| Windows | AMD64 (x64) | `hello_world_mcp_server-windows-amd64.exe` |
| Windows | ARM64 | `hello_world_mcp_server-windows-arm64.exe` |
| Linux | AMD64 (x64) | `hello_world_mcp_server-linux-amd64` |
| Linux | ARM64 | `hello_world_mcp_server-linux-arm64` |
| macOS | AMD64 (Intel) | `hello_world_mcp_server-macos-amd64` |
| macOS | ARM64 (Apple Silicon) | `hello_world_mcp_server-macos-arm64` |

## Manual Building

### Prerequisites

- [Dart SDK](https://dart.dev/get-dart) 3.0.0 or later
- Git

### Local Build Commands

```bash
# Install dependencies
dart pub get

# Build for current platform
dart compile exe bin/hello_world_mcp_server.dart -o hello_world_mcp_server

# Build with specific output name
dart compile exe bin/hello_world_mcp_server.dart -o dist/hello_world_mcp_server
```

### Cross-Platform Building

While Dart has limited cross-compilation support, you can try:

```bash
# Attempt cross-compilation (may not work for all combinations)
dart compile exe bin/hello_world_mcp_server.dart -o hello_world_mcp_server --target-os=windows
dart compile exe bin/hello_world_mcp_server.dart -o hello_world_mcp_server --target-os=linux
dart compile exe bin/hello_world_mcp_server.dart -o hello_world_mcp_server --target-os=macos
```

**Note:** For reliable cross-platform builds, build on each target platform natively.

## Using Released Binaries

### Download

1. Go to the [Releases](../../releases) page
2. Download the appropriate binary for your platform:
   - **Windows**: `hello_world_mcp_server-windows-amd64.exe` or `hello_world_mcp_server-windows-arm64.exe`
   - **Linux**: `hello_world_mcp_server-linux-amd64` or `hello_world_mcp_server-linux-arm64`
   - **macOS**: `hello_world_mcp_server-macos-amd64` or `hello_world_mcp_server-macos-arm64`

### Verification

Verify the integrity of downloaded binaries using the provided checksums:

```bash
# Download checksums.txt from the release
# Verify a specific binary
sha256sum -c checksums.txt --ignore-missing
```

### Installation

#### Windows
```cmd
# No installation required, run directly
hello_world_mcp_server-windows-amd64.exe
```

#### Linux/macOS
```bash
# Make executable
chmod +x hello_world_mcp_server-linux-amd64

# Run
./hello_world_mcp_server-linux-amd64
```

### Usage

The MCP server communicates via stdin/stdout using JSON-RPC protocol:

```bash
# Test the server
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | ./hello_world_mcp_server-linux-amd64
```

## Development Workflow

### Making Changes

1. Make your code changes
2. Test locally: `dart run bin/hello_world_mcp_server.dart`
3. Build and test on target platforms
4. Commit and push your changes

### Creating a Release

1. Update version in [`pubspec.yaml`](pubspec.yaml) and [`bin/hello_world_mcp_server.dart`](bin/hello_world_mcp_server.dart)
2. Commit the version changes
3. Create and push a git tag:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```
4. Build binaries for all target platforms
5. Create a release and attach the built binaries

## Troubleshooting

### Build Failures

- Check build output for specific error messages
- Ensure all dependencies are properly declared in [`pubspec.yaml`](pubspec.yaml)
- Verify Dart SDK compatibility (minimum version 3.0.0)

### Architecture Issues

- ARM64 builds may fail on some platforms - this is a known limitation
- Cross-compilation support varies by platform
- Use native compilation when possible for best results

### Testing Issues

- The test step may timeout - this is expected for MCP servers
- Manual testing can be done by piping JSON-RPC messages to the executable
- Use MCP client tools for comprehensive testing

## Contributing

When contributing:

1. Ensure your changes build successfully on target platforms
2. Test on multiple platforms when possible
3. Update this documentation if you modify the build process
4. Follow semantic versioning for releases