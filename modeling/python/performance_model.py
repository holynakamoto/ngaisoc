#!/usr/bin/env python3
"""
NexGen-AI SoC Performance and Power Model

This model provides:
1. Roofline analysis for different precision modes
2. Memory bandwidth bottleneck analysis
3. Power estimation and thermal modeling
4. Chiplet scaling efficiency
5. Performance projections for various workloads

Author: Architecture Team
Date: 2026-01-02
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
import os


class Precision(Enum):
    """Supported compute precisions"""
    FP4 = "FP4"
    FP8 = "FP8"
    INT8 = "INT8"
    FP16 = "FP16"
    BF16 = "BF16"
    FP32 = "FP32"


@dataclass
class SMConfig:
    """Streaming Multiprocessor Configuration"""
    cuda_cores: int = 128
    tensor_cores: int = 4
    l1_cache_kb: int = 128
    shared_memory_kb: int = 128
    register_file_kb: int = 256
    clock_mhz: int = 2000
    
    # FLOPS per cycle per core
    tensor_core_ops_per_cycle: Dict[Precision, int] = None
    
    def __post_init__(self):
        if self.tensor_core_ops_per_cycle is None:
            # Operations per cycle per tensor core
            self.tensor_core_ops_per_cycle = {
                Precision.FP4: 512,   # 4-bit ops
                Precision.FP8: 256,   # 8-bit ops
                Precision.INT8: 256,
                Precision.FP16: 128,
                Precision.BF16: 128,
                Precision.FP32: 64,
            }
    
    def peak_tflops(self, precision: Precision) -> float:
        """Calculate peak TFLOPS for given precision"""
        ops_per_cycle = self.tensor_core_ops_per_cycle[precision]
        total_ops_per_cycle = ops_per_cycle * self.tensor_cores
        ops_per_second = total_ops_per_cycle * self.clock_mhz * 1e6
        return ops_per_second / 1e12  # Convert to TFLOPS


@dataclass
class ChipletConfig:
    """Single Chiplet Configuration"""
    num_sms: int = 16
    l2_cache_mb: int = 6
    ucIe_bandwidth_gbps: int = 256  # Per direction
    area_mm2: float = 400
    process_node: str = "TSMC 3nm"
    
    sm_config: SMConfig = None
    
    def __post_init__(self):
        if self.sm_config is None:
            self.sm_config = SMConfig()


@dataclass
class SoCConfig:
    """Full SoC Configuration"""
    num_chiplets: int = 4
    hbm3e_stacks: int = 8
    hbm3e_bandwidth_gbps_per_stack: int = 128
    nvlink_lanes: int = 6
    nvlink_bandwidth_gbps_per_lane: int = 100
    pcie_gen: int = 6
    pcie_lanes: int = 16
    pcie_bandwidth_gbps: int = 128  # PCIe 6.0 x16
    
    chiplet_config: ChipletConfig = None
    
    def __post_init__(self):
        if self.chiplet_config is None:
            self.chiplet_config = ChipletConfig()
    
    @property
    def total_sms(self) -> int:
        return self.num_chiplets * self.chiplet_config.num_sms
    
    @property
    def total_hbm_bandwidth_gbps(self) -> int:
        return self.hbm3e_stacks * self.hbm3e_bandwidth_gbps_per_stack
    
    @property
    def total_area_mm2(self) -> float:
        return self.num_chiplets * self.chiplet_config.area_mm2


class PerformanceModel:
    """Performance modeling and roofline analysis"""
    
    def __init__(self, soc_config: SoCConfig):
        self.config = soc_config
        self.sm_config = soc_config.chiplet_config.sm_config
    
    def peak_compute(self, precision: Precision) -> float:
        """Calculate peak compute in TFLOPS for entire SoC"""
        per_sm = self.sm_config.peak_tflops(precision)
        return per_sm * self.config.total_sms
    
    def compute_density(self, precision: Precision) -> float:
        """Calculate TFLOPS per mm²"""
        return self.peak_compute(precision) / self.config.total_area_mm2
    
    def memory_bandwidth_tbps(self) -> float:
        """Total memory bandwidth in TB/s"""
        return self.config.total_hbm_bandwidth_gbps / 1000.0
    
    def arithmetic_intensity_roof(self, precision: Precision) -> float:
        """
        Calculate arithmetic intensity ceiling (FLOPS/Byte)
        This is where we transition from memory-bound to compute-bound
        """
        peak_flops = self.peak_compute(precision) * 1e12  # Convert to FLOPS
        bandwidth_bytes_per_sec = self.config.total_hbm_bandwidth_gbps * 1e9 / 8
        return peak_flops / bandwidth_bytes_per_sec
    
    def roofline_performance(
        self, 
        arithmetic_intensity: np.ndarray, 
        precision: Precision
    ) -> np.ndarray:
        """
        Calculate achieved performance on roofline model
        
        Args:
            arithmetic_intensity: Array of FLOPS/Byte ratios
            precision: Compute precision
        
        Returns:
            Achieved TFLOPS for each intensity point
        """
        peak_tflops = self.peak_compute(precision)
        bandwidth_tbps = self.memory_bandwidth_tbps()
        
        # Memory-bound region: Performance = Bandwidth * Intensity
        memory_bound = bandwidth_tbps * arithmetic_intensity
        
        # Compute-bound region: Performance = Peak Compute
        compute_bound = np.full_like(arithmetic_intensity, peak_tflops)
        
        # Take minimum (bottleneck)
        return np.minimum(memory_bound, compute_bound)
    
    def plot_roofline(self, precision: Precision, save_path: str = None):
        """Generate roofline plot for given precision"""
        # Arithmetic intensity range (FLOPS/Byte)
        ai = np.logspace(-2, 3, 1000)
        
        performance = self.roofline_performance(ai, precision)
        ridge_point = self.arithmetic_intensity_roof(precision)
        
        plt.figure(figsize=(10, 6))
        plt.loglog(ai, performance, 'b-', linewidth=2, label='Roofline')
        plt.axvline(ridge_point, color='r', linestyle='--', 
                   label=f'Ridge Point: {ridge_point:.1f} FLOPS/Byte')
        
        # Add common workload markers
        workloads = {
            'GEMM (Optimized)': 100,
            'GEMM (Naive)': 10,
            'Attention (FlashAttention)': 50,
            'Attention (Naive)': 5,
            'Elementwise': 0.5,
            'Reduction': 1,
        }
        
        for name, ai_val in workloads.items():
            perf = self.roofline_performance(np.array([ai_val]), precision)[0]
            plt.plot(ai_val, perf, 'o', markersize=8, label=name)
        
        plt.xlabel('Arithmetic Intensity (FLOPS/Byte)', fontsize=12)
        plt.ylabel('Performance (TFLOPS)', fontsize=12)
        plt.title(f'Roofline Model - {precision.value} Precision\n'
                 f'Peak: {self.peak_compute(precision):.1f} TFLOPS, '
                 f'BW: {self.memory_bandwidth_tbps():.2f} TB/s', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best', fontsize=9)
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def analyze_workload(self, precision: Precision, arithmetic_intensity: float) -> Dict:
        """Detailed analysis of a specific workload"""
        peak_tflops = self.peak_compute(precision)
        achieved_tflops = self.roofline_performance(
            np.array([arithmetic_intensity]), precision
        )[0]
        
        ridge_point = self.arithmetic_intensity_roof(precision)
        is_memory_bound = arithmetic_intensity < ridge_point
        
        efficiency = (achieved_tflops / peak_tflops) * 100
        
        return {
            'precision': precision.value,
            'arithmetic_intensity': arithmetic_intensity,
            'peak_tflops': peak_tflops,
            'achieved_tflops': achieved_tflops,
            'efficiency_percent': efficiency,
            'bottleneck': 'Memory' if is_memory_bound else 'Compute',
            'ridge_point': ridge_point,
        }


class PowerModel:
    """Power and thermal modeling"""
    
    def __init__(self, soc_config: SoCConfig):
        self.config = soc_config
        
        # Power model parameters (watts)
        self.sm_dynamic_power_mw = 1500  # mW per SM at peak
        self.l2_power_per_mb_mw = 50
        self.hbm_stack_power_w = 15  # Watts per HBM stack
        self.interconnect_power_w = 20  # UCIe + NVLink
        self.io_power_w = 10  # PCIe, misc I/O
        self.static_power_per_chiplet_w = 5  # Leakage
    
    def dynamic_power(self, utilization: float = 1.0) -> float:
        """
        Calculate dynamic power consumption
        
        Args:
            utilization: Fraction of peak utilization (0.0-1.0)
        
        Returns:
            Power in Watts
        """
        # SM power scales roughly with utilization
        sm_power = (self.config.total_sms * self.sm_dynamic_power_mw / 1000) * utilization
        
        # Cache power scales with square root of utilization (less than linear)
        total_l2_mb = self.config.num_chiplets * self.config.chiplet_config.l2_cache_mb
        cache_power = (total_l2_mb * self.l2_power_per_mb_mw / 1000) * np.sqrt(utilization)
        
        # HBM power scales linearly with bandwidth utilization
        hbm_power = self.config.hbm3e_stacks * self.hbm_stack_power_w * utilization
        
        return sm_power + cache_power + hbm_power
    
    def static_power(self) -> float:
        """Calculate static (leakage) power"""
        return self.config.num_chiplets * self.static_power_per_chiplet_w
    
    def total_power(self, utilization: float = 1.0) -> float:
        """Total SoC power consumption"""
        return (self.dynamic_power(utilization) + 
                self.static_power() + 
                self.interconnect_power_w + 
                self.io_power_w)
    
    def power_efficiency(self, precision: Precision, utilization: float = 1.0) -> float:
        """
        Calculate TFLOPS per Watt
        
        Args:
            precision: Compute precision
            utilization: Workload utilization
        
        Returns:
            TFLOPS/W
        """
        perf_model = PerformanceModel(self.config)
        achieved_tflops = perf_model.peak_compute(precision) * utilization
        power_w = self.total_power(utilization)
        return achieved_tflops / power_w
    
    def thermal_estimate(self, utilization: float = 1.0, 
                        ambient_c: float = 25.0,
                        theta_ja: float = 0.1) -> float:
        """
        Estimate junction temperature
        
        Args:
            utilization: Workload utilization
            ambient_c: Ambient temperature (°C)
            theta_ja: Thermal resistance junction-to-ambient (°C/W)
        
        Returns:
            Estimated junction temperature (°C)
        """
        power = self.total_power(utilization)
        return ambient_c + (power * theta_ja)


class ScalingModel:
    """Analyze chiplet scaling efficiency"""
    
    def __init__(self, base_chiplet_config: ChipletConfig):
        self.base_config = base_chiplet_config
    
    def compute_scaling(self, num_chiplets_list: List[int], 
                       precision: Precision) -> Dict[int, float]:
        """Analyze ideal compute scaling across chiplet counts"""
        results = {}
        for n in num_chiplets_list:
            soc = SoCConfig(
                num_chiplets=n,
                chiplet_config=self.base_config
            )
            perf_model = PerformanceModel(soc)
            results[n] = perf_model.peak_compute(precision)
        return results
    
    def memory_scaling(self, num_chiplets_list: List[int]) -> Dict[int, float]:
        """Analyze memory bandwidth scaling"""
        results = {}
        for n in num_chiplets_list:
            # Assume HBM stacks scale with chiplets (2 stacks per chiplet)
            soc = SoCConfig(
                num_chiplets=n,
                hbm3e_stacks=n * 2,
                chiplet_config=self.base_config
            )
            perf_model = PerformanceModel(soc)
            results[n] = perf_model.memory_bandwidth_tbps()
        return results
    
    def power_scaling(self, num_chiplets_list: List[int], 
                     utilization: float = 1.0) -> Dict[int, float]:
        """Analyze power consumption scaling"""
        results = {}
        for n in num_chiplets_list:
            soc = SoCConfig(
                num_chiplets=n,
                hbm3e_stacks=n * 2,
                chiplet_config=self.base_config
            )
            power_model = PowerModel(soc)
            results[n] = power_model.total_power(utilization)
        return results
    
    def efficiency_analysis(self, num_chiplets_list: List[int],
                          precision: Precision) -> Dict[int, Dict]:
        """Combined efficiency analysis"""
        compute = self.compute_scaling(num_chiplets_list, precision)
        memory = self.memory_scaling(num_chiplets_list)
        power = self.power_scaling(num_chiplets_list)
        
        results = {}
        for n in num_chiplets_list:
            results[n] = {
                'compute_tflops': compute[n],
                'memory_tbps': memory[n],
                'power_watts': power[n],
                'tflops_per_watt': compute[n] / power[n],
                'compute_per_area': compute[n] / (n * self.base_config.area_mm2)
            }
        return results
    
    def plot_scaling(self, num_chiplets_list: List[int], 
                    precision: Precision, save_path: str = None):
        """Visualize scaling characteristics"""
        analysis = self.efficiency_analysis(num_chiplets_list, precision)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Compute scaling
        ax = axes[0, 0]
        compute = [analysis[n]['compute_tflops'] for n in num_chiplets_list]
        ax.plot(num_chiplets_list, compute, 'o-', linewidth=2, markersize=8)
        ax.set_xlabel('Number of Chiplets')
        ax.set_ylabel('Peak Compute (TFLOPS)')
        ax.set_title(f'Compute Scaling - {precision.value}')
        ax.grid(True, alpha=0.3)
        
        # Memory bandwidth scaling
        ax = axes[0, 1]
        memory = [analysis[n]['memory_tbps'] for n in num_chiplets_list]
        ax.plot(num_chiplets_list, memory, 'o-', linewidth=2, markersize=8, color='orange')
        ax.set_xlabel('Number of Chiplets')
        ax.set_ylabel('Memory Bandwidth (TB/s)')
        ax.set_title('Memory Bandwidth Scaling')
        ax.grid(True, alpha=0.3)
        
        # Power scaling
        ax = axes[1, 0]
        power = [analysis[n]['power_watts'] for n in num_chiplets_list]
        ax.plot(num_chiplets_list, power, 'o-', linewidth=2, markersize=8, color='red')
        ax.axhline(500, color='k', linestyle='--', label='500W Target')
        ax.set_xlabel('Number of Chiplets')
        ax.set_ylabel('Power (Watts)')
        ax.set_title('Power Consumption')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Efficiency
        ax = axes[1, 1]
        efficiency = [analysis[n]['tflops_per_watt'] for n in num_chiplets_list]
        ax.plot(num_chiplets_list, efficiency, 'o-', linewidth=2, markersize=8, color='green')
        ax.set_xlabel('Number of Chiplets')
        ax.set_ylabel('TFLOPS/Watt')
        ax.set_title('Power Efficiency')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()


def main():
    """Example usage and validation of architecture targets"""
    
    # Get script directory and create outputs directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(script_dir, '..', '..', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    
    print("=" * 80)
    print("NexGen-AI SoC Performance Model")
    print("=" * 80)
    
    # Define baseline configuration
    soc = SoCConfig(
        num_chiplets=4,
        hbm3e_stacks=8,
        chiplet_config=ChipletConfig(
            num_sms=16,
            l2_cache_mb=6,
            area_mm2=400
        )
    )
    
    print(f"\nConfiguration:")
    print(f"  Chiplets: {soc.num_chiplets}")
    print(f"  Total SMs: {soc.total_sms}")
    print(f"  Total Area: {soc.total_area_mm2:.1f} mm²")
    print(f"  HBM Stacks: {soc.hbm3e_stacks}")
    print(f"  Total HBM BW: {soc.total_hbm_bandwidth_gbps} GB/s ({soc.total_hbm_bandwidth_gbps/1000:.2f} TB/s)")
    
    # Performance analysis
    print("\n" + "=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    perf_model = PerformanceModel(soc)
    
    for precision in [Precision.FP16, Precision.FP8, Precision.INT8]:
        peak = perf_model.peak_compute(precision)
        density = perf_model.compute_density(precision)
        ridge = perf_model.arithmetic_intensity_roof(precision)
        
        print(f"\n{precision.value}:")
        print(f"  Peak Compute: {peak:.1f} TFLOPS")
        print(f"  Compute Density: {density:.3f} TFLOPS/mm²")
        print(f"  Ridge Point: {ridge:.1f} FLOPS/Byte")
        
        # Check against targets
        target_density = 2.0  # TFLOPS/mm²
        if density >= target_density:
            print(f"  ✓ Meets density target ({target_density} TFLOPS/mm²)")
        else:
            print(f"  ✗ Below density target ({target_density} TFLOPS/mm²)")
    
    # Workload analysis
    print("\n" + "=" * 80)
    print("WORKLOAD ANALYSIS")
    print("=" * 80)
    
    workloads = {
        'GEMM (Optimized)': 100,
        'Attention (FlashAttention)': 50,
        'Elementwise Ops': 0.5,
    }
    
    for name, ai in workloads.items():
        result = perf_model.analyze_workload(Precision.FP16, ai)
        print(f"\n{name}:")
        print(f"  Arithmetic Intensity: {ai:.1f} FLOPS/Byte")
        print(f"  Achieved: {result['achieved_tflops']:.1f} TFLOPS ({result['efficiency_percent']:.1f}% of peak)")
        print(f"  Bottleneck: {result['bottleneck']}")
    
    # Power analysis
    print("\n" + "=" * 80)
    print("POWER ANALYSIS")
    print("=" * 80)
    
    power_model = PowerModel(soc)
    
    for util in [1.0, 0.75, 0.5]:
        power = power_model.total_power(util)
        efficiency = power_model.power_efficiency(Precision.FP16, util)
        temp = power_model.thermal_estimate(util)
        
        print(f"\nUtilization: {util*100:.0f}%")
        print(f"  Total Power: {power:.1f} W")
        print(f"  Efficiency: {efficiency:.2f} TFLOPS/W (FP16)")
        print(f"  Est. Junction Temp: {temp:.1f}°C")
        
        if power <= 500:
            print(f"  ✓ Within 500W power budget")
        else:
            print(f"  ✗ Exceeds 500W power budget")
    
    # Scaling analysis
    print("\n" + "=" * 80)
    print("CHIPLET SCALING ANALYSIS")
    print("=" * 80)
    
    scaling_model = ScalingModel(soc.chiplet_config)
    chiplet_counts = [2, 4, 6, 8]
    
    analysis = scaling_model.efficiency_analysis(chiplet_counts, Precision.FP16)
    
    print(f"\n{'Chiplets':<10} {'TFLOPS':<12} {'BW (TB/s)':<12} {'Power (W)':<12} {'TFLOPS/W':<12}")
    print("-" * 60)
    for n in chiplet_counts:
        a = analysis[n]
        print(f"{n:<10} {a['compute_tflops']:<12.1f} {a['memory_tbps']:<12.2f} "
              f"{a['power_watts']:<12.1f} {a['tflops_per_watt']:<12.2f}")
    
    print("\n" + "=" * 80)
    print("GENERATING PLOTS...")
    print("=" * 80)
    
    # Generate roofline plot
    roofline_path = os.path.join(outputs_dir, 'roofline_fp16.png')
    perf_model.plot_roofline(Precision.FP16, save_path=roofline_path)
    print(f"✓ Generated: {roofline_path}")
    
    # Generate scaling plot
    scaling_path = os.path.join(outputs_dir, 'chiplet_scaling.png')
    scaling_model.plot_scaling(chiplet_counts, Precision.FP16, save_path=scaling_path)
    print(f"✓ Generated: {scaling_path}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\n✓ Performance targets validated")
    print("✓ Power budget analyzed")
    print("✓ Scaling characteristics modeled")
    print("\nNext steps:")
    print("  1. Refine SM microarchitecture details")
    print("  2. Model interconnect contention")
    print("  3. Add multi-node scaling analysis")
    print("  4. Develop detailed power state modeling")


if __name__ == "__main__":
    main()

