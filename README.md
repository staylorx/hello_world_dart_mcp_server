# Hello World MCP Server

A simple Hello World MCP (Model Context Protocol) server written in Dart that demonstrates basic MCP server implementation with two example tools.

## Overview

This MCP server provides a minimal example of how to implement an MCP server in Dart. It includes two basic tools:

- **`say_hello`**: Greets a person with an optional custom message
- **`get_server_info`**: Returns information about the MCP server

## Features

- JSON-RPC 2.0 protocol implementation
- Stdio-based communication
- Cross-platform support (Windows, Linux, macOS)
- Native binary compilation
- Simple tool demonstration

## Requirements

- Dart SDK 3.0.0 or later
- Compatible MCP client

## Installation

### Option 1: Using Dart Runtime (Development)

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd hello-world-server
   ```

2. Install dependencies:
   ```bash
   dart pub get
   ```

3. Run the server:
   ```bash
   dart run bin/hello_world_mcp_server.dart
   ```

### Option 2: Using Pre-built Binaries (Production)

Download the appropriate binary for your platform from the [Releases](../../releases) page:

- **Windows**: `hello_world_mcp_server-windows-amd64.exe` or `hello_world_mcp_server-windows-arm64.exe`
- **Linux**: `hello_world_mcp_server-linux-amd64` or `hello_world_mcp_server-linux-arm64`
- **macOS**: `hello_world_mcp_server-macos-amd64` or `hello_world_mcp_server-macos-arm64`

#### Linux/macOS Setup:
```bash
# Make the binary executable
chmod +x hello_world_mcp_server-linux-amd64

# Run the server
./hello_world_mcp_server-linux-amd64
```

#### Windows Setup:
```cmd
# Run directly
hello_world_mcp_server-windows-amd64.exe
```

### Option 3: Build from Source

```bash
# Install dependencies
dart pub get

# Compile to native executable
dart compile exe bin/hello_world_mcp_server.dart -o hello_world_mcp_server

# Run the compiled binary
./hello_world_mcp_server  # Linux/macOS
hello_world_mcp_server.exe  # Windows
```

## Usage

### Running the MCP Server

The MCP server communicates via stdin/stdout using the JSON-RPC 2.0 protocol. It's designed to be used with MCP-compatible clients.

#### Using Native Dart Runner

```bash
dart run bin/hello_world_mcp_server.dart
```

#### Using Compiled Binary

```bash
# Linux/macOS
./hello_world_mcp_server-linux-amd64

# Windows
hello_world_mcp_server-windows-amd64.exe
```

### MCP Client Configuration

To use this server with an MCP client, configure it as a stdio-based server:

#### Example Configuration (MCP Client)

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "dart",
      "args": ["run", "/path/to/hello-world-server/bin/hello_world_mcp_server.dart"]
    }
  }
}
```

#### Using Binary in MCP Client

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "/path/to/hello_world_mcp_server-linux-amd64"
    }
  }
}
```

### Manual Testing

You can test the server manually by sending JSON-RPC messages:

```bash
# Initialize the server
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | dart run bin/hello_world_mcp_server.dart

# List available tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | dart run bin/hello_world_mcp_server.dart

# Call the say_hello tool
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"say_hello","arguments":{"name":"World","message":"Greetings"}}}' | dart run bin/hello_world_mcp_server.dart

# Get server information
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_server_info","arguments":{}}}' | dart run bin/hello_world_mcp_server.dart
```

## Available Tools

### `say_hello`

Greets a person with an optional custom message.

**Parameters:**
- `name` (required, string): The name of the person to greet
- `message` (optional, string): Custom message (defaults to "Hello")

**Example:**
```json
{
  "name": "say_hello",
  "arguments": {
    "name": "Alice",
    "message": "Good morning"
  }
}
```

**Response:**
```
Good morning, Alice! 👋
```

### `get_server_info`

Returns information about this MCP server.

**Parameters:** None

**Example:**
```json
{
  "name": "get_server_info",
  "arguments": {}
}
```

**Response:**
```
Hello World MCP Server Information:
- Name: hello-world-server
- Version: 1.0.0
- Language: Dart
- Protocol Version: 2024-11-05
- Available Tools: say_hello, get_server_info

This is a simple demonstration MCP server that shows how to implement basic tools using Dart.
```

## Development

### Project Structure

```
hello-world-server/
├── bin/
│   └── hello_world_mcp_server.dart  # Main server implementation
├── dagger/
│   └── build_script.py              # Dagger build script for multi-platform builds
├── artifacts/                       # Build output directory (created by Dagger)
├── BUILD.md                         # Detailed build instructions
├── LICENSE                          # MIT License
├── pubspec.yaml                     # Dart project configuration
├── pyproject.toml                   # Python project config for Dagger builds
├── README.md                        # This file
└── .gitignore                       # Git ignore rules
```

### Running in Development

```bash
# Install dependencies
dart pub get

# Run the server
dart run bin/hello_world_mcp_server.dart

# Run with debugging output
dart run bin/hello_world_mcp_server.dart 2>debug.log
```

### Building

#### Option 1: Using Dagger (Recommended)

This project uses [Dagger](https://dagger.io/) for reproducible, containerized builds across all platforms.

Note for Windows developers, Python is used for the dagger builds, but that piece is best done in 'nix.

**Prerequisites:**
- Python 3.11+
- Docker (for Dagger)

**Build all platforms:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Dagger build script
python build_script.py
```

This will build binaries for:
- Windows (AMD64, ARM64)
- Linux (AMD64, ARM64)
- macOS/Darwin (AMD64, ARM64)

All binaries will be saved to the `artifacts/` directory.

**Using pyproject.toml:**
```bash
# Install in development mode
pip install -e .

# Run the build command
build-binaries
```

#### Option 2: Manual Build

See [BUILD.md](BUILD.md) for comprehensive build instructions, including:
- Manual compilation
- Cross-platform building
- Release process

## Protocol Details

This server implements the MCP (Model Context Protocol) specification:

- **Protocol Version**: 2024-11-05
- **Transport**: stdio (stdin/stdout)
- **Message Format**: JSON-RPC 2.0
- **Capabilities**: Tools

### Supported Methods

- `initialize` - Initialize the MCP session
- `notifications/initialized` - Acknowledge initialization
- `tools/list` - List available tools
- `tools/call` - Execute a tool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Please ensure your changes:
- Follow Dart coding conventions
- Include appropriate tests
- Don't break existing functionality
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please use the GitHub repository's issue tracker.

## Related

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Dart Language](https://dart.dev/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)