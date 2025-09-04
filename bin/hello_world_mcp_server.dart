#!/usr/bin/env dart

import 'dart:convert';
import 'dart:io';

class MCPServer {
  static const String version = '1.0.0';
  static const String name = 'hello-world-server';

  void start() {
    stderr.writeln('Hello World MCP server running on stdio');
    
    // Listen for JSON-RPC messages on stdin
    stdin
        .transform(utf8.decoder)
        .transform(const LineSplitter())
        .listen(handleMessage);
  }

  void handleMessage(String line) {
    if (line.trim().isEmpty) return;

    try {
      final message = jsonDecode(line);
      final response = processMessage(message);
      
      if (response != null) {
        stdout.writeln(jsonEncode(response));
      }
    } catch (e) {
      stderr.writeln('Error processing message: $e');
    }
  }

  Map<String, dynamic>? processMessage(Map<String, dynamic> message) {
    final method = message['method'] as String?;
    final id = message['id'];

    switch (method) {
      case 'initialize':
        return {
          'jsonrpc': '2.0',
          'id': id,
          'result': {
            'protocolVersion': '2024-11-05',
            'capabilities': {
              'tools': {},
            },
            'serverInfo': {
              'name': name,
              'version': version,
            },
          },
        };

      case 'notifications/initialized':
        // No response needed for notifications
        return null;

      case 'tools/list':
        return {
          'jsonrpc': '2.0',
          'id': id,
          'result': {
            'tools': [
              {
                'name': 'say_hello',
                'description': 'Says hello to a person with an optional custom message',
                'inputSchema': {
                  'type': 'object',
                  'properties': {
                    'name': {
                      'type': 'string',
                      'description': 'The name of the person to greet',
                    },
                    'message': {
                      'type': 'string',
                      'description': 'Optional custom message (defaults to "Hello")',
                    },
                  },
                  'required': ['name'],
                },
              },
              {
                'name': 'get_server_info',
                'description': 'Returns information about this MCP server',
                'inputSchema': {
                  'type': 'object',
                  'properties': {},
                },
              },
            ],
          },
        };

      case 'tools/call':
        return handleToolCall(message, id);

      default:
        return {
          'jsonrpc': '2.0',
          'id': id,
          'error': {
            'code': -32601,
            'message': 'Method not found: $method',
          },
        };
    }
  }

  Map<String, dynamic> handleToolCall(Map<String, dynamic> message, dynamic id) {
    final params = message['params'] as Map<String, dynamic>?;
    final toolName = params?['name'] as String?;
    final arguments = params?['arguments'] as Map<String, dynamic>? ?? {};

    switch (toolName) {
      case 'say_hello':
        final name = arguments['name'] as String? ?? 'World';
        final customMessage = arguments['message'] as String? ?? 'Hello';
        final greeting = '$customMessage, $name! 👋';
        
        return {
          'jsonrpc': '2.0',
          'id': id,
          'result': {
            'content': [
              {
                'type': 'text',
                'text': greeting,
              },
            ],
          },
        };

      case 'get_server_info':
        return {
          'jsonrpc': '2.0',
          'id': id,
          'result': {
            'content': [
              {
                'type': 'text',
                'text': '''Hello World MCP Server Information:
- Name: $name
- Version: $version
- Language: Dart
- Protocol Version: 2024-11-05
- Available Tools: say_hello, get_server_info

This is a simple demonstration MCP server that shows how to implement basic tools using Dart.''',
              },
            ],
          },
        };

      default:
        return {
          'jsonrpc': '2.0',
          'id': id,
          'error': {
            'code': -32602,
            'message': 'Unknown tool: $toolName',
          },
        };
    }
  }
}

void main() {
  final server = MCPServer();
  server.start();
}