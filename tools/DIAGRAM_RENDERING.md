# Quick Guide: Rendering Mermaid Diagrams

## Quick Start

```bash
# List all available diagrams
python tools/render_diagrams.py --list

# Render all diagrams as PNG
python tools/render_diagrams.py --all

# Render specific diagram
python tools/render_diagrams.py --diagram chiplet

# Render as SVG
python tools/render_diagrams.py --all --format svg
```

## Prerequisites

Install Mermaid CLI:
```bash
npm install -g @mermaid-js/mermaid-cli
```

## Viewing in Terminal

### Option 1: iTerm2 (macOS) - Best Experience

```bash
# Install imgcat
curl -s https://iterm2.com/utilities/imgcat > /usr/local/bin/imgcat
chmod +x /usr/local/bin/imgcat

# Render and view
python tools/render_diagrams.py --all --show
```

### Option 2: chafa (Universal)

```bash
# Install
brew install chafa  # macOS
sudo apt-get install chafa  # Linux

# Use
python tools/render_diagrams.py --all --show
```

### Option 3: Open in Default Viewer

```bash
# Render first
python tools/render_diagrams.py --all

# Then open
open outputs/diagrams/  # macOS
xdg-open outputs/diagrams/  # Linux
```

## Available Diagrams

From `architecture/block_diagrams.md`:

1. `4_chiplet_configuration_with_ucie_and_nvlink` - Chiplet interconnect topology
2. `complete_soc_system_block_diagram` - System-level architecture
3. `detailed_memory_subsystem_architecture` - Memory hierarchy
4. `detailed_sm_block_diagram` - SM microarchitecture
5. `single_chiplet_floorplan_top_view` - Single chiplet floorplan
6. `package_level_floorplan_4_chiplet_configuration` - Package layout
7. `power_delivery_architecture` - Power distribution network

## Examples

```bash
# Render just the chiplet diagram
python tools/render_diagrams.py --diagram chiplet

# Render memory hierarchy as SVG
python tools/render_diagrams.py --diagram memory --format svg

# Render all and view in iTerm2
python tools/render_diagrams.py --all --show

# Custom output location
python tools/render_diagrams.py --all --output-dir docs/images
```

## Output Location

By default, rendered diagrams are saved to:
```
outputs/diagrams/
```

Files are named based on their section headings, e.g.:
- `4_chiplet_configuration_with_ucie_and_nvlink.png`
- `complete_soc_system_block_diagram.png`
- etc.

## Troubleshooting

**"mmdc not found"**
```bash
npm install -g @mermaid-js/mermaid-cli
```

**"No diagrams found"**
- Check that the markdown file has ` ```mermaid ` code blocks
- Verify the file path is correct

**Images not displaying in terminal**
- Install `imgcat` (iTerm2) or `chafa` (universal)
- Or use `--show` to open in default viewer

