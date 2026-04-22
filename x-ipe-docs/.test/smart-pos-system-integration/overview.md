# SMART POS System Integration — Knowledge Notes Overview

> Extracted from Confluence: CHINA SMART → 20.SMART POS → Architecture Design → 01. Application Architecture → 0101. Design For System Integration
> 
> **Source:** https://jiranium-apac-japan.atlassian.net/wiki/spaces/CS/
> **Extracted:** 2026-04-13 | **Total Notes:** 31 | **Coverage:** 30 integrations + 1 landscape overview

---

## Table of Contents

| # | Integration | Division | Type | File |
|---|-------------|----------|------|------|
| 01 | **Integration Landscape** (parent page) | All | Overview | [01.integration-landscape.md](01.integration-landscape.md) |
| 02 | **AX** (ERP) | FSN/WFJ/FBP | API + File | [02.ax-integration.md](02.ax-integration.md) |
| 03 | **RED** (EPC Management) | FSN | API | [03.red-integration.md](03.red-integration.md) |
| 04 | **3S** (EPC/SN Validation) | FSN | API | [04.3s-integration.md](04.3s-integration.md) |
| 05 | **CASS** (After-Sales) | FSN | API | [05.cass-integration.md](05.cass-integration.md) |
| 06 | **China Product Hub** | FSN | File | [06.china-product-hub.md](06.china-product-hub.md) |
| 07 | **BA Express** (Business Analytics) | FBP | API + File | [07.ba-express-integration.md](07.ba-express-integration.md) |
| 08 | **FBRS** (Replenishment) | FBP | File | [08.fbrs-integration.md](08.fbrs-integration.md) |
| 09 | **E-FAPIAO** (Electronic Invoice) | FBP/FSN | API | [09.e-fapiao-integration.md](09.e-fapiao-integration.md) |
| 10 | **GDP** (Stock On Hand) | FBP | File | [10.gdp-integration.md](10.gdp-integration.md) |
| 11 | **P360** (SN Validation) | WFJ | API | [11.p360-integration.md](11.p360-integration.md) |
| 12 | **Brinks Logistics** | WFJ | API | [12.brinks-logistics.md](12.brinks-logistics.md) |
| 13 | **TTPOS Store Transfer** | FSN/WFJ | File | [13.ttpos-store-transfer.md](13.ttpos-store-transfer.md) |
| 14 | **China Data Warehouse** | FSN/WFJ | File | [14.china-data-warehouse.md](14.china-data-warehouse.md) |
| 15 | **FSN API Gateway** (TBD) | FSN/WFJ | TBD | [15.fsn-api-gateway.md](15.fsn-api-gateway.md) |
| 16 | **RS** (Replenishment) | FSN/WFJ/FBP | API + File | [16.rs-integration.md](16.rs-integration.md) |
| 17 | **dataLAB** (Analytics) | FSN/WFJ/FBP | File | [17.datalab-integration.md](17.datalab-integration.md) |
| 18 | **GAIA** (Reconciliation) | FSN/WFJ/FBP | API + File | [18.gaia-integration.md](18.gaia-integration.md) |
| 19 | **RetailNext & ShopTracker** | FSN/WFJ/FBP | File | [19.retailnext-shoptracker.md](19.retailnext-shoptracker.md) |
| 20 | **LION** (CRM) | FSN/WFJ/FBP | API + File | [20.lion-integration.md](20.lion-integration.md) |
| 21 | **Product/Price Master** | FSN/WFJ/FBP | File | [21.product-price-master.md](21.product-price-master.md) |
| 22 | **WMS** (Warehouse) | FSN/WFJ/FBP | File | [22.wms-integration.md](22.wms-integration.md) |
| 23 | **New WMS UpScale** | FSN/WFJ/FBP | File | [23.new-wms-upscale.md](23.new-wms-upscale.md) |
| 24 | **TTPOS VIP/Staff Quota** | FSN/WFJ | API | [24.ttpos-vip-staff-quota.md](24.ttpos-vip-staff-quota.md) |
| 25 | **PEARL** (Product Info) | WFJ | API | [25.pearl-integration.md](25.pearl-integration.md) |
| 26 | **AX TX Reconciliation** | FSN/WFJ/FBP | File | [26.ax-tx-reconciliation.md](26.ax-tx-reconciliation.md) |
| 27 | **TTPOS VIP Quota** | FSN/WFJ | API | [27.ttpos-vip-quota.md](27.ttpos-vip-quota.md) |
| 28 | **EDH** (Enterprise Data Hub) | FSN/WFJ/FBP | File | [28.edh-integration.md](28.edh-integration.md) |
| 29 | **InChanel** (Omni-channel) | FSN | API | [29.inchanel-integration.md](29.inchanel-integration.md) |
| 30 | **Apollo** (Integration Gateway) | All | Reference | [30.apollo-design.md](30.apollo-design.md) |
| 31 | **Workday** (Employee Master) | FSN/WFJ/FBP | File | [31.workday-integration.md](31.workday-integration.md) |

---

## Integration Patterns Summary

### Common Integration Gateways
- **Apollo CN** — Required for almost all integrations (central China gateway)
- **Apollo APAC** — Required for distribution pattern (TX, SOH to downstream)
- **Global APIM** — Required for global systems (P360, 3S, InChanel)

### Integration Types
- **API:** AX, RED, 3S, CASS, E-FAPIAO, P360, Brinks, TTPOS VIP/Staff, PEARL, InChanel
- **File:** China Product Hub, FBRS, GDP, TTPOS Store Transfer, CDW, WMS, New WMS, dataLAB, RetailNext, Product/Price Master, EDH, Workday
- **Mixed (API + File):** AX, BA Express, RS, GAIA, LION

### Division Coverage
- **FSN only:** RED, 3S, CASS, China Product Hub, InChanel
- **WFJ only:** P360, Brinks, PEARL
- **FBP only:** BA Express, FBRS, GDP
- **FSN/WFJ:** TTPOS Store Transfer, CDW, FSN API Gateway, TTPOS VIP/Staff, TTPOS VIP Quota
- **FBP/FSN:** E-FAPIAO
- **All 3 Divisions:** AX, RS, dataLAB, GAIA, RetailNext, LION, Product/Price Master, WMS, New WMS, AX Reconciliation, EDH, Apollo, Workday

### TX Distribution Pattern
```
SMART POS → Apollo CN → Apollo APAC → downstream systems
```
Used by: RS, RetailNext, dataLAB, GAIA, CDW, BA Express

### Parallel Run Strategy
Most integrations maintain both TTPOS and SMART POS data flows simultaneously. "Combine tools" merge data from both systems during the transition period.
