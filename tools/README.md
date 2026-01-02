# Tools and Scripts

This directory contains automation tools and helper scripts for the NexGen-AI SoC project.

## Diagram Rendering

### render_diagrams.py

Extracts Mermaid diagrams from markdown files and renders them as PNG, SVG, or PDF images.

#### Installation

The script requires the Mermaid CLI tool:

```bash
npm install -g @mermaid-js/mermaid-cli
```

#### Usage

**List all available diagrams:**
```bash
python tools/render_diagrams.py --list
```

**Render all diagrams:**
```bash
python tools/render_diagrams.py --all
```

**Render a specific diagram:**
```bash
python tools/render_diagrams.py --diagram chiplet
```

**Render with different format:**
```bash
python tools/render_diagrams.py --all --format svg
```

**Render and display in terminal/viewer:**
```bash
python tools/render_diagrams.py --all --show
```

**Custom file and output directory:**
```bash
python tools/render_diagrams.py --file architecture/block_diagrams.md --output-dir outputs/diagrams
```

#### Options

- `--file`: Markdown file containing Mermaid diagrams (default: `architecture/block_diagrams.md`)
- `--format`: Output format - `png`, `svg`, or `pdf` (default: `png`)
- `--output-dir`: Output directory (default: `outputs/diagrams`)
- `--diagram`: Render specific diagram by name (partial match supported)
- `--list`: List all available diagrams
- `--all`: Render all diagrams
- `--show`: Display rendered images in terminal/viewer (if supported)

#### Terminal Display

The `--show` option will attempt to display images using:
1. `imgcat` (iTerm2 on macOS) - best terminal experience
2. `chafa` (general terminal image viewer)
3. Default system viewer (fallback)

#### Examples

```bash
# List diagrams
python tools/render_diagrams.py --list

# Render all as PNG
python tools/render_diagrams.py --all

# Render specific diagram as SVG
python tools/render_diagrams.py --diagram memory --format svg

# Render and view in terminal (iTerm2)
python tools/render_diagrams.py --all --show
```

#### Output

Rendered diagrams are saved to `outputs/diagrams/` by default with filenames based on their section headings:
- `4_chiplet_configuration_with_ucie_and_nvlink.png`
- `complete_soc_system_block_diagram.png`
- `detailed_memory_subsystem_architecture.png`
- etc.

## Terminal Viewing Options

### Option 1: Install imgcat (iTerm2 - Recommended)

For macOS users with iTerm2:

```bash
# Install imgcat
curl -s https://iterm2.com/utilities/imgcat > /usr/local/bin/imgcat
chmod +x /usr/local/bin/imgcat
```

Then use:
```bash
python tools/render_diagrams.py --all --show
```

### Option 2: Install chafa (Universal)

Works on most terminals:

```bash
# macOS
brew install chafa

# Linux
sudo apt-get install chafa  # Debian/Ubuntu
sudo yum install chafa      # RHEL/CentOS
```

### Option 3: View Generated Images

Simply render the diagrams and open them manually:

```bash
python tools/render_diagrams.py --all
open outputs/diagrams/  # macOS
xdg-open outputs/diagrams/  # Linux
```

## Integration with Workflow

### Pre-commit Hook

You can add a git hook to automatically render diagrams:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python tools/render_diagrams.py --all --format png
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/diagrams.yml
- name: Render Diagrams
  run: |
    npm install -g @mermaid-js/mermaid-cli
    python tools/render_diagrams.py --all --format png
```

## Troubleshooting

### mmdc not found

```bash
npm install -g @mermaid-js/mermaid-cli
```

### Permission errors

Make sure the output directory is writable:
```bash
mkdir -p outputs/diagrams
chmod 755 outputs/diagrams
```

### Diagram extraction issues

If diagrams aren't being found, check:
1. Mermaid code blocks use ` ```mermaid ` (not ` ``` mermaid `)
2. Section headings exist before each diagram
3. File path is correct
