# NexGen-AI SoC Project Overview

**Last Updated:** January 2, 2026  
**Status:** 🟢 DUAL-TRACK STRATEGY APPROVED  
**Phase:** Execution

---

## Quick Navigation

### ⭐ Start Here
- **[DUAL_TRACK_STRATEGY_APPROVED.md](documentation/DUAL_TRACK_STRATEGY_APPROVED.md)** - Complete implementation plan
- **[Architecture Spec v1.0](architecture/ARCHITECTURE_SPEC_v1.0.md)** - Frozen v1.0 baseline
- **[Architecture Spec v2.0](architecture/ARCHITECTURE_SPEC_v2.0_RUBIN_COMPETITIVE.md)** - v2.0 Ultra specification

### 📊 Executive Materials
- **[Executive Summary](documentation/stakeholder_review/EXECUTIVE_SUMMARY.md)** - One-page summary
- **[Decision Memo](documentation/stakeholder_review/DECISION_MEMO.md)** - Executive decision
- **[Stakeholder Presentation](documentation/stakeholder_review/stakeholder_presentation.md)** - Full presentation

### 📈 Analysis & Models
- **[Performance Analysis](documentation/trade_off_analyses/performance_analysis.md)** - Technical findings
- **[Rubin Competitive Analysis](documentation/stakeholder_review/RUBIN_COMPETITIVE_ANALYSIS.md)** - v2.0 vs Rubin
- **[Performance Models](modeling/python/)** - Python analysis tools

### 📐 Architecture
- **[Block Diagrams](architecture/block_diagrams.md)** - Mermaid diagrams
- **[Architecture Overview](architecture/overview.md)** - High-level architecture

### 📋 Project Management
- **[Project Status](documentation/project_status/)** - Status reports
- **[PRD](PRD.md)** - Product requirements

---

## Project Summary

### Dual-Track Strategy

**Track 1: v1.0 "Efficiency Champion"**
- Launch: Q4 2027
- Performance: 508 TFLOPS FP16
- Power: 425W
- Price: $32,000
- Target: Tier 3 (Efficiency-focused market)

**Track 2: v2.0 "Ultra Performance Titan"**
- Launch: Q1 2028
- Performance: 5.9 PFLOPS FP16 (18% faster than Rubin Ultra)
- Power: 1,200W (67% less than Rubin)
- Price: $85,000
- Target: Tier 2 (Performance-focused market)

### Investment & Returns

**Total Investment:** $88M NRE
- v1.0: $37M
- v2.0: $27M (incremental)
- Shared: $24M

**Expected Return:** $1.88B risk-adjusted NPV (3-year)

### Timeline

| Milestone | Date |
|-----------|------|
| Architecture Freeze | ✅ Jan 2, 2026 |
| v1.0 RTL Freeze | Q2 2026 |
| v1.0 Tapeout | Q4 2026 |
| v1.0 Launch | Q4 2027 |
| v2.0 Tapeout | Q1 2027 |
| v2.0 Launch | Q1 2028 |

---

## Key Decisions Made

1. ✅ **Architecture Target Revision** (Jan 2, 2026)
   - From: 2.0 TFLOPS/mm² (impossible)
   - To: 0.7-1.0 TFLOPS/mm² (realistic)

2. ✅ **Option C Approved** (Jan 2, 2026)
   - v1.0 architecture frozen
   - 508 TFLOPS FP16, 425W power

3. ✅ **Dual-Track Strategy Approved** (Jan 2, 2026)
   - v1.0 + v2.0 parallel development
   - $88M investment authorized

---

## Competitive Position

**v1.0 vs Market:**
- 2-3x NVIDIA H100 performance
- 40% lower power than H100
- Competitive with AMD MI300X
- Superior to Intel Gaudi 3

**v2.0 vs Market:**
- 18% faster FP16 than NVIDIA Rubin Ultra
- 67% less power than Rubin Ultra
- 38% lower TCO than Rubin Ultra
- 7x faster than H100

---

## Team & Resources

**Current:** 30 engineers  
**Target (Q2 2026):** 165 engineers

**Budget:** $88M NRE over 24 months

---

## Project Health

**Overall Status:** 🟢 **GREEN**

| Metric | Status |
|--------|--------|
| Schedule | 🟢 On Track |
| Budget | 🟢 On Track |
| Technical Risk | 🟡 Medium (acceptable) |
| Team Staffing | 🟡 Ramping |
| Strategic Position | 🟢 Strong |

---

## Next Steps

**This Week:**
- Distribute dual-track approval
- All-hands announcement
- Begin v2.0 recruiting
- TSMC capacity reservation

**Q1 2026:**
- Team ramp to 80 engineers
- v1.0 RTL development
- v2.0 architecture kickoff

---

**For detailed information, see the documents linked above.**

**Questions?** Contact Architecture Team  
**Status Updates:** See [project_status/](documentation/project_status/)

---

*Project: NexGen-AI SoC*  
*Status: Dual-Track Strategy Approved ✅*

