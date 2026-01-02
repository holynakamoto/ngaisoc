# Performance and Power Modeling

This directory contains simulation models and benchmarks for evaluating the NexGen-AI SoC architecture.

## Directory Structure

- **python/:** Python-based high-level models for performance and power estimation
- **systemc/:** SystemC cycle-accurate models for detailed simulation
- **benchmarks/:** AI workload benchmarks (BERT, ResNet, transformer models)

## Modeling Objectives

1. **Performance Evaluation:** Cycle-accurate simulation of AI workloads
2. **Power Analysis:** Power estimation using McPAT or custom models
3. **Trade-off Analysis:** PPA (Power/Performance/Area) optimization
4. **Scalability Studies:** Multi-chiplet and multi-node system simulation

## Key Metrics

- MLPerf benchmark results
- Power consumption profiles
- Memory bandwidth utilization
- Scaling efficiency (single to multi-node)

## Tools and Frameworks

- Python: NumPy, Pandas, Matplotlib for analysis
- SystemC: Cycle-accurate modeling
- McPAT: Power estimation
- Custom scripts: PPA optimization

