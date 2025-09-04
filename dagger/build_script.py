#!/usr/bin/env python3
"""
Dagger-based build script for Hello World MCP Server
Builds binaries for Windows, Linux, and macOS on both AMD64 and ARM64 architectures.

Usage:
    python build_script.py                    # Build for all platforms
    python build_script.py --os windows       # Build only for Windows
    python build_script.py --os linux         # Build only for Linux
    python build_script.py --os macos         # Build only for macOS
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Tuple

import click
import dagger
from dagger import Container, Directory

# Build configuration
PLATFORMS = [
    ("linux", "amd64", "x64"),
    ("linux", "arm64", "arm64"),
    ("windows", "amd64", "x64"),
    ("windows", "arm64", "arm64"),
    ("darwin", "amd64", "x64"),
    ("darwin", "arm64", "arm64"),
]

DART_VERSION = "latest"  # Use stable version for reproducible builds
PROJECT_NAME = "hello_world_mcp_server"


async def get_dart_container(
    client: dagger.Client, os_name: str, arch: str, dart_arch: str
) -> Container:
    """Create a container with Dart SDK installed for the specified platform."""

    if os_name == "linux":
        # Use Ubuntu base image
        container = client.container().from_("ubuntu:22.04")

        # Install dependencies
        container = container.with_exec(["apt-get", "update"]).with_exec(
            ["apt-get", "install", "-y", "curl", "unzip", "ca-certificates"]
        )

        # Download and install Dart SDK
        dart_url = f"https://storage.googleapis.com/dart-archive/channels/stable/release/{DART_VERSION}/sdk/dartsdk-linux-{dart_arch}-release.zip"

    elif os_name == "darwin":
        # Use a Linux container to cross-compile for macOS
        container = client.container().from_("ubuntu:22.04")

        container = container.with_exec(["apt-get", "update"]).with_exec(
            ["apt-get", "install", "-y", "curl", "unzip", "ca-certificates"]
        )

        dart_url = f"https://storage.googleapis.com/dart-archive/channels/stable/release/{DART_VERSION}/sdk/dartsdk-macos-{dart_arch}-release.zip"

    else:  # windows
        # Use a Linux container to cross-compile for Windows
        container = client.container().from_("ubuntu:22.04")

        container = container.with_exec(["apt-get", "update"]).with_exec(
            ["apt-get", "install", "-y", "curl", "unzip", "ca-certificates"]
        )

        dart_url = f"https://storage.googleapis.com/dart-archive/channels/stable/release/{DART_VERSION}/sdk/dartsdk-windows-{dart_arch}-release.zip"

    # Download and extract Dart SDK
    container = (
        container.with_exec(["curl", "-L", "-o", "/tmp/dart-sdk.zip", dart_url])
        .with_exec(["unzip", "/tmp/dart-sdk.zip", "-d", "/opt/"])
        .with_env_variable("PATH", "/opt/dart-sdk/bin:$PATH", expand=True)
    )

    return container


async def build_binary(
    client: dagger.Client,
    source_dir: Directory,
    os_name: str,
    arch: str,
    dart_arch: str,
) -> Container:
    """Build a binary for the specified platform."""

    print(f"Building for {os_name}-{arch}...")

    # Get Dart container for the platform
    container = await get_dart_container(client, os_name, arch, dart_arch)

    # Mount source code
    container = container.with_directory("/workspace", source_dir)
    container = container.with_workdir("/workspace")

    # Get dependencies
    container = container.with_exec(["dart", "pub", "get"])

    # Determine output filename
    if os_name == "windows":
        output_name = f"{PROJECT_NAME}.exe"
        final_name = f"{PROJECT_NAME}-{os_name}-{arch}.exe"
    else:
        output_name = PROJECT_NAME
        final_name = f"{PROJECT_NAME}-{os_name}-{arch}"

    # Build the executable
    container = container.with_exec(
        ["dart", "compile", "exe", f"bin/{PROJECT_NAME}.dart", "-o", output_name]
    )

    # Rename to include platform info
    container = container.with_exec(["mv", output_name, final_name])

    return container


async def build_for_platforms(os_filter: str = None):
    """Build binaries for the specified platforms."""

    # Filter platforms based on OS argument
    if os_filter:
        # Normalize macos to darwin for internal consistency
        target_os = "darwin" if os_filter == "macos" else os_filter
        platforms = [p for p in PLATFORMS if p[0] == target_os]

        if not platforms:
            click.echo(f"❌ No platforms found for OS: {os_filter}", err=True)
            sys.exit(1)

        click.echo(f"Starting Dagger-based build for {os_filter.upper()}...")
    else:
        platforms = PLATFORMS
        click.echo("Starting Dagger-based multi-platform build...")

    # Get source directory
    source_path = Path.cwd()

    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
        # Load source directory
        source_dir = client.host().directory(str(source_path))

        # Build for selected platforms
        build_tasks = []
        for os_name, arch, dart_arch in platforms:
            task = build_binary(client, source_dir, os_name, arch, dart_arch)
            build_tasks.append((task, os_name, arch))

        # Execute all builds concurrently
        results = []
        for task, os_name, arch in build_tasks:
            try:
                container = await task
                results.append((container, os_name, arch))
                click.echo(f"✅ Successfully built {os_name}-{arch}")
            except Exception as e:
                click.echo(f"❌ Failed to build {os_name}-{arch}: {e}", err=True)
                continue

        # Export binaries
        artifacts_dir = source_path / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        for container, os_name, arch in results:
            try:
                if os_name == "windows":
                    binary_name = f"{PROJECT_NAME}-{os_name}-{arch}.exe"
                else:
                    binary_name = f"{PROJECT_NAME}-{os_name}-{arch}"

                # Export the binary
                binary_file = container.file(f"/workspace/{binary_name}")
                await binary_file.export(str(artifacts_dir / binary_name))

                click.echo(f"📦 Exported {binary_name}")

            except Exception as e:
                click.echo(f"❌ Failed to export {os_name}-{arch}: {e}", err=True)

        if os_filter:
            click.echo(
                f"\n🎉 Build complete for {os_filter.upper()}! Artifacts saved to: {artifacts_dir}"
            )
        else:
            click.echo(f"\n🎉 Build complete! Artifacts saved to: {artifacts_dir}")

        # List all created artifacts
        if artifacts_dir.exists():
            click.echo("\nCreated artifacts:")
            for artifact in sorted(artifacts_dir.glob("*")):
                size = artifact.stat().st_size
                click.echo(f"  - {artifact.name} ({size:,} bytes)")


@click.command()
@click.option(
    "--os",
    "os_name",
    type=click.Choice(["windows", "linux", "macos", "darwin"], case_sensitive=False),
    help="Build for specific OS only (windows, linux, macos/darwin). If not specified, builds for all platforms.",
)
def main(os_name):
    """
    Build Hello World MCP Server for specified platforms.

    Examples:
    \b
      python build_script.py                    # Build for all platforms
      python build_script.py --os windows       # Build only for Windows
      python build_script.py --os linux         # Build only for Linux
      python build_script.py --os macos         # Build only for macOS
    """
    asyncio.run(build_for_platforms(os_name))


if __name__ == "__main__":
    main()
