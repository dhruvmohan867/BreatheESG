# Sources

For each of the three data sources: what real-world format was researched, what was learned, what the sample data looks like, and what would break in a real deployment.

## 1. SAP — Fuel and Procurement Data

### What I Researched
SAP Materials Management (MM) module handles fuel procurement. Data can be extracted via:
- **IDoc**: Intermediate Document format for EDI. XML/flat file structure.
- **BAPI**: Function module calls via RFC. Requires direct SAP connectivity.
- **OData**: RESTful API available in S/4HANA. Not available in older ECC systems.
- **Flat file export**: Transaction SE16N or custom ABAP reports export to CSV/TSV.

I chose **flat file export from MM** because it's the most common extraction method for mid-market SAP deployments. Most companies don't have OData enabled or RFC connectivity available to external systems.

### What I Learned
- SAP field names are abbreviated German: WERKS (plant), MATNR (material number), MENGE (quantity), MEINS (unit of measure), BUDAT (posting date), KOSTL (cost center), BWART (movement type)
- Units are inconsistent — same fuel may appear as L, LTR, Liters, or KL depending on the plant configuration
- Dates can be YYYY-MM-DD or DD/MM/YYYY depending on user locale settings
- Plant codes (1010, 1020) are meaningless without the T001W lookup table
- Movement type 101 = goods receipt. You'd also see 102 (reversal), 201 (consumption) in real data

### Sample Data Design
```
WERKS,MATNR,MAKTX,MENGE,MEINS,BUDAT,KOSTL,BWART
1010,50000120,Diesel Fuel - Generator,4500,L,2024-01-15,CC4010,101
1020,50000135,Petrol - Fleet Vehicles,320,L,2024-01-22,CC5020,101
1010,50000140,LPG - Canteen,2.5,KL,2024-02-01,CC4010,101
```

Edge cases included:
- Mixed date formats (ISO vs DD/MM/YYYY)
- Inconsistent unit abbreviations (L vs LTR)
- KL (kiloliters) requiring conversion
- Negative quantity (reversal/correction)
- Missing unit field
- Invalid date string
- SCM (standard cubic meters for natural gas) — an unknown unit

### What Would Break in Production
- **Plant code resolution**: We can't map WERKS 1010 to "Mumbai Manufacturing Plant" without the T001W master data table
- **Material master**: MATNR 50000120 means nothing without the MARA table. We're relying on MAKTX (description) which may not always be present
- **Movement type filtering**: Real SAP data includes reversals (102), consumption (201), and inter-plant transfers (301). We only handle goods receipts
- **Multi-currency procurement**: Fuel purchased abroad has currency and exchange rate fields we're ignoring
- **Character encoding**: SAP exports can contain German umlauts (ä, ö, ü) and other special characters

---

## 2. Utility Data — Electricity

### What I Researched
Indian utility providers (Tata Power, BSES, MSEDCL, BESCOM, Adani Electricity) offer:
- **Portal CSV download**: Most common. Manual login, download monthly consumption
- **PDF bills**: Standardized per provider but different across providers
- **Green Button API**: US standard, not available in India
- **Automated meter reading (AMR)**: Available for industrial consumers, provides 15-min interval data

I chose **portal CSV export** because it's what facilities teams actually do — log in monthly, download consumption, email the file.

### What I Learned
- Billing periods don't align with calendar months. A "January" bill might cover Dec 28 to Jan 27
- Meter IDs are provider-specific identifiers (MTR-A001) not standardized
- Tariff types (Commercial, Industrial, Residential) affect pricing but not emissions
- Account numbers link to billing, meter IDs link to consumption points
- A single facility can have multiple meters (one per floor, per building, per process)
- Readings can be in kWh or MWh depending on meter type

### Sample Data Design
```
account_number,meter_id,billing_period_start,billing_period_end,reading_date,kwh_consumed,unit,tariff_type,provider,facility
ACC-2201,MTR-A001,2024-01-01,2024-01-31,2024-02-05,12450,kWh,Commercial,Tata Power,Mumbai HQ
```

Edge cases included:
- Negative consumption (meter replacement or correction)
- Missing meter ID
- Zero consumption (closed facility)
- Massive spike (145,000 kWh — possibly a factory)
- Invalid date string
- MWh unit requiring conversion (1 MWh = 1000 kWh)

### What Would Break in Production
- **Billing period overlaps**: Two bills for the same meter with overlapping periods would double-count consumption
- **Time-of-use tariffs**: Peak/off-peak breakdowns in the same bill aren't handled
- **Reactive power**: Industrial meters measure kVAh alongside kWh. We only handle active energy
- **Solar offset**: Facilities with rooftop solar have net metering — consumption can be negative legitimately
- **Multi-provider consolidation**: A company with facilities across states has different providers with different CSV formats

---

## 3. Corporate Travel — Flights

### What I Researched
Major corporate travel platforms:
- **SAP Concur**: Market leader. Exposes data via SAE (Standard Accounting Extract) files and API
- **Navan (formerly TripActions)**: REST API with CSV export option
- **OTIS/FCM**: Custom report builders with CSV/Excel output

I chose **Concur SAE-style CSV export** because Concur dominates the Indian enterprise market and SAE files are the standard way companies extract travel data for reporting.

### What I Learned
- Concur exports include booking reference, employee ID, departure/arrival airports (IATA codes), travel class, expense category, and vendor
- Distances aren't always provided — sometimes you only get airport code pairs and need to compute great-circle distance
- Travel class matters: business class has ~2x the emission factor of economy (more seat space = more emissions per passenger)
- Expense categories distinguish Air Travel from Ground Transport from Hotel stays
- International flights have lower per-km emissions than domestic flights (longer cruise phase)

### Sample Data Design
```
booking_ref,employee_id,trip_date,departure_iata,arrival_iata,distance_km,travel_class,expense_category,vendor,unit
TRV-20240101,EMP-045,2024-01-10,DEL,BOM,1400,Economy,Air Travel,IndiGo,km
```

Emission factor logic:
- Domestic economy (< 3500 km): 0.255 kgCO₂/km
- International economy (> 3500 km): 0.195 kgCO₂/km
- Business class: 0.39 kgCO₂/km (1.5x economy, accounting for seat space)

Edge cases included:
- Missing departure IATA code
- Missing arrival IATA code
- Distance > 20,000 km (unrealistic for single flight)
- Negative distance
- Invalid date
- International long-haul (DEL-LHR, BOM-SFO)

### What Would Break in Production
- **Airport code resolution**: We accept raw IATA codes but don't validate them against a real airport database. "ZZZ" would pass through
- **Multi-leg flights**: DEL → DXB → LHR shows as one booking but is two flight segments with different distances
- **Hotel and ground transport**: We only handle flights. Hotels need room-nights, ground transport needs vehicle type
- **Missing distances**: Real Concur exports sometimes omit distance entirely. We'd need a great-circle distance calculator using IATA coordinates
- **Employee privacy**: Production systems need to anonymize employee IDs for GDPR/privacy compliance
- **Cabin class mapping**: Concur uses "Y" (economy), "C" (business), "F" (first) — different from our free-text approach
