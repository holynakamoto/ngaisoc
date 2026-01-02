# Quick Start Guide: Performance Modeling

This guide helps you quickly get started with the NexGen-AI SoC performance modeling tools.

## Setup

```bash
# Navigate to project root
cd /path/to/ngaisoc

# Create virtual environment (if not already created)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Models

### 1. Baseline Performance Analysis

```bash
python modeling/python/performance_model.py
```

**What it does:**
- Validates baseline architecture against PRD targets
- Generates roofline plots
- Analyzes chiplet scaling
- Reports power consumption

**Output:**
- Console report with metrics
- `outputs/roofline_fp16.png`
- `outputs/chiplet_scaling.png`

### 2. Architecture Exploration

```bash
python modeling/python/arch_exploration.py
```

**What it does:**
- Compares 5 different architecture variants
- Identifies best configuration meeting targets
- Generates comparison plots

**Output:**
- Comparison table
- `outputs/architecture_comparison.png`
- Recommendations

### 3. Sensitivity Analysis

```bash
python modeling/python/sensitivity_analysis.py
```

**What it does:**
- Analyzes impact of each parameter on performance
- Identifies which parameters matter most
- Shows trade-offs between parameters

**Output:**
- Sensitivity metrics
- `outputs/sensitivity_analysis.png`
- Key insights

## Understanding the Results

### Critical Finding
The baseline architecture achieves **0.041 TFLOPS/mm²**, which is **48x below** the 2.0 TFLOPS/mm² target.

### What This Means
- The 2.0 TFLOPS/mm² target is extremely aggressive (4-5x higher than H100)
- Even "aggressive" optimizations achieve only 0.819 TFLOPS/mm²
- Recommendation: Revise target to 0.5-1.0 TFLOPS/mm²

### Next Steps
1. Review `documentation/trade_off_analyses/performance_analysis.md`
2. Run architecture exploration to see all options
3. Use sensitivity analysis to identify optimization priorities
4. Update PRD with realistic targets

## Customizing Configurations

### Modify Baseline Configuration

Edit `performance_model.py` in the `main()` function:

```python
soc = SoCConfig(
    num_chiplets=4,
    hbm3e_stacks=8,
    chiplet_config=ChipletConfig(
        num_sms=32,        # Increase from 16
        area_mm2=350,      # Reduce from 400
        sm_config=SMConfig(
            clock_mhz=2300,  # Increase from 2000
            tensor_cores=6,  # Increase from 4
        )
    )
)
```

### Create New Variant

Add to `arch_exploration.py`:

```python
def create_my_variant() -> ArchitectureVariant:
    sm = SMConfig(...)
    chiplet = ChipletConfig(...)
    soc = SoCConfig(...)
    return ArchitectureVariant(
        name="My Variant",
        description="...",
        sm_config=sm,
        chiplet_config=chiplet,
        soc_config=soc
    )
```

## Troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Plot Generation Fails
- Check that `outputs/` directory exists
- Ensure matplotlib backend is available

### Results Don't Make Sense
- Check parameter units (MHz vs GHz, mm² vs cm²)
- Verify tensor core ops/cycle assumptions
- Review power model parameters

## Further Reading

- `README.md` - Detailed documentation
- `documentation/trade_off_analyses/performance_analysis.md` - Full analysis
- `PRD.md` - Product requirements

