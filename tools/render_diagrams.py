#!/usr/bin/env python3
"""
Mermaid Diagram Renderer

Extracts Mermaid diagrams from markdown files and renders them as PNG/SVG.
Can also display in terminal if supported.

Usage:
    python tools/render_diagrams.py [--format png|svg] [--output-dir DIR] [--diagram NAME]
    python tools/render_diagrams.py --list
    python tools/render_diagrams.py --all
"""

import re
import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


def extract_mermaid_blocks(markdown_file: str) -> List[Tuple[str, str]]:
    """
    Extract Mermaid code blocks from markdown file.
    
    Returns:
        List of (diagram_name, mermaid_code) tuples
    """
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Pattern to match ```mermaid blocks
    pattern = r'```mermaid\s*(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    diagrams = []
    for i, match in enumerate(matches):
        code = match.group(1).strip()
        
        # Find the position of this match
        start_pos = match.start()
        
        # Look backwards for the most recent heading
        before = content[:start_pos]
        
        # Find all headings before this position
        heading_pattern = r'^###?\s+(.+?)$'
        headings = list(re.finditer(heading_pattern, before, re.MULTILINE))
        
        if headings:
            # Use the last (most recent) heading
            heading_text = headings[-1].group(1).strip()
            # Clean up heading text for filename
            name = heading_text.lower()
            name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars
            name = re.sub(r'[-\s]+', '_', name)   # Replace spaces/dashes with underscore
            name = name.strip('_')
        else:
            # Fallback: use section number or generic name
            name = f"diagram_{i+1}"
        
        diagrams.append((name, code))
    
    return diagrams


def render_mermaid(diagram_code: str, output_file: str, format: str = 'png') -> bool:
    """
    Render Mermaid diagram to file using mmdc.
    
    Args:
        diagram_code: Mermaid diagram code
        output_file: Output file path
        format: Output format (png, svg, pdf)
    
    Returns:
        True if successful, False otherwise
    """
    # Create temporary .mmd file
    temp_file = output_file.replace(f'.{format}', '.mmd')
    
    try:
        with open(temp_file, 'w') as f:
            f.write(diagram_code)
        
        # Run mmdc
        # Format is determined by output file extension, but we can specify explicitly
        cmd = ['mmdc', '-i', temp_file, '-o', output_file, '-e', format]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error rendering {output_file}: {result.stderr}", file=sys.stderr)
            return False
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False


def check_mmdc_available() -> bool:
    """Check if mmdc is available."""
    try:
        result = subprocess.run(['mmdc', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def display_in_terminal(image_path: str) -> bool:
    """
    Try to display image in terminal.
    Supports: imgcat (iTerm2), chafa, or opens default viewer.
    """
    # Try imgcat (iTerm2)
    if subprocess.run(['which', 'imgcat'], capture_output=True).returncode == 0:
        subprocess.run(['imgcat', image_path])
        return True
    
    # Try chafa
    if subprocess.run(['which', 'chafa'], capture_output=True).returncode == 0:
        subprocess.run(['chafa', image_path])
        return True
    
    # Fallback: open in default viewer
    if sys.platform == 'darwin':
        subprocess.run(['open', image_path])
    elif sys.platform.startswith('linux'):
        subprocess.run(['xdg-open', image_path])
    elif sys.platform == 'win32':
        subprocess.run(['start', image_path], shell=True)
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Render Mermaid diagrams from markdown files'
    )
    parser.add_argument(
        '--file',
        default='architecture/block_diagrams.md',
        help='Markdown file containing Mermaid diagrams (default: architecture/block_diagrams.md)'
    )
    parser.add_argument(
        '--format',
        choices=['png', 'svg', 'pdf'],
        default='png',
        help='Output format (default: png)'
    )
    parser.add_argument(
        '--output-dir',
        default='outputs/diagrams',
        help='Output directory for rendered diagrams (default: outputs/diagrams)'
    )
    parser.add_argument(
        '--diagram',
        help='Render specific diagram by name (use --list to see available)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available diagrams'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Render all diagrams'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Display rendered images in terminal/viewer'
    )
    
    args = parser.parse_args()
    
    # Check if mmdc is available
    if not check_mmdc_available():
        print("Error: mmdc (Mermaid CLI) not found.", file=sys.stderr)
        print("Install with: npm install -g @mermaid-js/mermaid-cli", file=sys.stderr)
        sys.exit(1)
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    # Extract diagrams
    diagrams = extract_mermaid_blocks(args.file)
    
    if not diagrams:
        print(f"No Mermaid diagrams found in {args.file}")
        sys.exit(1)
    
    # List diagrams
    if args.list:
        print(f"Found {len(diagrams)} diagram(s) in {args.file}:\n")
        for i, (name, code) in enumerate(diagrams, 1):
            lines = len(code.split('\n'))
            print(f"  {i}. {name} ({lines} lines)")
        sys.exit(0)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Filter diagrams if specific one requested
    if args.diagram:
        diagrams = [(name, code) for name, code in diagrams 
                   if args.diagram.lower() in name.lower()]
        if not diagrams:
            print(f"Error: Diagram '{args.diagram}' not found", file=sys.stderr)
            sys.exit(1)
    
    # Render diagrams
    rendered = []
    for name, code in diagrams:
        output_file = os.path.join(args.output_dir, f"{name}.{args.format}")
        print(f"Rendering {name}...", end=' ')
        
        if render_mermaid(code, output_file, args.format):
            print(f"✓ Saved to {output_file}")
            rendered.append(output_file)
        else:
            print("✗ Failed")
    
    # Display if requested
    if args.show and rendered:
        print("\nDisplaying rendered diagrams...")
        for img in rendered:
            display_in_terminal(img)
    
    print(f"\n✓ Rendered {len(rendered)} diagram(s) to {args.output_dir}/")


if __name__ == "__main__":
    main()

