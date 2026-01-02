# NexGen-AI SoC Architecture Specification v1.0
## ARCHITECTURE FREEZE - Option C (Hybrid) Configuration

**Status:** ✅ APPROVED - ARCHITECTURE FROZEN  
**Date:** January 2, 2026  
**Approval:** Executive Leadership  
**Effective:** Immediately  

---

## Document Control

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 1.0 | Jan 2, 2026 | Architecture Team | Initial freeze - Option C approved |

**Distribution:** Architecture, Design, Verification, Physical Design, Software, Program Management

---

## Executive Summary

This document defines the frozen architecture baseline for the NexGen-AI SoC, a chiplet-based AI accelerator targeting hyperscale training and inference workloads. The architecture delivers **2-3x NVIDIA H100 performance** at **lower power** with manageable technical risk.

**Key Specifications:**
- **Peak Performance:** 500-700 TFLOPS (FP16)
- **Compute Density:** 0.7-1.0 TFLOPS/mm²
- **Power Budget:** 425W @ 100% utilization
- **Memory Bandwidth:** 1.024 TB/s (HBM3E)
- **Process Technology:** TSMC 3nm (N3E)
- **Target Launch:** Q4 2027

---

## Architecture Overview

### Chiplet-Based Design

```
┌─────────────────────────────────────────────────────────────┐
│                    NexGen-AI SoC Package                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Chiplet 0   │  │  Chiplet 1   │  │   HBM3E      │      │
│  │  32 SMs      │──│  32 SMs      │──│  Stacks 0-1  │      │
│  │  350 mm²     │  │  350 mm²     │  │  256 GB/s    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
│         │                  │                                  │
│         └──────────┬───────┘           ┌──────────────┐      │
│                    │                   │   HBM3E      │      │
│  ┌──────────────┐ │ ┌──────────────┐  │  Stacks 2-3  │      │
│  │  Chiplet 2   │─┼─│  Chiplet 3   │──│  256 GB/s    │      │
│  │  32 SMs      │ │ │  32 SMs      │  └──────────────┘      │
│  │  350 mm²     │ │ │  350 mm²     │                         │
│  └──────────────┘ │ └──────┬───────┘  ┌──────────────┐      │
│         │          │        │          │   HBM3E      │      │
│         │          │        └──────────│  Stacks 4-5  │      │
│         │          │                   │  256 GB/s    │      │
│         └──────────┼───────────────────┘              │      │
│                    │        ┌──────────────┐          │      │
│                    │        │   HBM3E      │          │      │
│                    └────────│  Stacks 6-7  │──────────┘      │
│                             │  256 GB/s    │                 │
│                             └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
         UCIe Mesh Interconnect (256 GB/s per link)
```

### Top-Level Specifications

| Parameter | Specification | Notes |
|-----------|--------------|-------|
| **Total Chiplets** | 4 | Scalable to 2, 6, 8 in future SKUs |
| **SMs per Chiplet** | 32 | **FROZEN** |
| **Total SMs** | 128 | 64 GPC clusters total |
| **Process Node** | TSMC 3nm (N3E) | Standard design rules |
| **Chiplet Die Size** | 350 mm² | **FROZEN** |
| **Total Silicon Area** | 1,400 mm² | Excluding HBM |
| **Package Size** | ~50mm × 50mm | With interposer |

---

## Compute Architecture - FROZEN

### Streaming Multiprocessor (SM) Configuration

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **CUDA Cores** | 128 per SM | Standard |
| **Tensor Cores** | 6 per SM | 1.5x baseline for AI workloads |
| **Clock Frequency** | 2.3 GHz (nominal) | Conservative for yields |
| **Clock Bins** | 2.2 / 2.3 / 2.4 GHz | Binning strategy for yields |
| **Register File** | 256 KB per SM | 65,536 × 32-bit registers |
| **Shared Memory** | 128 KB per SM | Configurable with L1 |
| **L1 Data Cache** | 128 KB per SM | Shared with SMEM pool |
| **Max Threads/SM** | 2,048 | 64 warps × 32 threads |

### Tensor Core Specifications

| Precision | Ops/Cycle per Core | Total Ops/SM/Cycle | Notes |
|-----------|-------------------|-------------------|-------|
| **FP4** | 192 | 1,152 | Sparse/quantized inference |
| **FP8** | 96 | 576 | Training and inference |
| **INT8** | 96 | 576 | Integer inference |
| **FP16** | 48 | 288 | **PRIMARY TARGET** |
| **BF16** | 48 | 288 | Training precision |
| **TF32** | 32 | 192 | TensorFlow compatible |
| **FP32** | 24 | 144 | General purpose |

### Performance Targets - FROZEN

| Metric | Target | Tolerance | Measured As |
|--------|--------|-----------|-------------|
| **Peak FP16 (4 chiplets)** | 508 TFLOPS | ±10% | Synthetic benchmark |
| **Peak FP8 (4 chiplets)** | 1,017 TFLOPS | ±10% | Synthetic benchmark |
| **Compute Density** | 0.73 TFLOPS/mm² | ±15% | Peak FP16 / Total Area |
| **Sustained Performance** | 100-150 TFLOPS | N/A | Real workloads (20-30% peak) |

**Competitive Positioning:**
- 2.0x NVIDIA H100 (FP16)
- 2.5x AMD MI300X (FP16)
- 3.0x Intel Gaudi 3 (FP16)

---

## Memory Hierarchy - FROZEN

### Cache Architecture

| Level | Size | Associativity | Latency | Bandwidth | Scope |
|-------|------|---------------|---------|-----------|-------|
| **Register File** | 256 KB/SM | N/A | 1 cycle | ~10 TB/s | Per SM |
| **Shared Memory** | 128 KB/SM | N/A | 1-2 cycles | ~8 TB/s | Per SM |
| **L1 Data Cache** | 128 KB/SM | 4-way | 1-2 cycles | ~6 TB/s | Per SM |
| **Constant Cache** | 64 KB/SM | 2-way | 10 cycles | N/A | Per SM |
| **Texture Cache** | 48 KB/SM | 4-way | 10 cycles | N/A | Per SM |
| **Instruction Cache** | 32 KB/SM | 2-way | 5 cycles | N/A | Per SM |
| **L2 Cache** | 8 MB/chiplet | 16-way | 30-50 cycles | ~2 TB/s | Per chiplet |
| **L2 Total** | 32 MB | - | - | - | SoC-wide |

**L1/Shared Memory Configuration:**
- Configurable split: 128KB/0KB, 96KB/32KB, 64KB/64KB, 32KB/96KB, 0KB/128KB
- Software-managed via kernel launch parameters

### HBM3E Subsystem - FROZEN

| Parameter | Specification | Notes |
|-----------|--------------|-------|
| **Total Stacks** | 8 | 2 per chiplet |
| **Capacity per Stack** | 8 GB or 16 GB | Two SKU options |
| **Total Capacity** | 64 GB or 128 GB | Standard / High-mem |
| **Bandwidth per Stack** | 128 GB/s | HBM3E standard |
| **Total Bandwidth** | 1,024 GB/s (1.024 TB/s) | **FROZEN** |
| **Memory Clock** | 1.2 GHz | HBM3E spec |
| **Bus Width per Stack** | 1024-bit | 8 channels × 128-bit |
| **ECC** | Inline (On-die) | +12.5% overhead |

**Memory Controllers:**
- 8 independent memory controllers (1 per stack)
- Address interleaving for load balancing
- DRAM refresh handled transparently
- Power management (self-refresh, low-power modes)

### Memory Bandwidth Analysis

**Ridge Point:** 3,974 FLOPS/Byte (where memory becomes bottleneck)

**Workload Performance:**
| Workload | Arithmetic Intensity | Achieved % | Bottleneck |
|----------|---------------------|------------|------------|
| Dense GEMM (optimized) | 100 FLOPS/Byte | 20-25% | Memory |
| Sparse GEMM | 50 FLOPS/Byte | 10-15% | Memory |
| Attention (FlashAttention) | 50 FLOPS/Byte | 10-15% | Memory |
| Attention (naive) | 10 FLOPS/Byte | 2-5% | Memory |
| Elementwise ops | 0.5 FLOPS/Byte | <1% | Memory |
| Convolution (optimized) | 80 FLOPS/Byte | 15-20% | Memory |

**Implications:**
- Most workloads memory-bound (not compute-bound)
- Real-world performance: 100-150 TFLOPS sustained
- Software optimization critical (kernel fusion, FlashAttention)
- This is **industry-wide issue** (H100 similar)

---

## Interconnect Architecture - FROZEN

### UCIe (Universal Chiplet Interconnect Express)

| Parameter | Specification | Notes |
|-----------|--------------|-------|
| **Standard** | UCIe 1.0 | Industry standard |
| **Topology** | 2D Mesh | All chiplets connected |
| **Links per Chiplet** | 4 (N/S/E/W) | Bidirectional |
| **Bandwidth per Link** | 256 GB/s | 128 GB/s each direction |
| **Total UCIe BW** | 1,024 GB/s | Aggregate internal |
| **Latency** | 10-20 ns | Chiplet-to-chiplet |
| **Protocol** | PCIe 6.0 based | With extensions |
| **Cache Coherency** | Supported | NVLink-C2C inspired |

**Mesh Topology:**
```
Chiplet 0 ←→ Chiplet 1
    ↑ ↘         ↑ ↘
    ↓   ↘       ↓   ↘
Chiplet 2 ←→ Chiplet 3
```

**Routing:**
- Dimension-ordered routing (X-Y)
- Deadlock-free by design
- Load balancing across links
- Packet-based (64B flits)

### NVLink 4.0 (Multi-GPU)

| Parameter | Specification | Notes |
|-----------|--------------|-------|
| **Links per SoC** | 6 | External GPU connections |
| **Bandwidth per Link** | 100 GB/s | Bidirectional |
| **Total NVLink BW** | 600 GB/s | Multi-GPU scaling |
| **Supported Topologies** | All-to-all, ring, tree | Software configurable |
| **Max GPUs** | 16 | In single fabric |

### PCIe 6.0 (Host Interface)

| Parameter | Specification | Notes |
|-----------|--------------|-------|
| **Generation** | PCIe 6.0 | Latest standard |
| **Lanes** | x16 | Standard slot |
| **Bandwidth** | 128 GB/s | 64 GB/s each direction |
| **PAM4 Encoding** | Yes | PCIe 6.0 feature |
| **Topology** | Root complex to CPU | Host connection |

---

## Power Architecture - FROZEN

### Power Budget Breakdown

| Component | Power @ 100% | Percentage | Power @ 75% |
|-----------|-------------|------------|-------------|
| **SM Arrays (128 total)** | 240 W | 66% | 185 W |
| **L2 Caches (32 MB)** | 13 W | 3.6% | 11 W |
| **HBM3E (8 stacks)** | 60 W | 16.5% | 48 W |
| **HBM Controllers** | 16 W | 4.4% | 13 W |
| **UCIe Interconnect** | 12 W | 3.3% | 10 W |
| **NVLink + PCIe** | 10 W | 2.7% | 8 W |
| **Static (Leakage)** | 13 W | 3.6% | 13 W |
| **TOTAL** | **364 W** | **100%** | **288 W** |

**Target Verification:**
- ✅ 364W < 500W budget (27% margin)
- Comfortable thermal headroom
- Standard air cooling sufficient

### Power Management Features - FROZEN

**Dynamic Voltage and Frequency Scaling (DVFS):**
- Per-chiplet frequency control
- Per-SM cluster clock gating
- Voltage domains: Core, HBM, I/O, Aux
- Frequency bins: 1.8, 2.0, 2.2, 2.3, 2.4 GHz

**Power States:**
| State | Description | Power | Entry/Exit Latency |
|-------|-------------|-------|-------------------|
| **P0** | Max performance | 364 W | N/A |
| **P1** | Nominal | 290 W | <1 µs |
| **P2** | Power save | 180 W | <10 µs |
| **P3** | Idle | 50 W | <100 µs |
| **P4** | Deep sleep | 15 W | <1 ms |

**Clock Gating:**
- Hierarchical: SoC → Chiplet → GPC → SM → Unit
- Automatic (hardware) and manual (software)
- Fine-grained per functional unit

**Power Monitoring:**
- Per-chiplet current sensors
- Temperature sensors (per chiplet, per HBM stack)
- Over-current, over-voltage, over-temperature protection
- Telemetry via I²C interface

### Thermal Specifications - FROZEN

| Parameter | Value | Notes |
|-----------|-------|-------|
| **TDP** | 425 W | Thermal Design Power |
| **Max Junction Temp** | 95°C | Absolute maximum |
| **Nominal Junction Temp** | 65-75°C | Typical operation |
| **Ambient Temp (max)** | 35°C | Data center spec |
| **Cooling Solution** | Air (forced convection) | Standard heatsink + fan |
| **Θ_JA (thermal resistance)** | 0.12 °C/W | With production cooling |

---

## Physical Design Constraints - FROZEN

### Die Floorplan Guidelines

**Per-Chiplet Layout (350 mm²):**
```
┌─────────────────────────────────────┐
│ [North Edge: UCIe PHY, NVLink PHY]  │
├──────────┬──────────────┬───────────┤
│ SM 0-7   │  L2 Cache    │  SM 8-15  │
│ (NW)     │  4 MB North  │  (NE)     │
├──────────┼──────────────┼───────────┤
│ HBM Ctrl │   Crossbar   │  HBM Ctrl │
│ West     │  Interconnect│  East     │
├──────────┼──────────────┼───────────┤
│ SM 16-23 │  L2 Cache    │  SM 24-31 │
│ (SW)     │  4 MB South  │  (SE)     │
├──────────┴──────────────┴───────────┤
│ [South Edge: UCIe PHY, PMU, Debug]  │
└─────────────────────────────────────┘
```

**Area Breakdown:**
- SM arrays: 60% (210 mm²)
- L2 cache: 15% (52 mm²)
- Crossbar/routing: 10% (35 mm²)
- HBM controllers + PHY: 8% (28 mm²)
- UCIe/NVLink/PCIe PHY: 5% (17.5 mm²)
- PMU/Debug/Misc: 2% (7 mm²)

### Package Specifications - FROZEN

| Parameter | Specification | Notes |
|-----------|--------------|-------|
| **Package Type** | 2.5D (Interposer) | Silicon interposer |
| **Package Size** | 50mm × 50mm | Approximate |
| **Interposer Material** | Silicon | Passive, routing only |
| **Bump Pitch** | 40 µm (micro-bumps) | Chiplet-to-interposer |
| **C4 Bump Pitch** | 150 µm | Package-to-substrate |
| **Total I/O Bumps** | ~10,000 | Power + signal |

---

## Software & Programming Model - FROZEN

### Compute API

**Primary:** CUDA-compatible (source-level)
- Target: 95%+ existing CUDA code compatibility
- Runtime: Custom (NexGen runtime)
- Driver: Linux kernel module

**Secondary:** ROCm/HIP support (future)

### Memory Model

**Unified Memory:**
- CPU and GPU share address space
- Automatic migration (demand paging)
- Coherency maintained by hardware

**Explicit Memory:**
- cudaMalloc, cudaMemcpy semantics
- Host-to-device, device-to-host
- Peer-to-peer (GPU-to-GPU)

### Precision Support

| Type | Supported | Performance | Use Case |
|------|-----------|-------------|----------|
| **FP4** | ✅ | 2048 TOPS | Quantized inference |
| **FP8** | ✅ | 1017 TFLOPS | Training + inference |
| **INT8** | ✅ | 1017 TOPS | Integer inference |
| **FP16** | ✅ | 508 TFLOPS | **PRIMARY** |
| **BF16** | ✅ | 508 TFLOPS | Training |
| **TF32** | ✅ | 339 TFLOPS | TensorFlow |
| **FP32** | ✅ | 169 TFLOPS | General purpose |
| **FP64** | ❌ | N/A | Not supported |

---

## Verification & Validation Requirements

### Functional Verification

**Coverage Goals:**
- Code coverage: 100% (RTL)
- Functional coverage: 95%
- Cross-coverage: 90%
- Assertion coverage: 100%

**Testbenches:**
- Unit-level (per module)
- Cluster-level (SM, GPC)
- Chiplet-level (full chiplet)
- SoC-level (4 chiplets + HBM)

### Performance Validation

**Benchmarks (Required):**
- MLPerf Training v4.0 (all models)
- MLPerf Inference v4.0 (all models)
- SPEC CPU2017 (reference)
- Custom microbenchmarks (GEMM, attention, etc.)

**Targets:**
- MLPerf Training: Top 3 across all models
- MLPerf Inference: Top 3 across all scenarios
- Sustained performance: >20% of peak

### Power Validation

**Measurements:**
- Per-chiplet power sensors
- Per-HBM-stack power sensors
- Total package power @ wall
- Power efficiency (TFLOPS/W)

**Compliance:**
- TDP ≤ 425W (required)
- Idle power < 50W (target)
- Power ramp rate < 100W/s (safety)

---

## Manufacturing & Test Strategy

### Wafer-Level Testing

**Test Coverage:**
- Electrical: shorts, opens, parametrics
- Functional: BIST (Built-In Self-Test)
- Memory: MBIST (Memory BIST)
- At-speed: 80% of target frequency

**Yield Targets:**
- Wafer yield: >70% (aggressive but achievable)
- Known-good-die (KGD): >90% (after test)
- Package yield: >95%

**Redundancy:**
- Each chiplet: 32 SMs (30 required, 2 spare)
- Laser fuse programming for disable

### Package-Level Testing

**Tests:**
- Chiplet-to-chiplet connectivity (UCIe)
- HBM interface (1024 GB/s BW verification)
- PCIe/NVLink interfaces
- Full system boot and POST

**Binning Strategy:**
| Bin | Clock | SMs | Power | Price Premium |
|-----|-------|-----|-------|---------------|
| **Ultra** | 2.4 GHz | 128 | 400W | +20% |
| **Performance** | 2.3 GHz | 128 | 425W | Baseline |
| **Standard** | 2.2 GHz | 120-128 | 450W | -15% |
| **Value** | 2.0 GHz | 112-120 | 400W | -30% |

---

## Product Roadmap & SKUs

### Launch SKUs (Q4 2027)

| SKU | Chiplets | SMs | HBM | TFLOPS | Power | Price |
|-----|----------|-----|-----|--------|-------|-------|
| **NexGen-AI 128** | 4 | 128 | 128 GB | 508 | 425W | $32,000 |
| **NexGen-AI 128 Lite** | 4 | 128 | 64 GB | 508 | 425W | $28,000 |

### Future SKUs (2028+)

| SKU | Chiplets | SMs | TFLOPS | Target Market |
|-----|----------|-----|--------|---------------|
| **NexGen-AI 64** | 2 | 64 | 254 | Inference, edge servers |
| **NexGen-AI 192** | 6 | 192 | 763 | Large-scale training |
| **NexGen-AI 256** | 8 | 256 | 1017 | Supercomputing |

### Next Generation (2029 - "NexGen-AI 2")

**Process:** TSMC 2nm  
**Target Density:** 1.2-1.5 TFLOPS/mm²  
**Architecture:** Refined Option C (48 SMs/chiplet)

---

## Risk Register & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Clock target miss (2.3 GHz) | 15% | Medium | Frequency binning (2.2/2.3/2.4) |
| Yield below 70% | 20% | Medium | Redundant SMs, conservative design |
| Power exceeds 500W | 25% | Low | 27% margin, aggressive gating |
| HBM supply shortage | 30% | Medium | Dual-source (SK Hynix + Samsung) |
| UCIe interop issues | 10% | High | Early silicon validation |
| Schedule slip (>2 months) | 20% | Medium | Critical path management |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| NVIDIA B100 launch before us | 40% | High | Focus on power efficiency, TCO |
| Price pressure | 50% | Medium | Value SKUs, volume discounts |
| Customer acceptance | 30% | High | Early access program, sampling |
| Supply chain issues | 40% | Medium | Strategic inventory, dual-source |

---

## Dependencies & Assumptions

### Critical Dependencies

**TSMC:**
- N3E process availability (Q1 2026)
- Wafer allocation (15 wafers/month by Q4 2026)
- Design rule manual (final by Q2 2026)

**HBM Suppliers:**
- HBM3E production (SK Hynix/Samsung)
- Pricing locked ($250/stack target)
- Long-lead items (order by Q2 2026)

**EDA Tools:**
- Synopsys VCS (simulation)
- Cadence Innovus (P&R)
- Mentor Calibre (signoff)

### Key Assumptions

**Technical:**
- TSMC N3E yields >70% by Q4 2026
- UCIe 1.0 standard stable
- HBM3E meets 128 GB/s per stack

**Business:**
- Market demand >10,000 units/year by 2028
- ASP ~$30,000 sustainable
- Competition pricing stable ($28-40k)

**Schedule:**
- No major COVID-style disruptions
- Team fully staffed by Q2 2026
- No >1 month tool delays

---

## Architecture Change Control

### Change Classification

**Class 1: No Impact** (approved by Architecture Lead)
- Documentation clarifications
- Non-functional changes
- Performance optimizations (within spec)

**Class 2: Minor Impact** (approved by Architecture Review Board)
- <5% performance impact
- <5% power impact
- <2% area impact
- Schedule impact <1 month

**Class 3: Major Impact** (requires Executive approval)
- >5% performance, power, or area impact
- Any change to frozen parameters
- Schedule impact >1 month
- Cost impact >$1M

### Frozen Parameters (No Changes Without Executive Approval)

- ✅ SMs per chiplet: **32**
- ✅ Chiplet area: **350 mm²**
- ✅ Clock frequency: **2.3 GHz nominal**
- ✅ Tensor cores per SM: **6**
- ✅ HBM bandwidth: **1024 GB/s**
- ✅ Power budget: **425W**
- ✅ Process: **TSMC N3E**

---

## Next Steps & Timeline

### Immediate (January 2026)

- [x] Architecture freeze approved - **COMPLETE**
- [ ] PRD update with new targets - **Due: Jan 13**
- [ ] All-hands announcement - **Due: Jan 15**
- [ ] TSMC engagement kickoff - **Due: Jan 20**
- [ ] HBM supplier negotiations - **Due: Jan 31**

### Q1 2026

- [ ] Detailed SM microarchitecture design
- [ ] L2 cache design
- [ ] Crossbar interconnect design
- [ ] UCIe PHY integration
- [ ] Verification environment setup

### Q2 2026

- [ ] RTL freeze (SM, L2, interconnect)
- [ ] Synthesis and timing analysis
- [ ] Power analysis (detailed)
- [ ] Floorplanning

### Q3-Q4 2026

- [ ] Physical design
- [ ] DRC/LVS/timing signoff
- [ ] Tape-out preparation
- [ ] **Tape-out #1: Q4 2026**

### 2027

- [ ] Silicon bring-up (Q1)
- [ ] Debug and characterization (Q2)
- [ ] Tape-out #2 if needed (Q2)
- [ ] Production ramp (Q3)
- [ ] **Customer shipments: Q4 2027**

---

## Approvals

This architecture specification has been reviewed and approved by:

**Architecture Team Lead:** _________________ Date: _________

**Design Engineering VP:** _________________ Date: _________

**Verification Lead:** _________________ Date: _________

**Physical Design Lead:** _________________ Date: _________

**Program Manager:** _________________ Date: _________

**CTO:** _________________ Date: _________

---

## Document End

**This architecture is now FROZEN. All future changes require formal change control process.**

**Questions or clarifications:** Contact Architecture Team  
**Change requests:** Submit via Architecture Change Request (ACR) process

**Next architecture review:** Q2 2026 (post-RTL freeze)

---

*CONFIDENTIAL AND PROPRIETARY - NexGen AI Corporation*  
*Do not distribute outside approved personnel*

