# Architecture Documentation

This directory contains the complete architecture documentation for the NexGen-AI SoC.

## ⭐ FROZEN Architecture

**[ARCHITECTURE_SPEC_v1.0.md](ARCHITECTURE_SPEC_v1.0.md)** - **OFFICIAL ARCHITECTURE BASELINE**

**Status:** ✅ APPROVED - ARCHITECTURE FROZEN  
**Date:** January 2, 2026  
**Configuration:** Option C (Hybrid Approach)

This is the **frozen architecture specification**. All design work must conform to this baseline. Changes require formal Architecture Change Request (ACR) process.

### Key Frozen Parameters

- **SMs per chiplet:** 32 (FROZEN)
- **Chiplet area:** 350 mm² (FROZEN)
- **Clock frequency:** 2.3 GHz nominal (FROZEN)
- **Tensor cores per SM:** 6 (FROZEN)
- **HBM bandwidth:** 1024 GB/s (FROZEN)
- **Power budget:** 425W (FROZEN)
- **Process:** TSMC N3E (FROZEN)

## Documentation Structure

### Core Documents

1. **[ARCHITECTURE_SPEC_v1.0.md](ARCHITECTURE_SPEC_v1.0.md)** ⭐
   - Official frozen architecture baseline
   - Complete specifications
   - Change control process

2. **[overview.md](overview.md)**
   - High-level architecture overview
   - Component descriptions
   - Design principles

3. **[block_diagrams.md](block_diagrams.md)**
   - Comprehensive Mermaid diagrams
   - System-level architecture
   - Memory hierarchy
   - SM microarchitecture
   - Floorplan layouts
   - Power distribution

### Subsystem Specifications

**[subsystem_specs/](subsystem_specs/)** - Detailed subsystem specifications
- Memory subsystem
- Compute subsystem
- Interconnect subsystem
- Power management subsystem
- Test infrastructure
- Boot and reset

## Architecture Highlights

### Configuration: Option C (Hybrid)

- **Peak Performance:** 500-700 TFLOPS (FP16)
- **Compute Density:** 0.7-1.0 TFLOPS/mm²
- **Power Budget:** 425W @ 100% utilization
- **Memory Bandwidth:** 1.024 TB/s (HBM3E)
- **Competitive:** 2-3x NVIDIA H100 performance

### Chiplet Design

- **4 chiplets** per package
- **32 SMs per chiplet** (128 total)
- **350 mm² per chiplet** (1,400 mm² total)
- **UCIe mesh interconnect** (256 GB/s per link)
- **2 HBM3E stacks per chiplet** (8 total)

## Change Control

All changes to frozen parameters require:
1. Architecture Change Request (ACR) submission
2. Impact analysis (performance, power, area, schedule)
3. Architecture Review Board approval
4. Executive approval (for Class 3 changes)

See [ARCHITECTURE_SPEC_v1.0.md](ARCHITECTURE_SPEC_v1.0.md) Section "Architecture Change Control" for details.

## Related Documentation

- [Performance Analysis](../../documentation/trade_off_analyses/performance_analysis.md) - Performance modeling results
- [Stakeholder Review](../../documentation/stakeholder_review/) - Executive review materials
- [PRD](../../PRD.md) - Product Requirements Document

## Questions

For architecture questions or change requests:
- **Architecture Team Lead**
- **Architecture Review Board**
- Submit ACR via formal process

---

**Last Updated:** January 2, 2026  
**Version:** 1.0 (FROZEN)

