#!/usr/bin/env python3
"""
Architecture Exploration Tool

Compares different architectural configurations to find optimal
trade-offs for meeting performance targets.

Author: Architecture Team
Date: 2026-01-02
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List
import os
import sys

# Import from performance_model
sys.path.append(os.path.dirname(__file__))
from performance_model import (
    SoCConfig, ChipletConfig, SMConfig,
    PerformanceModel, PowerModel, ScalingModel,
    Precision
)


@dataclass
class ArchitectureVariant:
    """Represents an architectural configuration variant"""
    name: str
    description: str
    sm_config: SMConfig
    chiplet_config: ChipletConfig
    soc_config: SoCConfig
    
    def evaluate(self) -> Dict:
        """Evaluate this architecture variant"""
        perf_model = PerformanceModel(self.soc_config)
        power_model = PowerModel(self.soc_config)
        
        fp16_density = perf_model.compute_density(Precision.FP16)
        fp16_peak = perf_model.peak_compute(Precision.FP16)
        total_power = power_model.total_power(1.0)
        efficiency = power_model.power_efficiency(Precision.FP16, 1.0)
        
        return {
            'name': self.name,
            'fp16_tflops': fp16_peak,
            'fp16_density_tflops_per_mm2': fp16_density,
            'total_power_w': total_power,
            'efficiency_tflops_per_w': efficiency,
            'total_area_mm2': self.soc_config.total_area_mm2,
            'num_chiplets': self.soc_config.num_chiplets,
            'total_sms': self.soc_config.total_sms,
            'meets_density_target': fp16_density >= 2.0,
            'meets_power_target': total_power <= 500.0,
        }


def create_baseline() -> ArchitectureVariant:
    """Create baseline configuration"""
    sm = SMConfig(
        cuda_cores=128,
        tensor_cores=4,
        clock_mhz=2000,
        tensor_core_ops_per_cycle={
            Precision.FP4: 512,
            Precision.FP8: 256,
            Precision.INT8: 256,
            Precision.FP16: 128,
            Precision.BF16: 128,
            Precision.FP32: 64,
        }
    )
    
    chiplet = ChipletConfig(
        num_sms=16,
        l2_cache_mb=6,
        area_mm2=400,
        sm_config=sm
    )
    
    soc = SoCConfig(
        num_chiplets=4,
        hbm3e_stacks=8,
        chiplet_config=chiplet
    )
    
    return ArchitectureVariant(
        name="Baseline",
        description="Original baseline configuration",
        sm_config=sm,
        chiplet_config=chiplet,
        soc_config=soc
    )


def create_aggressive_optimized() -> ArchitectureVariant:
    """Option A: Aggressive optimization to hit 2.0 TFLOPS/mm²"""
    sm = SMConfig(
        cuda_cores=128,
        tensor_cores=8,  # Doubled from 4
        clock_mhz=2500,  # Increased from 2000
        tensor_core_ops_per_cycle={
            Precision.FP4: 512,
            Precision.FP8: 256,
            Precision.INT8: 256,
            Precision.FP16: 256,  # Doubled from 128
            Precision.BF16: 256,
            Precision.FP32: 128,  # Doubled from 64
        }
    )
    
    chiplet = ChipletConfig(
        num_sms=48,  # 3x increase from 16
        l2_cache_mb=8,  # Slightly increased
        area_mm2=300,  # Reduced 25% from 400
        sm_config=sm
    )
    
    soc = SoCConfig(
        num_chiplets=4,
        hbm3e_stacks=8,
        chiplet_config=chiplet
    )
    
    return ArchitectureVariant(
        name="Aggressive Optimized",
        description="3x SMs, 2x tensor cores, higher clock, denser ops",
        sm_config=sm,
        chiplet_config=chiplet,
        soc_config=soc
    )


def create_realistic_optimized() -> ArchitectureVariant:
    """Option C: Realistic optimization (0.8-1.0 TFLOPS/mm²)"""
    sm = SMConfig(
        cuda_cores=128,
        tensor_cores=6,  # 1.5x increase
        clock_mhz=2300,  # Moderate increase
        tensor_core_ops_per_cycle={
            Precision.FP4: 512,
            Precision.FP8: 256,
            Precision.INT8: 256,
            Precision.FP16: 192,  # 1.5x increase
            Precision.BF16: 192,
            Precision.FP32: 96,  # 1.5x increase
        }
    )
    
    chiplet = ChipletConfig(
        num_sms=32,  # 2x increase from 16
        l2_cache_mb=7,
        area_mm2=350,  # Reduced 12.5% from 400
        sm_config=sm
    )
    
    soc = SoCConfig(
        num_chiplets=4,
        hbm3e_stacks=8,
        chiplet_config=chiplet
    )
    
    return ArchitectureVariant(
        name="Realistic Optimized",
        description="2x SMs, 1.5x tensor cores, moderate clock boost",
        sm_config=sm,
        chiplet_config=chiplet,
        soc_config=soc
    )


def create_high_sm_density() -> ArchitectureVariant:
    """High SM density variant"""
    sm = SMConfig(
        cuda_cores=128,
        tensor_cores=4,
        clock_mhz=2200,
        tensor_core_ops_per_cycle={
            Precision.FP4: 512,
            Precision.FP8: 256,
            Precision.INT8: 256,
            Precision.FP16: 160,  # Moderate increase
            Precision.BF16: 160,
            Precision.FP32: 80,
        }
    )
    
    chiplet = ChipletConfig(
        num_sms=40,  # 2.5x increase
        l2_cache_mb=8,
        area_mm2=320,  # Reduced 20%
        sm_config=sm
    )
    
    soc = SoCConfig(
        num_chiplets=4,
        hbm3e_stacks=8,
        chiplet_config=chiplet
    )
    
    return ArchitectureVariant(
        name="High SM Density",
        description="2.5x SMs, optimized area, moderate improvements",
        sm_config=sm,
        chiplet_config=chiplet,
        soc_config=soc
    )


def create_power_optimized() -> ArchitectureVariant:
    """Power-optimized variant (lower power, still good performance)"""
    sm = SMConfig(
        cuda_cores=128,
        tensor_cores=4,
        clock_mhz=1800,  # Lower clock for power savings
        tensor_core_ops_per_cycle={
            Precision.FP4: 512,
            Precision.FP8: 256,
            Precision.INT8: 256,
            Precision.FP16: 128,
            Precision.BF16: 128,
            Precision.FP32: 64,
        }
    )
    
    chiplet = ChipletConfig(
        num_sms=24,  # Moderate increase
        l2_cache_mb=6,
        area_mm2=380,  # Slightly reduced
        sm_config=sm
    )
    
    soc = SoCConfig(
        num_chiplets=4,
        hbm3e_stacks=8,
        chiplet_config=chiplet
    )
    
    return ArchitectureVariant(
        name="Power Optimized",
        description="Lower clock, moderate SM increase, focus on efficiency",
        sm_config=sm,
        chiplet_config=chiplet,
        soc_config=soc
    )


def compare_variants(variants: List[ArchitectureVariant], 
                   save_path: str = None) -> None:
    """Compare multiple architecture variants"""
    results = [v.evaluate() for v in variants]
    
    # Print comparison table
    print("\n" + "=" * 100)
    print("ARCHITECTURE VARIANT COMPARISON")
    print("=" * 100)
    print(f"\n{'Variant':<25} {'FP16 TFLOPS':<15} {'Density':<15} {'Power (W)':<15} {'TFLOPS/W':<15} {'Status':<15}")
    print("-" * 100)
    
    for r in results:
        density = r['fp16_density_tflops_per_mm2']
        power = r['total_power_w']
        
        status = []
        if r['meets_density_target']:
            status.append("✓Density")
        if r['meets_power_target']:
            status.append("✓Power")
        if not status:
            status.append("✗")
        
        print(f"{r['name']:<25} {r['fp16_tflops']:<15.1f} {density:<15.3f} "
              f"{power:<15.1f} {r['efficiency_tflops_per_w']:<15.2f} {' '.join(status):<15}")
    
    # Create comparison plots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    names = [r['name'] for r in results]
    
    # Density comparison
    ax = axes[0, 0]
    densities = [r['fp16_density_tflops_per_mm2'] for r in results]
    colors = ['green' if d >= 2.0 else 'red' for d in densities]
    ax.barh(names, densities, color=colors, alpha=0.7)
    ax.axvline(2.0, color='k', linestyle='--', linewidth=2, label='Target: 2.0 TFLOPS/mm²')
    ax.set_xlabel('Compute Density (TFLOPS/mm²)', fontsize=12)
    ax.set_title('Compute Density Comparison', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')
    
    # Power comparison
    ax = axes[0, 1]
    powers = [r['total_power_w'] for r in results]
    colors = ['green' if p <= 500 else 'red' for p in powers]
    ax.barh(names, powers, color=colors, alpha=0.7)
    ax.axvline(500, color='k', linestyle='--', linewidth=2, label='Target: 500W')
    ax.set_xlabel('Power Consumption (Watts)', fontsize=12)
    ax.set_title('Power Consumption Comparison', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')
    
    # Efficiency comparison
    ax = axes[1, 0]
    efficiencies = [r['efficiency_tflops_per_w'] for r in results]
    ax.barh(names, efficiencies, color='blue', alpha=0.7)
    ax.set_xlabel('Power Efficiency (TFLOPS/W)', fontsize=12)
    ax.set_title('Power Efficiency Comparison', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Area vs Performance scatter
    ax = axes[1, 1]
    areas = [r['total_area_mm2'] for r in results]
    tflops = [r['fp16_tflops'] for r in results]
    colors = ['green' if r['meets_density_target'] and r['meets_power_target'] 
              else 'orange' if r['meets_power_target'] else 'red' 
              for r in results]
    ax.scatter(areas, tflops, s=200, c=colors, alpha=0.6, edgecolors='black', linewidth=2)
    for i, name in enumerate(names):
        ax.annotate(name, (areas[i], tflops[i]), 
                   xytext=(5, 5), textcoords='offset points', fontsize=9)
    ax.set_xlabel('Total Area (mm²)', fontsize=12)
    ax.set_ylabel('Peak FP16 Performance (TFLOPS)', fontsize=12)
    ax.set_title('Area vs Performance Trade-off', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n✓ Comparison plot saved: {save_path}")
    else:
        plt.show()
    
    # Detailed analysis
    print("\n" + "=" * 100)
    print("DETAILED ANALYSIS")
    print("=" * 100)
    
    for r in results:
        print(f"\n{r['name']}:")
        print(f"  Description: {next(v.description for v in variants if v.name == r['name'])}")
        print(f"  Total SMs: {r['total_sms']}")
        print(f"  Total Area: {r['total_area_mm2']:.1f} mm²")
        print(f"  FP16 Performance: {r['fp16_tflops']:.1f} TFLOPS")
        print(f"  Compute Density: {r['fp16_density_tflops_per_mm2']:.3f} TFLOPS/mm²")
        print(f"  Power: {r['total_power_w']:.1f} W")
        print(f"  Efficiency: {r['efficiency_tflops_per_w']:.2f} TFLOPS/W")
        
        if r['meets_density_target']:
            print(f"  ✓ Meets density target (2.0 TFLOPS/mm²)")
        else:
            gap = 2.0 - r['fp16_density_tflops_per_mm2']
            print(f"  ✗ Below density target by {gap:.3f} TFLOPS/mm²")
        
        if r['meets_power_target']:
            print(f"  ✓ Meets power target (500W)")
        else:
            excess = r['total_power_w'] - 500.0
            print(f"  ✗ Exceeds power target by {excess:.1f} W")


def main():
    """Main exploration function"""
    print("=" * 100)
    print("NexGen-AI SoC Architecture Exploration")
    print("=" * 100)
    
    # Create variants
    variants = [
        create_baseline(),
        create_realistic_optimized(),
        create_high_sm_density(),
        create_aggressive_optimized(),
        create_power_optimized(),
    ]
    
    # Compare variants
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(script_dir, '..', '..', 'outputs')
    comparison_path = os.path.join(outputs_dir, 'architecture_comparison.png')
    
    compare_variants(variants, save_path=comparison_path)
    
    print("\n" + "=" * 100)
    print("RECOMMENDATIONS")
    print("=" * 100)
    
    results = [v.evaluate() for v in variants]
    
    # Find best variant
    power_compliant = [r for r in results if r['meets_power_target']]
    if power_compliant:
        best_density = max(power_compliant, key=lambda x: x['fp16_density_tflops_per_mm2'])
        print(f"\n✓ Best configuration meeting power target: {best_density['name']}")
        print(f"  Density: {best_density['fp16_density_tflops_per_mm2']:.3f} TFLOPS/mm²")
        print(f"  Power: {best_density['total_power_w']:.1f} W")
        print(f"  Efficiency: {best_density['efficiency_tflops_per_w']:.2f} TFLOPS/W")
    
    # Check if any meet density target
    meets_density = [r for r in results if r['meets_density_target']]
    if not meets_density:
        print("\n⚠️  WARNING: No configuration meets the 2.0 TFLOPS/mm² target")
        print("   Consider revising target to 0.5-1.0 TFLOPS/mm² (competitive with H100)")
    
    print("\nNext steps:")
    print("  1. Review comparison plots")
    print("  2. Select configuration based on priorities (density vs power vs efficiency)")
    print("  3. Run sensitivity analysis to identify critical parameters")
    print("  4. Update PRD with realistic targets if needed")


if __name__ == "__main__":
    main()

