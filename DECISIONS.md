# Decisions

Every ambiguity encountered during development, what was chosen, why, and what I would ask the PM if I could.

## 1. SAP Export Format: IDoc Flat File

**Ambiguity**: SAP exposes data via IDoc, BAPI, OData, RFC, and flat file exports. Which one to handle?

**Decision**: IDoc-style flat file CSV. In practice, most mid-market SAP deployments export fuel and procurement data as flat files from MM (Materials Management). The columns follow SAP field naming conventions: WERKS (plant code), MATNR (material number), MAKTX (material description), MENGE (quantity), MEINS (unit of measure), BUDAT (posting date), KOSTL (cost center).

**Why**: OData requires API connectivity and authentication setup. BAPI requires RFC connections. For a prototype that handles realistic shapes, flat file ingestion covers the most common real-world scenario — someone exports from SAP GUI and emails a CSV.

**Would ask PM**: Does the client use S/4HANA (OData-first) or ECC (flat file exports)? Are we connecting directly to SAP or receiving periodic file drops?

## 2. Utility Data: Portal CSV Export

**Ambiguity**: Utility data comes as PDF bills, portal CSV downloads, or API feeds. Which mode?

**Decision**: Portal CSV export with columns matching what Indian utility portals typically provide — account number, meter ID, billing period start/end, consumption, tariff type, provider name, facility location.

**Why**: PDF parsing is unreliable and out of scope for a 4-day prototype. API connectivity varies wildly between providers. Most facilities teams manually download CSVs from their utility portal monthly. This is the realistic ingestion path.

**Would ask PM**: Do they have multiple utility providers across facilities? Are billing periods aligned or do we need period normalization?

## 3. Travel Platform: Concur-Style CSV Export

**Ambiguity**: Concur exposes data via API (SAE), CSV export, and Excel reports. Which one?

**Decision**: CSV export mimicking Concur's expense report format — booking reference, employee ID, IATA airport codes, distance, travel class, expense category, vendor.

**Why**: Concur API access requires SAE certification and is enterprise-only. Most companies export monthly travel reports as CSV. Using IATA codes (DEL, BOM, LHR) instead of city names is what real travel platforms provide.

**Would ask PM**: Does the client use Concur, Navan, or TripActions? Do they need hotel and ground transport or just flights for now?

## 4. Scope Classification: Auto-Assigned by Source Type

**Ambiguity**: Should scope be user-input or system-determined?

**Decision**: Auto-assigned during ingestion. SAP fuel → Scope 1, Utility → Scope 2, Travel → Scope 3. This follows GHG Protocol category boundaries directly.

**Why**: For the three source types we handle, scope classification is deterministic. Fuel combustion is always Scope 1, purchased electricity is always Scope 2, business travel is always Scope 3. Making this a user input adds friction and error risk with no benefit.

**Would ask PM**: Are there edge cases where their fuel data includes purchased fuel for resale (which wouldn't be Scope 1)?

## 5. Emission Factors: Hardcoded Per-Fuel-Type

**Ambiguity**: Should emission factors come from a database, user input, or be hardcoded?

**Decision**: Hardcoded in the parser layer with fuel-type keyword matching. Diesel = 2.68 kgCO₂/L, Petrol = 2.31, LPG = 1.51, Electricity (India grid) = 0.82 kgCO₂/kWh, Domestic flight = 0.255 kgCO₂/km.

**Why**: For a prototype, maintaining an emission factor database is overengineering. The factors used are from IPCC/DEFRA and are defensible. Storing the applied factor per-record means they can be updated and records recalculated later.

**Would ask PM**: Do they have custom emission factors? Do they want DEFRA, EPA, or IPCC defaults?

## 6. Suspicious Row Detection: Rule-Based, Not ML

**Decision**: Simple rules — negative values, missing fields, zero readings, statistical spikes (10x median), unrealistic distances (>20,000 km), invalid dates. No machine learning.

**Why**: Rule-based detection is explainable. When an analyst asks "why was this flagged?", the answer is "because the quantity is negative" not "because the model said so." For an audit-facing tool, explainability is more important than accuracy.

## 7. Authentication: Deferred

**Decision**: No user authentication in the prototype. Reviewer names are free-text input.

**Would ask PM**: What auth system does the client use? SSO? Do we need role-based access (analyst vs auditor)?

## 8. Unit Normalization Strategy

**Decision**: All fuel volumes → Liters, all energy → kWh, all distances → km. The original value and unit are preserved alongside the normalized version.

**Why**: Having one canonical unit per measurement type makes aggregation possible. Keeping the original prevents data loss and supports auditor verification.
