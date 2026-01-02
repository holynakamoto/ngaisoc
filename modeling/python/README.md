# Python Performance Models

This directory contains Python-based high-level models for performance and power estimation of the NexGen-AI SoC.

## Files

- **performance_model.py**: Main performance and power modeling script with roofline analysis, scaling studies, and power estimation
- **arch_exploration.py**: Architecture exploration tool comparing multiple configuration variants
- **sensitivity_analysis.py**: Sensitivity analysis identifying which parameters have the most impact

## Usage

### Basic Usage

```bash
# Install dependencies
pip install -r ../../requirements.txt

# Run the baseline performance model
python performance_model.py

# Compare different architecture variants
python arch_exploration.py

# Analyze parameter sensitivity
python sensitivity_analysis.py
```

### Using as a Library

```python
from performance_model import (
    SoCConfig, ChipletConfig, SMConfig,
    PerformanceModel, PowerModel, ScalingModel,
    Precision
)

# Create configuration
soc = SoCConfig(
    num_chiplets=4,
    hbm3e_stacks=8,
    chiplet_config=ChipletConfig(num_sms=16)
)

# Analyze performance
perf_model = PerformanceModel(soc)
peak_tflops = perf_model.peak_compute(Precision.FP16)
print(f"Peak FP16: {peak_tflops:.1f} TFLOPS")

# Analyze power
power_model = PowerModel(soc)
total_power = power_model.total_power(utilization=1.0)
print(f"Peak Power: {total_power:.1f} W")

# Generate roofline plot
perf_model.plot_roofline(Precision.FP16, save_path='roofline.png')
```

## Model Components

### Configuration Classes
- **SMConfig**: Streaming Multiprocessor configuration
- **ChipletConfig**: Single chiplet configuration
- **SoCConfig**: Full SoC configuration

### Analysis Classes
- **PerformanceModel**: Roofline analysis, compute density, memory bandwidth
- **PowerModel**: Power estimation, thermal modeling, efficiency calculations
- **ScalingModel**: Chiplet scaling efficiency analysis

## Outputs

### performance_model.py
- Console output with performance metrics and validation
- Roofline plots (saved to `../../outputs/roofline_fp16.png`)
- Scaling analysis plots (saved to `../../outputs/chiplet_scaling.png`)

### arch_exploration.py
- Comparison table of architecture variants
- Multi-panel comparison plots (density, power, efficiency, area vs performance)
- Detailed analysis of each variant
- Recommendations for best configurations
- Output: `../../outputs/architecture_comparison.png`

### sensitivity_analysis.py
- Sensitivity analysis for key parameters:
  - Number of SMs per chiplet
  - Chiplet area
  - Clock frequency
  - Tensor cores per SM
  - FP16 operations per cycle
- Normalized sensitivity metrics
- Output: `../../outputs/sensitivity_analysis.png`

## Extending the Model

To add new features:
1. Extend configuration classes for new parameters
2. Add methods to analysis classes for new metrics
3. Update the main() function to include new analyses

## Key Findings

⚠️ **Critical Finding:** The baseline architecture achieves only **0.041 TFLOPS/mm²**, which is **48x below** the 2.0 TFLOPS/mm² target.

### Baseline Results
- **Compute Density:** 0.041 TFLOPS/mm² (target: 2.0)
- **Power (4 chiplets):** 267W ✅ (within 500W target)
- **Power (8 chiplets):** 504W ❌ (exceeds 500W target)
- **All workloads are memory-bound**

### Architecture Exploration Results
The `arch_exploration.py` tool compares 5 variants:
1. **Baseline:** 0.041 TFLOPS/mm², 267W
2. **Realistic Optimized:** 0.242 TFLOPS/mm², 363W
3. **High SM Density:** 0.176 TFLOPS/mm², 412W
4. **Aggressive Optimized:** 0.819 TFLOPS/mm², 460W ⭐ (best)
5. **Power Optimized:** 0.058 TFLOPS/mm², 315W

**Recommendation:** Even the "Aggressive Optimized" variant achieves only 0.819 TFLOPS/mm². Consider revising the PRD target to 0.5-1.0 TFLOPS/mm² (competitive with H100).

### Sensitivity Analysis Insights
- **Highest impact parameters:**
  - Number of SMs per chiplet (direct scaling)
  - Chiplet area (inverse relationship)
  - FP16 ops per cycle (compute capability)
- **Power drivers:**
  - Clock frequency (quadratic relationship)
  - Number of SMs (linear relationship)

## Validation

The model validates against PRD targets:
- Compute density: 2 TFLOPS/mm² (FP16) - **Not achievable with baseline**
- Power budget: <500W per SoC - **Met for 4-6 chiplets**
- Scaling: Linear scaling up to 8 chiplets - **Confirmed**

See `../../documentation/trade_off_analyses/performance_analysis.md` for detailed findings and recommendations.

