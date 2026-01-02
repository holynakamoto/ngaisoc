#!/usr/bin/env python3
"""
Sensitivity Analysis Tool

Analyzes which architectural parameters have the most impact on
performance, power, and density targets.

Author: Architecture Team
Date: 2026-01-02
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple
import os
import sys

sys.path.append(os.path.dirname(__file__))
from performance_model import (
    SoCConfig, ChipletConfig, SMConfig,
    PerformanceModel, PowerModel,
    Precision
)


def sensitivity_analysis(
    base_soc: SoCConfig,
    param_name: str,
    param_values: List[float],
    metric_func,
    metric_name: str
) -> Tuple[List[float], List[float]]:
    """
    Perform sensitivity analysis on a single parameter
    
    Args:
        base_soc: Base SoC configuration
        param_name: Name of parameter to vary
        param_values: List of values to test
        metric_func: Function that takes SoCConfig and returns metric value
        metric_name: Name of metric being analyzed
    
    Returns:
        Tuple of (param_values, metric_values)
    """
    metric_values = []
    
    for val in param_values:
        # Create modified config
        if param_name == 'num_sms':
            chiplet = ChipletConfig(
                num_sms=int(val),
                l2_cache_mb=base_soc.chiplet_config.l2_cache_mb,
                area_mm2=base_soc.chiplet_config.area_mm2,
                sm_config=base_soc.chiplet_config.sm_config
            )
            soc = SoCConfig(
                num_chiplets=base_soc.num_chiplets,
                hbm3e_stacks=base_soc.hbm3e_stacks,
                chiplet_config=chiplet
            )
        elif param_name == 'chiplet_area':
            chiplet = ChipletConfig(
                num_sms=base_soc.chiplet_config.num_sms,
                l2_cache_mb=base_soc.chiplet_config.l2_cache_mb,
                area_mm2=val,
                sm_config=base_soc.chiplet_config.sm_config
            )
            soc = SoCConfig(
                num_chiplets=base_soc.num_chiplets,
                hbm3e_stacks=base_soc.hbm3e_stacks,
                chiplet_config=chiplet
            )
        elif param_name == 'clock_mhz':
            sm = SMConfig(
                cuda_cores=base_soc.chiplet_config.sm_config.cuda_cores,
                tensor_cores=base_soc.chiplet_config.sm_config.tensor_cores,
                clock_mhz=int(val),
                tensor_core_ops_per_cycle=base_soc.chiplet_config.sm_config.tensor_core_ops_per_cycle
            )
            chiplet = ChipletConfig(
                num_sms=base_soc.chiplet_config.num_sms,
                l2_cache_mb=base_soc.chiplet_config.l2_cache_mb,
                area_mm2=base_soc.chiplet_config.area_mm2,
                sm_config=sm
            )
            soc = SoCConfig(
                num_chiplets=base_soc.num_chiplets,
                hbm3e_stacks=base_soc.hbm3e_stacks,
                chiplet_config=chiplet
            )
        elif param_name == 'tensor_cores':
            sm = SMConfig(
                cuda_cores=base_soc.chiplet_config.sm_config.cuda_cores,
                tensor_cores=int(val),
                clock_mhz=base_soc.chiplet_config.sm_config.clock_mhz,
                tensor_core_ops_per_cycle=base_soc.chiplet_config.sm_config.tensor_core_ops_per_cycle
            )
            chiplet = ChipletConfig(
                num_sms=base_soc.chiplet_config.num_sms,
                l2_cache_mb=base_soc.chiplet_config.l2_cache_mb,
                area_mm2=base_soc.chiplet_config.area_mm2,
                sm_config=sm
            )
            soc = SoCConfig(
                num_chiplets=base_soc.num_chiplets,
                hbm3e_stacks=base_soc.hbm3e_stacks,
                chiplet_config=chiplet
            )
        elif param_name == 'fp16_ops_per_cycle':
            ops_dict = base_soc.chiplet_config.sm_config.tensor_core_ops_per_cycle.copy()
            ops_dict[Precision.FP16] = int(val)
            sm = SMConfig(
                cuda_cores=base_soc.chiplet_config.sm_config.cuda_cores,
                tensor_cores=base_soc.chiplet_config.sm_config.tensor_cores,
                clock_mhz=base_soc.chiplet_config.sm_config.clock_mhz,
                tensor_core_ops_per_cycle=ops_dict
            )
            chiplet = ChipletConfig(
                num_sms=base_soc.chiplet_config.num_sms,
                l2_cache_mb=base_soc.chiplet_config.l2_cache_mb,
                area_mm2=base_soc.chiplet_config.area_mm2,
                sm_config=sm
            )
            soc = SoCConfig(
                num_chiplets=base_soc.num_chiplets,
                hbm3e_stacks=base_soc.hbm3e_stacks,
                chiplet_config=chiplet
            )
        else:
            raise ValueError(f"Unknown parameter: {param_name}")
        
        metric_val = metric_func(soc)
        metric_values.append(metric_val)
    
    return param_values, metric_values


def analyze_all_parameters(base_soc: SoCConfig, save_path: str = None):
    """Analyze sensitivity of all key parameters"""
    
    # Define metrics
    def compute_density(soc):
        perf = PerformanceModel(soc)
        return perf.compute_density(Precision.FP16)
    
    def total_power(soc):
        power = PowerModel(soc)
        return power.total_power(1.0)
    
    def peak_tflops(soc):
        perf = PerformanceModel(soc)
        return perf.peak_compute(Precision.FP16)
    
    def efficiency(soc):
        perf = PerformanceModel(soc)
        power = PowerModel(soc)
        return perf.peak_compute(Precision.FP16) / power.total_power(1.0)
    
    # Parameters to analyze
    analyses = [
        ('num_sms', np.arange(16, 65, 4), 'Number of SMs per Chiplet', 'SMs'),
        ('chiplet_area', np.arange(250, 450, 10), 'Chiplet Area (mm²)', 'mm²'),
        ('clock_mhz', np.arange(1500, 3000, 100), 'Clock Frequency (MHz)', 'MHz'),
        ('tensor_cores', np.arange(2, 11, 1), 'Tensor Cores per SM', 'cores'),
        ('fp16_ops_per_cycle', np.arange(64, 320, 16), 'FP16 Ops per Cycle per Tensor Core', 'ops/cycle'),
    ]
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    print("\n" + "=" * 100)
    print("SENSITIVITY ANALYSIS")
    print("=" * 100)
    
    for idx, (param_name, param_values, param_label, param_unit) in enumerate(analyses):
        ax = axes[idx]
        
        # Analyze compute density
        _, density_vals = sensitivity_analysis(
            base_soc, param_name, param_values, compute_density, 'Density'
        )
        
        # Analyze power
        _, power_vals = sensitivity_analysis(
            base_soc, param_name, param_values, total_power, 'Power'
        )
        
        # Analyze peak performance
        _, perf_vals = sensitivity_analysis(
            base_soc, param_name, param_values, peak_tflops, 'Performance'
        )
        
        # Plot
        ax2 = ax.twinx()
        ax3 = ax.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        
        line1 = ax.plot(param_values, density_vals, 'b-o', linewidth=2, 
                       markersize=6, label='Density (TFLOPS/mm²)')
        line2 = ax2.plot(param_values, power_vals, 'r-s', linewidth=2, 
                        markersize=6, label='Power (W)')
        line3 = ax3.plot(param_values, perf_vals, 'g-^', linewidth=2, 
                        markersize=6, label='Peak TFLOPS')
        
        # Add target lines
        ax.axhline(2.0, color='b', linestyle='--', alpha=0.5, label='Density Target')
        ax2.axhline(500, color='r', linestyle='--', alpha=0.5, label='Power Target')
        
        ax.set_xlabel(f'{param_label} ({param_unit})', fontsize=11)
        ax.set_ylabel('Density (TFLOPS/mm²)', color='b', fontsize=11)
        ax2.set_ylabel('Power (W)', color='r', fontsize=11)
        ax3.set_ylabel('Peak TFLOPS', color='g', fontsize=11)
        ax.set_title(f'Sensitivity: {param_label}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Calculate sensitivity (normalized derivative)
        if len(density_vals) > 1:
            base_density = density_vals[0]
            base_param = param_values[0]
            final_density = density_vals[-1]
            final_param = param_values[-1]
            
            if base_density > 0 and base_param > 0:
                sensitivity = ((final_density - base_density) / base_density) / \
                              ((final_param - base_param) / base_param)
                print(f"\n{param_label}:")
                print(f"  Sensitivity: {sensitivity:.2f} (normalized)")
                print(f"  Density range: {min(density_vals):.3f} - {max(density_vals):.3f} TFLOPS/mm²")
                print(f"  Power range: {min(power_vals):.1f} - {max(power_vals):.1f} W")
    
    # Remove empty subplot
    fig.delaxes(axes[5])
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n✓ Sensitivity analysis plot saved: {save_path}")
    else:
        plt.show()
    
    print("\n" + "=" * 100)
    print("KEY INSIGHTS")
    print("=" * 100)
    print("\n1. Parameters with highest impact on density:")
    print("   - Number of SMs per chiplet (direct scaling)")
    print("   - Chiplet area (inverse relationship)")
    print("   - FP16 ops per cycle (compute capability)")
    print("\n2. Parameters affecting power:")
    print("   - Clock frequency (quadratic relationship)")
    print("   - Number of SMs (linear relationship)")
    print("\n3. Best trade-offs:")
    print("   - Increase SMs while reducing area")
    print("   - Optimize tensor core efficiency (ops/cycle)")
    print("   - Moderate clock increases (diminishing returns)")


def main():
    """Main sensitivity analysis"""
    print("=" * 100)
    print("NexGen-AI SoC Sensitivity Analysis")
    print("=" * 100)
    
    # Create baseline
    sm = SMConfig()
    chiplet = ChipletConfig(sm_config=sm)
    base_soc = SoCConfig(chiplet_config=chiplet)
    
    print(f"\nBaseline Configuration:")
    print(f"  SMs per chiplet: {chiplet.num_sms}")
    print(f"  Chiplet area: {chiplet.area_mm2} mm²")
    print(f"  Clock: {sm.clock_mhz} MHz")
    print(f"  Tensor cores: {sm.tensor_cores}")
    print(f"  FP16 ops/cycle: {sm.tensor_core_ops_per_cycle[Precision.FP16]}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(script_dir, '..', '..', 'outputs')
    sensitivity_path = os.path.join(outputs_dir, 'sensitivity_analysis.png')
    
    analyze_all_parameters(base_soc, save_path=sensitivity_path)


if __name__ == "__main__":
    main()

