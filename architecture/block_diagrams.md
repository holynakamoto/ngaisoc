# NexGen-AI SoC Block Diagrams

This document contains comprehensive block diagrams for the NexGen-AI SoC architecture using Mermaid notation.

## Table of Contents
1. [Chiplet Interconnect Topology](#chiplet-interconnect-topology)
2. [System-Level Architecture](#system-level-architecture)
3. [Memory Hierarchy](#memory-hierarchy)
4. [SM (Streaming Multiprocessor) Microarchitecture](#sm-microarchitecture)
5. [Floorplan Conceptual Layout](#floorplan-conceptual-layout)
6. [Power Distribution Network](#power-distribution-network)

---

## Chiplet Interconnect Topology

### 4-Chiplet Configuration with UCIe and NVLink

```mermaid
graph TB
    subgraph Package["NexGen-AI SoC Package (4 Chiplets)"]
        subgraph C0["Chiplet 0"]
            SM0_0["16x SMs"]
            L2_0["L2 Cache<br/>6 MB"]
            UCIe0["UCIe PHY"]
            NVL0["NVLink 4.0<br/>6 Links"]
            HBM0["HBM3E Ctrl<br/>2 Stacks"]
        end
        
        subgraph C1["Chiplet 1"]
            SM1_0["16x SMs"]
            L2_1["L2 Cache<br/>6 MB"]
            UCIe1["UCIe PHY"]
            NVL1["NVLink 4.0<br/>6 Links"]
            HBM1["HBM3E Ctrl<br/>2 Stacks"]
        end
        
        subgraph C2["Chiplet 2"]
            SM2_0["16x SMs"]
            L2_2["L2 Cache<br/>6 MB"]
            UCIe2["UCIe PHY"]
            NVL2["NVLink 4.0<br/>6 Links"]
            HBM2["HBM3E Ctrl<br/>2 Stacks"]
        end
        
        subgraph C3["Chiplet 3"]
            SM3_0["16x SMs"]
            L2_3["L2 Cache<br/>6 MB"]
            UCIe3["UCIe PHY"]
            NVL3["NVLink 4.0<br/>6 Links"]
            HBM3["HBM3E Ctrl<br/>2 Stacks"]
            PCIe["PCIe 6.0 x16"]
        end
        
        %% UCIe Interconnect (Mesh Topology)
        UCIe0 <-->|"256 GB/s"| UCIe1
        UCIe1 <-->|"256 GB/s"| UCIe3
        UCIe3 <-->|"256 GB/s"| UCIe2
        UCIe2 <-->|"256 GB/s"| UCIe0
        UCIe0 <-->|"256 GB/s"| UCIe3
        UCIe1 <-->|"256 GB/s"| UCIe2
        
        %% HBM Connections
        SM0_0 -.->|"Memory"| HBM0
        SM1_0 -.->|"Memory"| HBM1
        SM2_0 -.->|"Memory"| HBM2
        SM3_0 -.->|"Memory"| HBM3
    end
    
    %% External NVLink (Multi-GPU)
    NVL0 & NVL1 & NVL2 & NVL3 ==>|"600 GB/s<br/>External"| EXT_GPU["External GPUs"]
    
    %% PCIe Host Connection
    PCIe ==>|"128 GB/s"| HOST["Host CPU<br/>PCIe 6.0"]
    
    %% HBM3E Memory
    HBM0 -.->|"256 GB/s"| MEM0["HBM3E<br/>Stack 0-1"]
    HBM1 -.->|"256 GB/s"| MEM1["HBM3E<br/>Stack 2-3"]
    HBM2 -.->|"256 GB/s"| MEM2["HBM3E<br/>Stack 4-5"]
    HBM3 -.->|"256 GB/s"| MEM3["HBM3E<br/>Stack 6-7"]
    
    style Package fill:#f0f0f0,stroke:#333,stroke-width:3px
    style C0 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style C1 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style C2 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style C3 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style HOST fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style EXT_GPU fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**Key Features:**
- **Mesh topology** for low-latency chiplet-to-chiplet communication
- **UCIe standard** for die-to-die interconnect (256 GB/s per link)
- **Distributed HBM3E** - 2 stacks per chiplet for balanced bandwidth
- **Chiplet 3** includes PCIe controller for host interface
- **NVLink 4.0** for multi-GPU scaling (600 GB/s aggregate external)

---

## System-Level Architecture

### Complete SoC System Block Diagram

```mermaid
graph TB
    subgraph HOST["Host System"]
        CPU["CPU<br/>x86/ARM"]
        SYS_MEM["System Memory<br/>DDR5"]
        STORAGE["NVMe Storage"]
    end
    
    subgraph SOC["NexGen-AI SoC"]
        subgraph COMPUTE["Compute Complex"]
            direction TB
            GPC0["GPC 0<br/>16 SMs"]
            GPC1["GPC 1<br/>16 SMs"]
            GPC2["GPC 2<br/>16 SMs"]
            GPC3["GPC 3<br/>16 SMs"]
        end
        
        subgraph MEMORY["Memory Subsystem"]
            L2["L2 Cache<br/>24 MB Total<br/>(6MB per GPC)"]
            HBM_CTRL["HBM3E Controllers<br/>8x Controllers"]
            TLB["TLB & MMU"]
        end
        
        subgraph INTERCONNECT["Interconnect Fabric"]
            XBAR["Crossbar Switch"]
            COHERENCE["Cache Coherency<br/>Protocol Engine"]
            ATOMIC["Atomic Unit"]
        end
        
        subgraph IO["I/O & Interface"]
            PCIE_CTRL["PCIe 6.0 Controller<br/>x16 (128 GB/s)"]
            NVLINK_CTRL["NVLink 4.0 Controller<br/>6 Links (600 GB/s)"]
            DMA["DMA Engines<br/>Copy & Fill"]
        end
        
        subgraph CONTROL["Control & Management"]
            SCHEDULER["Global Scheduler<br/>& Dispatcher"]
            PMU["Power Management<br/>Unit (PMU)"]
            SEC["Security Engine<br/>AES, PKI"]
            DEBUG["Debug & Trace"]
            FUSE["eFuse & Config"]
        end
        
        %% Compute to Memory
        GPC0 & GPC1 & GPC2 & GPC3 --> L2
        L2 <--> XBAR
        XBAR <--> HBM_CTRL
        XBAR <--> COHERENCE
        XBAR <--> TLB
        
        %% Interconnect relationships
        COHERENCE <--> L2
        ATOMIC <--> XBAR
        
        %% I/O connections
        XBAR <--> DMA
        DMA <--> PCIE_CTRL
        DMA <--> NVLINK_CTRL
        
        %% Control plane
        SCHEDULER --> GPC0 & GPC1 & GPC2 & GPC3
        PMU -.->|"Power Ctrl"| GPC0 & GPC1 & GPC2 & GPC3
        PMU -.->|"Power Ctrl"| HBM_CTRL
        DEBUG -.->|"Monitor"| XBAR
        SEC <--> XBAR
        FUSE -.->|"Config"| PMU
    end
    
    %% External Memory
    HBM_CTRL <--> HBM["HBM3E Memory<br/>8 Stacks<br/>1024 GB/s<br/>64-128 GB"]
    
    %% Host connections
    CPU <--> PCIE_CTRL
    CPU <--> SYS_MEM
    STORAGE <--> CPU
    
    %% Multi-GPU
    NVLINK_CTRL <--> GPU1["GPU 1"]
    NVLINK_CTRL <--> GPU2["GPU 2"]
    NVLINK_CTRL <--> GPU3["GPU 3"]
    
    style SOC fill:#e8f5e9,stroke:#2e7d32,stroke-width:4px
    style COMPUTE fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style MEMORY fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style INTERCONNECT fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style IO fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style CONTROL fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    style HOST fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    style HBM fill:#ffebee,stroke:#c62828,stroke-width:2px
```

**Architecture Highlights:**
- **4 GPCs (Graphics Processing Clusters)** - Each containing 16 SMs
- **Hierarchical memory** - L1 (per-SM) → L2 (shared) → HBM3E
- **Crossbar interconnect** for non-blocking access patterns
- **Hardware coherency** across all compute units
- **Dedicated DMA engines** for efficient data movement
- **Comprehensive control plane** with power, security, and debug

---

## Memory Hierarchy

### Detailed Memory Subsystem Architecture

```mermaid
graph TB
    subgraph COMPUTE["Compute Units"]
        direction LR
        subgraph SM0["SM 0"]
            TC0["Tensor Cores<br/>4x Units"]
            CC0["CUDA Cores<br/>128x FP32"]
            RF0["Register File<br/>256 KB"]
            L1_0["L1 Cache<br/>128 KB"]
            SMEM0["Shared Mem<br/>128 KB"]
        end
        
        subgraph SM1["SM 1"]
            TC1["Tensor Cores<br/>4x Units"]
            CC1["CUDA Cores<br/>128x FP32"]
            RF1["Register File<br/>256 KB"]
            L1_1["L1 Cache<br/>128 KB"]
            SMEM1["Shared Mem<br/>128 KB"]
        end
        
        subgraph SM_N["SM 15"]
            TC_N["Tensor Cores<br/>4x Units"]
            CC_N["CUDA Cores<br/>128x FP32"]
            RF_N["Register File<br/>256 KB"]
            L1_N["L1 Cache<br/>128 KB"]
            SMEM_N["Shared Mem<br/>128 KB"]
        end
        
        TC0 & CC0 --> RF0
        RF0 --> L1_0
        RF0 --> SMEM0
        
        TC1 & CC1 --> RF1
        RF1 --> L1_1
        RF1 --> SMEM1
        
        TC_N & CC_N --> RF_N
        RF_N --> L1_N
        RF_N --> SMEM_N
    end
    
    subgraph L2_SYSTEM["L2 Cache System"]
        direction LR
        L2_SLICE0["L2 Slice 0<br/>1.5 MB"]
        L2_SLICE1["L2 Slice 1<br/>1.5 MB"]
        L2_SLICE2["L2 Slice 2<br/>1.5 MB"]
        L2_SLICE3["L2 Slice 3<br/>1.5 MB"]
    end
    
    subgraph MEM_CTRL["Memory Controllers"]
        direction LR
        MC0["HBM Ctrl 0<br/>128 GB/s"]
        MC1["HBM Ctrl 1<br/>128 GB/s"]
        MC2["HBM Ctrl 2<br/>128 GB/s"]
        MC3["HBM Ctrl 3<br/>128 GB/s"]
        MC4["HBM Ctrl 4<br/>128 GB/s"]
        MC5["HBM Ctrl 5<br/>128 GB/s"]
        MC6["HBM Ctrl 6<br/>128 GB/s"]
        MC7["HBM Ctrl 7<br/>128 GB/s"]
    end
    
    subgraph PHYSICAL_MEM["Physical Memory"]
        direction LR
        HBM0["Stack 0<br/>8-16 GB"]
        HBM1["Stack 1<br/>8-16 GB"]
        HBM2["Stack 2<br/>8-16 GB"]
        HBM3["Stack 3<br/>8-16 GB"]
        HBM4["Stack 4<br/>8-16 GB"]
        HBM5["Stack 5<br/>8-16 GB"]
        HBM6["Stack 6<br/>8-16 GB"]
        HBM7["Stack 7<br/>8-16 GB"]
    end
    
    subgraph MMU_TLB["Address Translation"]
        TLB_L1["L1 TLB<br/>Per SM"]
        TLB_L2["L2 TLB<br/>Shared"]
        PAGE_TABLE["Page Table<br/>Walker"]
    end
    
    %% Memory hierarchy flow
    L1_0 & L1_1 & L1_N --> L2_SLICE0
    L1_0 & L1_1 & L1_N --> L2_SLICE1
    L1_0 & L1_1 & L1_N --> L2_SLICE2
    L1_0 & L1_1 & L1_N --> L2_SLICE3
    
    L2_SLICE0 --> MC0 & MC1
    L2_SLICE1 --> MC2 & MC3
    L2_SLICE2 --> MC4 & MC5
    L2_SLICE3 --> MC6 & MC7
    
    MC0 --> HBM0
    MC1 --> HBM1
    MC2 --> HBM2
    MC3 --> HBM3
    MC4 --> HBM4
    MC5 --> HBM5
    MC6 --> HBM6
    MC7 --> HBM7
    
    %% Address translation
    L1_0 & L1_1 & L1_N -.->|"VA"| TLB_L1
    TLB_L1 -.->|"Miss"| TLB_L2
    TLB_L2 -.->|"Miss"| PAGE_TABLE
    PAGE_TABLE -.->|"PA"| MC0 & MC1 & MC2 & MC3
    
    %% Annotations
    LATENCY0["L1: 1-2 cycles<br/>28-56 ns @ 2GHz"]
    LATENCY1["L2: 20-40 cycles<br/>10-20 ns"]
    LATENCY2["HBM: 200-300 cycles<br/>100-150 ns"]
    
    L1_0 -.->|"Latency"| LATENCY0
    L2_SLICE0 -.->|"Latency"| LATENCY1
    HBM0 -.->|"Latency"| LATENCY2
    
    style COMPUTE fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style L2_SYSTEM fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style MEM_CTRL fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style PHYSICAL_MEM fill:#ffebee,stroke:#c62828,stroke-width:2px
    style MMU_TLB fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
```

**Memory Hierarchy Characteristics:**

| Level | Size (per unit) | Latency | Bandwidth | Scope |
|-------|----------------|---------|-----------|-------|
| Register File | 256 KB | 1 cycle | ~10 TB/s | Per SM |
| Shared Memory | 128 KB | 1-2 cycles | ~8 TB/s | Per SM |
| L1 Cache | 128 KB | 1-2 cycles | ~6 TB/s | Per SM |
| L2 Cache | 6 MB | 20-40 cycles | ~2 TB/s | Per Chiplet |
| HBM3E | 8-16 GB/stack | 200-300 cycles | 128 GB/s/stack | Global |

**Total Capacity:** 64-128 GB HBM3E, 24 MB L2, ~4 MB L1

---

## SM (Streaming Multiprocessor) Microarchitecture

### Detailed SM Block Diagram

```mermaid
graph TB
    subgraph SM["Streaming Multiprocessor (SM)"]
        subgraph FETCH["Instruction Fetch & Decode"]
            I_CACHE["I-Cache<br/>32 KB"]
            FETCH_UNIT["Fetch Unit"]
            DECODE["Decode Unit<br/>4-way"]
            SCOREBOARD["Scoreboard"]
        end
        
        subgraph WARP["Warp Scheduling"]
            WARP_SCHED0["Warp Scheduler 0"]
            WARP_SCHED1["Warp Scheduler 1"]
            WARP_SCHED2["Warp Scheduler 2"]
            WARP_SCHED3["Warp Scheduler 3"]
            DISPATCH["Dispatch Unit"]
        end
        
        subgraph EXEC["Execution Units"]
            direction TB
            
            subgraph TENSOR["Tensor Core Array"]
                TC0["Tensor Core 0<br/>MMA Units"]
                TC1["Tensor Core 1<br/>MMA Units"]
                TC2["Tensor Core 2<br/>MMA Units"]
                TC3["Tensor Core 3<br/>MMA Units"]
            end
            
            subgraph FP32_PIPE["FP32 Pipeline"]
                FP32_0["FP32 Units<br/>32x ALU"]
                FP32_1["FP32 Units<br/>32x ALU"]
                FP32_2["FP32 Units<br/>32x ALU"]
                FP32_3["FP32 Units<br/>32x ALU"]
            end
            
            subgraph INT_PIPE["INT32 Pipeline"]
                INT32_0["INT32 Units<br/>32x ALU"]
                INT32_1["INT32 Units<br/>32x ALU"]
            end
            
            subgraph SPECIAL["Special Function Units"]
                SFU0["SFU 0<br/>Transcendental"]
                SFU1["SFU 1<br/>Transcendental"]
            end
            
            LD_ST["Load/Store Units<br/>32 LSU"]
            TEX["Texture Units<br/>4x Samplers"]
        end
        
        subgraph MEM_SM["SM Memory"]
            RF["Register File<br/>256 KB<br/>65,536 x 32-bit"]
            SHARED["Shared Memory<br/>128 KB<br/>Configurable"]
            L1_DATA["L1 Data Cache<br/>128 KB"]
            CONST_CACHE["Constant Cache<br/>64 KB"]
            TEX_CACHE["Texture Cache<br/>48 KB"]
        end
        
        %% Instruction flow
        I_CACHE --> FETCH_UNIT
        FETCH_UNIT --> DECODE
        DECODE --> SCOREBOARD
        SCOREBOARD --> WARP_SCHED0 & WARP_SCHED1 & WARP_SCHED2 & WARP_SCHED3
        WARP_SCHED0 & WARP_SCHED1 & WARP_SCHED2 & WARP_SCHED3 --> DISPATCH
        
        %% Execution dispatch
        DISPATCH --> TC0 & TC1 & TC2 & TC3
        DISPATCH --> FP32_0 & FP32_1 & FP32_2 & FP32_3
        DISPATCH --> INT32_0 & INT32_1
        DISPATCH --> SFU0 & SFU1
        DISPATCH --> LD_ST
        DISPATCH --> TEX
        
        %% Register file access
        RF <--> TC0 & TC1 & TC2 & TC3
        RF <--> FP32_0 & FP32_1 & FP32_2 & FP32_3
        RF <--> INT32_0 & INT32_1
        RF <--> SFU0 & SFU1
        RF <--> LD_ST
        RF <--> TEX
        
        %% Memory access
        LD_ST <--> L1_DATA
        LD_ST <--> SHARED
        LD_ST <--> CONST_CACHE
        TEX <--> TEX_CACHE
        
    end
    
    %% External connections
    L1_DATA <--> L2["L2 Cache"]
    TEX_CACHE <--> L2
    CONST_CACHE <--> L2
    I_CACHE <--> L2
    
    style SM fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style FETCH fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style WARP fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style EXEC fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style TENSOR fill:#ffebee,stroke:#c62828,stroke-width:2px
    style MEM_SM fill:#fce4ec,stroke:#c2185b,stroke-width:2px
```

**SM Specifications:**
- **Warp Size:** 32 threads
- **Max Warps:** 64 (2048 threads per SM)
- **Registers:** 256 KB (65,536 x 32-bit registers)
- **Shared Memory:** 128 KB (configurable with L1)
- **Peak FP32:** 8.2 TFLOPS @ 2 GHz
- **Peak FP16 (Tensor):** 65.5 TFLOPS @ 2 GHz

---

## Floorplan Conceptual Layout

### Single Chiplet Floorplan (Top View)

```mermaid
graph TB
    subgraph CHIPLET["Single Chiplet (~20mm x 20mm, 400 mm²)"]
        subgraph TOP_LEFT["NW Quadrant"]
            SM0["SM 0"]
            SM1["SM 1"]
            SM2["SM 2"]
            SM3["SM 3"]
        end
        
        subgraph TOP_RIGHT["NE Quadrant"]
            SM4["SM 4"]
            SM5["SM 5"]
            SM6["SM 6"]
            SM7["SM 7"]
        end
        
        subgraph CENTER["Central Region"]
            direction TB
            L2_NORTH["L2 Slice 0<br/>1.5 MB"]
            XBAR_CENTER["Crossbar<br/>Interconnect"]
            L2_SOUTH["L2 Slice 1<br/>1.5 MB"]
            COHERENCE["Coherency<br/>Engine"]
        end
        
        subgraph BOTTOM_LEFT["SW Quadrant"]
            SM8["SM 8"]
            SM9["SM 9"]
            SM10["SM 10"]
            SM11["SM 11"]
        end
        
        subgraph BOTTOM_RIGHT["SE Quadrant"]
            SM12["SM 12"]
            SM13["SM 13"]
            SM14["SM 14"]
            SM15["SM 15"]
        end
        
        subgraph WEST_EDGE["West Edge"]
            HBM_W["HBM Ctrl 0<br/>PHY"]
            UCIE_W["UCIe PHY<br/>West"]
        end
        
        subgraph EAST_EDGE["East Edge"]
            HBM_E["HBM Ctrl 1<br/>PHY"]
            UCIE_E["UCIe PHY<br/>East"]
        end
        
        subgraph NORTH_EDGE["North Edge"]
            UCIE_N["UCIe PHY North"]
            NVLINK_N["NVLink PHY"]
            PCIE["PCIe PHY"]
        end
        
        subgraph SOUTH_EDGE["South Edge"]
            UCIE_S["UCIe PHY South"]
            PMU["PMU"]
            DEBUG["Debug"]
        end
        
        %% Connections to show relative positioning
        SM0 & SM1 & SM2 & SM3 --> L2_NORTH
        SM4 & SM5 & SM6 & SM7 --> L2_NORTH
        L2_NORTH --> XBAR_CENTER
        XBAR_CENTER --> L2_SOUTH
        L2_SOUTH --> SM8 & SM9 & SM10 & SM11
        L2_SOUTH --> SM12 & SM13 & SM14 & SM15
        
        XBAR_CENTER <--> COHERENCE
        XBAR_CENTER <--> HBM_W
        XBAR_CENTER <--> HBM_E
        XBAR_CENTER <--> UCIE_W
        XBAR_CENTER <--> UCIE_E
        XBAR_CENTER <--> UCIE_N
        XBAR_CENTER <--> UCIE_S
    end
    
    style CHIPLET fill:#f5f5f5,stroke:#333,stroke-width:4px
    style TOP_LEFT fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style TOP_RIGHT fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style BOTTOM_LEFT fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style BOTTOM_RIGHT fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style CENTER fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style WEST_EDGE fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style EAST_EDGE fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style NORTH_EDGE fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style SOUTH_EDGE fill:#fff9c4,stroke:#f9a825,stroke-width:2px
```

### Package-Level Floorplan (4-Chiplet Configuration)

```mermaid
graph TB
    subgraph PACKAGE["NexGen-AI Package (~50mm x 50mm with Interposer)"]
        subgraph INTERPOSER["Silicon Interposer"]
            direction LR
            
            subgraph QUAD_NW["Northwest"]
                C0["Chiplet 0<br/>20x20mm<br/>400mm²"]
                HBM0["HBM<br/>Stack 0"]
                HBM1["HBM<br/>Stack 1"]
            end
            
            subgraph QUAD_NE["Northeast"]
                C1["Chiplet 1<br/>20x20mm<br/>400mm²"]
                HBM2["HBM<br/>Stack 2"]
                HBM3["HBM<br/>Stack 3"]
            end
            
            subgraph QUAD_SW["Southwest"]
                C2["Chiplet 2<br/>20x20mm<br/>400mm²"]
                HBM4["HBM<br/>Stack 4"]
                HBM5["HBM<br/>Stack 5"]
            end
            
            subgraph QUAD_SE["Southeast"]
                C3["Chiplet 3<br/>20x20mm<br/>400mm²"]
                HBM6["HBM<br/>Stack 6"]
                HBM7["HBM<br/>Stack 7"]
            end
            
            subgraph CENTER_PKG["Central Routing"]
                UCIE_MESH["UCIe Mesh<br/>Interconnect"]
                POWER_DIST["Power<br/>Distribution"]
                THERMAL["Thermal<br/>Interface"]
            end
            
            subgraph EDGE_IO["Package I/O"]
                PCIE_IO["PCIe<br/>Bumps"]
                NVLINK_IO["NVLink<br/>Bumps"]
                POWER_IO["Power<br/>Bumps"]
            end
            
            %% Chiplet to HBM
            C0 -.-> HBM0 & HBM1
            C1 -.-> HBM2 & HBM3
            C2 -.-> HBM4 & HBM5
            C3 -.-> HBM6 & HBM7
            
            %% UCIe interconnect
            C0 <--> UCIE_MESH
            C1 <--> UCIE_MESH
            C2 <--> UCIE_MESH
            C3 <--> UCIE_MESH
            
            %% Power distribution
            POWER_IO --> POWER_DIST
            POWER_DIST -.-> C0 & C1 & C2 & C3
            POWER_DIST -.-> HBM0 & HBM1 & HBM2 & HBM3 & HBM4 & HBM5 & HBM6 & HBM7
            
            %% I/O
            C3 --> PCIE_IO
            C0 & C1 & C2 & C3 --> NVLINK_IO
        end
    end
    
    %% External connections
    PCIE_IO ==> HOST_SYS["Host System<br/>PCIe 6.0"]
    NVLINK_IO ==> MULTI_GPU["Multi-GPU<br/>NVLink"]
    
    %% Thermal solution
    THERMAL -.->|"Heat Transfer"| HEATSINK["Heatsink/<br/>Cooling Solution"]
    
    style PACKAGE fill:#f0f0f0,stroke:#333,stroke-width:4px
    style INTERPOSER fill:#fafafa,stroke:#666,stroke-width:3px
    style QUAD_NW fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style QUAD_NE fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style QUAD_SW fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style QUAD_SE fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style CENTER_PKG fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style EDGE_IO fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style C0 fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    style C1 fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    style C2 fill:#bbdefb,stroke:#1976d2,stroke-width:2px
    style C3 fill:#bbdefb,stroke:#1976d2,stroke-width:2px
```

**Package Specifications:**
- **Package Size:** ~50mm x 50mm (2500 mm²)
- **Chiplet Area:** 4 × 400 mm² = 1600 mm²
- **HBM Area:** 8 stacks × ~50 mm² = 400 mm²
- **Interposer Efficiency:** ~64% (chiplets + HBM)
- **Remaining:** Routing, power delivery, thermal interface

---

## Power Distribution Network

### Power Delivery Architecture

```mermaid
graph TB
    subgraph EXTERNAL["External Power Supply"]
        PSU["Power Supply Unit<br/>12V PCIe<br/>600W Capable"]
        VRM["Voltage Regulator<br/>Module (VRM)<br/>On-Board"]
    end
    
    subgraph PACKAGE_PWR["Package Power Distribution"]
        subgraph PRIMARY["Primary Rails"]
            VDD_CORE["VDD_CORE<br/>0.75V<br/>Core Logic"]
            VDD_HBM["VDD_HBM<br/>1.1V<br/>HBM Memory"]
            VDD_IO["VDD_IO<br/>1.8V<br/>I/O Interfaces"]
            VDD_AUX["VDD_AUX<br/>1.2V<br/>Aux Circuits"]
        end
        
        subgraph POWER_MGMT["Power Management"]
            PMIC["PMIC<br/>Power Management IC"]
            VOLTAGE_MON["Voltage<br/>Monitors"]
            CURRENT_MON["Current<br/>Sensors"]
            TEMP_MON["Temperature<br/>Sensors"]
        end
        
        subgraph DOMAINS["Power Domains (Per Chiplet)"]
            DOMAIN_SM["SM Array<br/>~150W<br/>DVFS Capable"]
            DOMAIN_L2["L2 Cache<br/>~8W"]
            DOMAIN_HBM["HBM Ctrl<br/>~30W"]
            DOMAIN_IO["I/O & PHY<br/>~12W"]
        end
    end
    
    subgraph PROTECTION["Protection Circuits"]
        OCP["Over-Current<br/>Protection"]
        OVP["Over-Voltage<br/>Protection"]
        UVP["Under-Voltage<br/>Protection"]
        OTP["Over-Temp<br/>Protection"]
    end
    
    %% Power flow
    PSU --> VRM
    VRM --> VDD_CORE & VDD_HBM & VDD_IO & VDD_AUX
    
    VDD_CORE --> DOMAIN_SM
    VDD_CORE --> DOMAIN_L2
    VDD_HBM --> DOMAIN_HBM
    VDD_IO --> DOMAIN_IO
    
    %% Management
    PMIC -.->|"Control"| VRM
    PMIC <--> VOLTAGE_MON
    PMIC <--> CURRENT_MON
    PMIC <--> TEMP_MON
    
    VOLTAGE_MON -.->|"Monitor"| VDD_CORE & VDD_HBM & VDD_IO
    CURRENT_MON -.->|"Monitor"| DOMAIN_SM & DOMAIN_HBM
    TEMP_MON -.->|"Monitor"| DOMAIN_SM
    
    %% Protection
    VOLTAGE_MON --> OVP & UVP
    CURRENT_MON --> OCP
    TEMP_MON --> OTP
    
    OCP & OVP & UVP & OTP -.->|"Shutdown"| PMIC
    
    %% DVFS control
    PMIC -.->|"DVFS"| DOMAIN_SM
    
    style EXTERNAL fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style PACKAGE_PWR fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style PRIMARY fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style POWER_MGMT fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style DOMAINS fill:#ffebee,stroke:#c62828,stroke-width:2px
    style PROTECTION fill:#fff9c4,stroke:#f9a825,stroke-width:2px
```

**Power Budget Breakdown (4-Chiplet SoC @ 100% Utilization):**

| Component | Power (W) | Percentage |
|-----------|-----------|------------|
| SM Arrays (64 total) | 192 | 72% |
| L2 Caches (24 MB total) | 12 | 4.5% |
| HBM3E (8 stacks) | 40 | 15% |
| HBM Controllers | 10 | 3.7% |
| Interconnect (UCIe) | 8 | 3% |
| I/O (PCIe, NVLink) | 10 | 3.7% |
| **Total Dynamic** | **272 W** | **~100%** |
| Static (Leakage) | 20 | - |
| **Grand Total** | **~292 W** | - |

---

## Usage Notes

### Viewing These Diagrams

1. **GitHub/GitLab:** Renders Mermaid natively
2. **VS Code:** Install "Markdown Preview Mermaid Support" extension
3. **Online:** Use [Mermaid Live Editor](https://mermaid.live/)
4. **Command Line:** Use the rendering tool to generate PNG/SVG images:
   ```bash
   # Install Mermaid CLI
   npm install -g @mermaid-js/mermaid-cli
   
   # Render all diagrams
   python tools/render_diagrams.py --all
   
   # List available diagrams
   python tools/render_diagrams.py --list
   
   # Render specific diagram
   python tools/render_diagrams.py --diagram chiplet
   ```
   See [tools/DIAGRAM_RENDERING.md](../tools/DIAGRAM_RENDERING.md) for details.
5. **Export:** Can be exported to PNG/SVG from Mermaid Live Editor

### Customization

To modify these diagrams:
1. Edit the Mermaid syntax in this markdown file
2. Adjust node names, connections, or styles
3. Change colors by modifying `style` declarations
4. Add/remove components as design evolves

### Integration with Architecture Documentation

These diagrams should be referenced in:
- Architecture specification documents
- Design review presentations
- Hardware/software interface documentation
- Verification planning documents
- Physical design guidelines

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-01-02 | 1.0 | Architecture Team | Initial block diagrams |

---

## Next Steps

1. **Add timing diagrams** for critical paths
2. **Create state machine diagrams** for control logic
3. **Develop interface specifications** with timing parameters
4. **Generate detailed floorplan** with exact dimensions
5. **Model thermal gradients** across package
6. **Create power state transition diagrams**

