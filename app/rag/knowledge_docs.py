"""
Pre-loaded enterprise knowledge base documents:
- Corporate Procurement Policy SOP (PO thresholds, signature authority, payment terms)
- Supplier Master Agreements (Apex Electronics, Nova Packaging, Titan Fasteners)
- Quality & Compliance Protocols (RoHS, REACH, ISO 9001)
- Expedited Freight & Critical Stockout Resolution Guide
"""

ENTERPRISE_KNOWLEDGE_DOCUMENTS = [
    {
        "id": "SOP-PROC-001",
        "title": "Corporate Procurement Policy 2026 & Financial Delegation of Authority",
        "category": "SOP",
        "content": (
            "CORPORATE PROCUREMENT POLICY (DOC REF: SOP-PROC-001 - REV 4.2)\n"
            "1. Financial Approval Thresholds:\n"
            "   - Tier 1 (Autonomous Execution): Purchase orders <= $5,000.00 USD may be generated and "
            "transmitted autonomously by the AI Procurement Agent ONLY if the supplier is in 'Approved' and 'Preferred' status, "
            "and unit price variance against the contracted catalog is <= 3.0%.\n"
            "   - Tier 2 (Buyer Approval Required): Purchase orders between $5,000.01 and $25,000.00 USD must be "
            "escalated to the designated Category Buyer for review and electronic sign-off prior to transmission.\n"
            "   - Tier 3 (Procurement Manager Approval): Purchase orders between $25,000.01 and $100,000.00 USD require "
            "Procurement Manager sign-off.\n"
            "   - Tier 4 (VP Operations Approval): Purchase orders > $100,000.00 USD or any purchase involving an unapproved/new vendor "
            "require Executive Vice President approval.\n"
            "2. Price Variance Rule:\n"
            "   - Any purchase order line item exhibiting a price increase > 5.0% compared to historical 90-day average must be "
            "escalated to a human buyer regardless of the total dollar amount.\n"
            "3. Multi-Vendor Policy:\n"
            "   - When multiple approved vendors offer the identical SKU, the agent must evaluate: 1) Lowest Total Cost of Acquisition "
            "(unit price + freight), 2) Historical On-Time Delivery Rate (minimum 92%), 3) Lead Time constraints."
        ),
        "metadata": {"version": "4.2", "department": "Supply Chain Operations", "effective_date": "2026-01-01"}
    },
    {
        "id": "MSA-APEX-2025",
        "title": "Master Supply Agreement: Apex Electronics Ltd",
        "category": "CONTRACT",
        "content": (
            "MASTER SUPPLY AGREEMENT - APEX ELECTRONICS LTD (CONTRACT # MSA-2025-APX)\n"
            "1. Products Covered: Microcontrollers (SKU-ELEC-001, STM32F4), Power Regulators (SKU-ELEC-002, LM2596), "
            "Ceramic Capacitors (SKU-ELEC-003, 100uF SMD).\n"
            "2. Lead Times & Minimum Order Quantities (MOQ):\n"
            "   - Standard lead time: 5 business days for domestic warehouse dispatch.\n"
            "   - Minimum order quantity (MOQ) for MCU-STM32 is 100 units; MOQ for Power Regulator is 200 units.\n"
            "3. Delivery Terms & Incoterms:\n"
            "   - DDP (Delivered Duty Paid) to Central Manufacturing Hub.\n"
            "4. SLA Penalty Clause:\n"
            "   - On-time delivery SLA benchmark is 96.0%. Delays exceeding 7 calendar days without 48-hour prior written notice "
            "incur a 1.5% penalty per week deducted from payable invoices.\n"
            "5. Payment Terms: Net 30 days from invoice date via wire transfer."
        ),
        "metadata": {"supplier_code": "SUP-APEX", "contract_type": "Preferred Tier 1", "expiry": "2027-12-31"}
    },
    {
        "id": "MSA-NOVA-2025",
        "title": "Master Supply Agreement: Nova Packaging Solutions",
        "category": "CONTRACT",
        "content": (
            "MASTER SUPPLY AGREEMENT - NOVA PACKAGING SOLUTIONS (CONTRACT # MSA-2025-NOV)\n"
            "1. Products Covered: Heavy Corrugated Shipping Cartons (SKU-PACK-001), Biodegradable Bubble Wrap (SKU-PACK-002), "
            "Reinforced Poly Strapping (SKU-PACK-003).\n"
            "2. Lead Times & Volume Discounts:\n"
            "   - Standard lead time: 3 business days.\n"
            "   - Tier Discount: Orders of corrugated cartons >= 500 units receive an automatic 8.0% volume rebate ($2.30/unit vs $2.50 standard).\n"
            "3. Sustainability Clause:\n"
            "   - 100% recycled material guarantee. ISO 14001 certification mandatory.\n"
            "4. Payment Terms: Net 45 days."
        ),
        "metadata": {"supplier_code": "SUP-NOVA", "contract_type": "Primary Packaging", "expiry": "2026-11-30"}
    },
    {
        "id": "MSA-TITAN-2025",
        "title": "Master Supply Agreement: Titan Fasteners & Hardware",
        "category": "CONTRACT",
        "content": (
            "MASTER SUPPLY AGREEMENT - TITAN FASTENERS & HARDWARE (CONTRACT # MSA-2025-TTN)\n"
            "1. Products Covered: M3 Stainless Machine Screws (SKU-MECH-001), Hex Stand-offs 12mm (SKU-MECH-002), "
            "Anodized Aluminum Mounting Brackets (SKU-MECH-003).\n"
            "2. Lead Times: 4 business days.\n"
            "3. Quality Assurance: Zero Defect Policy (PPM < 50). All batches must ship with Certificate of Conformance (CoC).\n"
            "4. Expedited Delivery: Available with 24-hour turnaround for a 15% surcharge upon emergency buyer confirmation.\n"
            "5. Payment Terms: Net 30 days."
        ),
        "metadata": {"supplier_code": "SUP-TITAN", "contract_type": "Mechanical Components", "expiry": "2027-06-30"}
    },
    {
        "id": "SOP-SC-004",
        "title": "Stockout Prevention & Critical Replenishment Protocol",
        "category": "SOP",
        "content": (
            "STOCKOUT PREVENTION AND EMERGENCY PROCUREMENT (DOC REF: SOP-SC-004)\n"
            "1. Critical Thresholds:\n"
            "   - Stockout Warning: Current stock <= Reorder Point (ROP = Daily Demand * Lead Time + Safety Stock).\n"
            "   - Critical Emergency: Current stock <= Safety Stock (< 5 days of production supply).\n"
            "2. Action Protocol:\n"
            "   - The AI Agent must calculate replenishment quantity = (Target Stock - Current Stock).\n"
            "   - If current supplier delivery lead time will result in stockout before arrival, the agent must check secondary "
            "approved suppliers and evaluate air freight / expedited shipping options.\n"
            "   - Emergency expediting with surcharges > $1,000 must be escalated to the Operations Manager."
        ),
        "metadata": {"version": "3.1", "department": "Supply Chain Logistics"}
    },
    {
        "id": "SOP-COMPL-002",
        "title": "Supplier Compliance, RoHS, and Environmental Safety",
        "category": "COMPLIANCE",
        "content": (
            "SUPPLIER COMPLIANCE & RESTRICTED SUBSTANCES PROTOCOL (SOP-COMPL-002)\n"
            "1. Restriction of Hazardous Substances (RoHS 3):\n"
            "   - All electronic and electromechanical components must possess valid RoHS 3 (EU 2015/863) certificates of compliance.\n"
            "2. Conflict Minerals Compliance:\n"
            "   - Tantalum, Tin, Tungsten, and Gold (3TG) must be sourced from conflict-free smelters.\n"
            "3. Any vendor failing to update compliance documents every 12 months is automatically downgraded to 'Non-Approved'."
        ),
        "metadata": {"regulatory": ["RoHS", "REACH", "Dodd-Frank 1502"]}
    }
]
