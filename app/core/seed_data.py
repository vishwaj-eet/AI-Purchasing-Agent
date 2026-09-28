import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.supplier import Supplier, SupplierCatalog, SupplierScorecard
from app.models.purchase_order import PurchaseOrder, POLineItem, POStatus, ApprovalTier
from app.models.email_message import EmailMessage
from app.models.approval import ApprovalRequest

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    # Check if data already exists
    if db.query(Product).first():
        logger.info("Database already seeded. Skipping initial seed.")
        return

    logger.info("Seeding initial enterprise supply chain data...")

    # 1. Suppliers
    suppliers = [
        Supplier(
            code="SUP-APEX",
            name="Apex Electronics Ltd",
            contact_name="Sarah Chen",
            contact_email="sales@apexelectronics.com",
            phone="+1-555-0144",
            address="100 Silicon Way, San Jose, CA",
            payment_terms="Net 30",
            currency="USD",
            reliability_score=98.2,
            on_time_delivery_rate=97.5,
            quality_rating=4.9,
            price_competitiveness_score=92.0,
            is_preferred=True,
            is_approved=True,
            notes="Primary franchised distributor for microcontrollers and passive components."
        ),
        Supplier(
            code="SUP-NOVA",
            name="Nova Packaging Solutions",
            contact_name="Marcus Vance",
            contact_email="orders@novapackaging.com",
            phone="+1-555-0288",
            address="45 Industrial Parkway, Chicago, IL",
            payment_terms="Net 45",
            currency="USD",
            reliability_score=96.0,
            on_time_delivery_rate=95.8,
            quality_rating=4.8,
            price_competitiveness_score=95.0,
            is_preferred=True,
            is_approved=True,
            notes="Eco-friendly packaging manufacturer with regional warehousing."
        ),
        Supplier(
            code="SUP-TITAN",
            name="Titan Fasteners & Hardware",
            contact_name="Elena Rostova",
            contact_email="supply@titanfasteners.com",
            phone="+1-555-0371",
            address="800 Precision Drive, Cleveland, OH",
            payment_terms="Net 30",
            currency="USD",
            reliability_score=94.5,
            on_time_delivery_rate=94.0,
            quality_rating=4.7,
            price_competitiveness_score=91.0,
            is_preferred=True,
            is_approved=True,
            notes="Aerospace and industrial grade hardware fasteners."
        ),
        Supplier(
            code="SUP-GLOB",
            name="Global Semiconductor Direct",
            contact_name="Kenji Sato",
            contact_email="b2b@globalsemi.com",
            phone="+1-555-0992",
            address="Tower 2, Akihabara Tech District, Tokyo, Japan",
            payment_terms="Net 60",
            currency="USD",
            reliability_score=84.0,
            on_time_delivery_rate=82.5,
            quality_rating=4.3,
            price_competitiveness_score=88.0,
            is_preferred=False,
            is_approved=True,
            notes="Secondary backup distributor; higher lead times due to trans-Pacific air freight."
        ),
        Supplier(
            code="SUP-UNKNOWN",
            name="FastTrack Component Brokers",
            contact_name="Dave Miller",
            contact_email="deals@fasttrackbroker.net",
            phone="+1-555-0610",
            address="33 Shadow Lane, Miami, FL",
            payment_terms="Advance",
            currency="USD",
            reliability_score=68.0,
            on_time_delivery_rate=65.0,
            quality_rating=3.2,
            price_competitiveness_score=98.0,
            is_preferred=False,
            is_approved=False,
            notes="Unverified grey-market broker. High risk of counterfeit components."
        )
    ]
    db.add_all(suppliers)
    db.commit()

    # Re-query suppliers to get IDs
    sup_apex = db.query(Supplier).filter_by(code="SUP-APEX").first()
    sup_nova = db.query(Supplier).filter_by(code="SUP-NOVA").first()
    sup_titan = db.query(Supplier).filter_by(code="SUP-TITAN").first()
    sup_glob = db.query(Supplier).filter_by(code="SUP-GLOB").first()

    # 2. Products & Inventory Position
    products = [
        Product(
            sku="SKU-ELEC-001",
            name="STM32F407 High-Performance Microcontroller IC",
            description="32-bit ARM Cortex-M4 MCU, 168MHz, 1MB Flash, LQFP-100",
            category="Electronics",
            unit_of_measure="PCS",
            unit_cost=8.45,
            current_stock=75,         # Below reorder point! Needs replenishment
            safety_stock=100,
            reorder_point=180,
            target_stock=600,
            daily_demand_rate=12.0,    # ~6.2 days of supply remaining
            lead_time_days=5
        ),
        Product(
            sku="SKU-ELEC-002",
            name="LM2596 Step-Down Voltage Regulator IC",
            description="3A Step-Down Voltage Regulator, 150kHz, TO-220-5",
            category="Electronics",
            unit_of_measure="PCS",
            unit_cost=1.85,
            current_stock=42,          # Critical emergency! Below safety stock
            safety_stock=80,
            reorder_point=160,
            target_stock=500,
            daily_demand_rate=9.0,     # ~4.6 days of supply
            lead_time_days=4
        ),
        Product(
            sku="SKU-ELEC-003",
            name="100uF 50V Low-ESR SMD Capacitor",
            description="Aluminum Electrolytic Capacitors - SMD 100uF 50V 20%",
            category="Electronics",
            unit_of_measure="PCS",
            unit_cost=0.35,
            current_stock=1200,        # Healthy stock
            safety_stock=300,
            reorder_point=600,
            target_stock=1500,
            daily_demand_rate=25.0,
            lead_time_days=5
        ),
        Product(
            sku="SKU-PACK-001",
            name="Corrugated Shipping Box 40x30x25cm",
            description="Heavy-duty double wall corrugated shipping box",
            category="Packaging",
            unit_of_measure="PCS",
            unit_cost=2.30,
            current_stock=110,         # Below reorder point
            safety_stock=150,
            reorder_point=280,
            target_stock=800,
            daily_demand_rate=20.0,
            lead_time_days=3
        ),
        Product(
            sku="SKU-PACK-002",
            name="Biodegradable Bubble Cushioning Roll",
            description="Air bubble wrap 300mm x 50m roll eco-friendly starch polymer",
            category="Packaging",
            unit_of_measure="ROLL",
            unit_cost=14.50,
            current_stock=35,
            safety_stock=20,
            reorder_point=40,
            target_stock=100,
            daily_demand_rate=3.0,
            lead_time_days=4
        ),
        Product(
            sku="SKU-MECH-001",
            name="M3 x 8mm Stainless Steel Hex Screws",
            description="ISO 7380 A2-70 Stainless Button Head Screws (Pack of 100)",
            category="Mechanical",
            unit_of_measure="PK",
            unit_cost=3.20,
            current_stock=18,          # Low stock!
            safety_stock=25,
            reorder_point=50,
            target_stock=150,
            daily_demand_rate=4.0,
            lead_time_days=4
        ),
        Product(
            sku="SKU-MECH-002",
            name="Extruded Aluminum Heatsink Bracket",
            description="Anodized black 6063-T5 aluminum thermal dissipation bracket",
            category="Mechanical",
            unit_of_measure="PCS",
            unit_cost=5.80,
            current_stock=240,         # Healthy
            safety_stock=80,
            reorder_point=150,
            target_stock=400,
            daily_demand_rate=6.0,
            lead_time_days=7
        )
    ]
    db.add_all(products)
    db.commit()

    # 3. Supplier Catalogs & Pricing Tiers
    catalogs = [
        SupplierCatalog(
            supplier_id=sup_apex.id,
            sku="SKU-ELEC-001",
            supplier_part_number="STM32F407VET6-APX",
            unit_price=8.45,
            moq=100,
            lead_time_days=5,
            tier_discount_json='[{"min_qty": 500, "discount_pct": 5.0}, {"min_qty": 1000, "discount_pct": 8.0}]'
        ),
        SupplierCatalog(
            supplier_id=sup_apex.id,
            sku="SKU-ELEC-002",
            supplier_part_number="LM2596S-ADJ-APX",
            unit_price=1.85,
            moq=100,
            lead_time_days=4,
            tier_discount_json='[{"min_qty": 500, "discount_pct": 6.0}]'
        ),
        SupplierCatalog(
            supplier_id=sup_apex.id,
            sku="SKU-ELEC-003",
            supplier_part_number="CAP-100UF-50V-SMD",
            unit_price=0.35,
            moq=500,
            lead_time_days=5
        ),
        SupplierCatalog(
            supplier_id=sup_nova.id,
            sku="SKU-PACK-001",
            supplier_part_number="BOX-403025-DW",
            unit_price=2.30,
            moq=200,
            lead_time_days=3,
            tier_discount_json='[{"min_qty": 500, "discount_pct": 8.0}]'
        ),
        SupplierCatalog(
            supplier_id=sup_nova.id,
            sku="SKU-PACK-002",
            supplier_part_number="BUBBLE-BIO-300",
            unit_price=14.50,
            moq=20,
            lead_time_days=4
        ),
        SupplierCatalog(
            supplier_id=sup_titan.id,
            sku="SKU-MECH-001",
            supplier_part_number="SCRW-M3-8-SS",
            unit_price=3.20,
            moq=25,
            lead_time_days=4
        ),
        SupplierCatalog(
            supplier_id=sup_titan.id,
            sku="SKU-MECH-002",
            supplier_part_number="BRKT-ALUM-6063",
            unit_price=5.80,
            moq=50,
            lead_time_days=6
        ),
        SupplierCatalog(
            supplier_id=sup_glob.id,
            sku="SKU-ELEC-001",
            supplier_part_number="GSD-STM32F407-OEM",
            unit_price=8.95,
            moq=150,
            lead_time_days=12
        )
    ]
    db.add_all(catalogs)

    # 4. Supplier Scorecards
    scorecards = [
        SupplierScorecard(
            supplier_id=sup_apex.id,
            total_orders=48,
            on_time_orders=47,
            late_orders=1,
            quality_defects=0,
            avg_delay_days=0.2,
            notes="Consistently superior delivery performance under MSA-2025-APX."
        ),
        SupplierScorecard(
            supplier_id=sup_nova.id,
            total_orders=35,
            on_time_orders=34,
            late_orders=1,
            quality_defects=1,
            avg_delay_days=0.4,
            notes="High reliability. Minor carton moisture issue resolved in Q1."
        ),
        SupplierScorecard(
            supplier_id=sup_titan.id,
            total_orders=29,
            on_time_orders=28,
            late_orders=1,
            quality_defects=0,
            avg_delay_days=0.3,
            notes="Excellent fastener precision and full CoC documentation provided."
        ),
        SupplierScorecard(
            supplier_id=sup_glob.id,
            total_orders=22,
            on_time_orders=18,
            late_orders=4,
            quality_defects=2,
            avg_delay_days=4.5,
            last_sla_breach=datetime.utcnow() - timedelta(days=20),
            notes="Frequent customs clearance hold-ups at port of entry."
        )
    ]
    db.add_all(scorecards)
    db.commit()

    # 5. Existing Purchase Orders (for history & email linking)
    po1 = PurchaseOrder(
        po_number="PO-1048",
        supplier_id=sup_apex.id,
        status=POStatus.ACKNOWLEDGED.value,
        total_amount=4225.00,
        currency="USD",
        approval_tier=ApprovalTier.AUTO.value,
        risk_score=0.08,
        expected_delivery_date=datetime.utcnow() + timedelta(days=3),
        agent_generated=1,
        notes="Automated replenishment order for STM32F407 microcontrollers."
    )
    db.add(po1)
    db.commit()

    li1 = POLineItem(
        po_id=po1.id,
        sku="SKU-ELEC-001",
        description="STM32F407 High-Performance Microcontroller IC",
        quantity=500,
        unit_price=8.45,
        subtotal=4225.00
    )
    db.add(li1)

    po2 = PurchaseOrder(
        po_number="PO-1049",
        supplier_id=sup_nova.id,
        status=POStatus.TRANSMITTED.value,
        total_amount=1610.00,
        currency="USD",
        approval_tier=ApprovalTier.AUTO.value,
        risk_score=0.12,
        expected_delivery_date=datetime.utcnow() + timedelta(days=2),
        agent_generated=1,
        notes="Automated replenishment for corrugated packaging cartons."
    )
    db.add(po2)
    db.commit()

    li2 = POLineItem(
        po_id=po2.id,
        sku="SKU-PACK-001",
        description="Corrugated Shipping Box 40x30x25cm",
        quantity=700,
        unit_price=2.30,
        subtotal=1610.00
    )
    db.add(li2)

    # 6. Sample Inbound Emails (Simulating real supplier communications)
    sample_emails = [
        EmailMessage(
            message_id="msg-apex-1048-ack",
            thread_id="th-po-1048",
            sender="sales@apexelectronics.com",
            recipient="procurement@enterprise.internal",
            subject="Order Confirmation: PO-1048 [STM32F407 Microcontrollers]",
            body=(
                "Dear Procurement Team,\n\n"
                "We are pleased to confirm receipt and acceptance of Purchase Order PO-1048.\n"
                "Quantity: 500 units of SKU-ELEC-001 (STM32F407VET6).\n"
                "Unit Price: $8.45 | Total: $4,225.00 USD.\n"
                "Estimated dispatch date: Tomorrow via FedEx Priority Freight.\n"
                "Tracking reference will be issued upon pickup.\n\n"
                "Best regards,\nSarah Chen - Apex Electronics"
            ),
            direction="INBOUND",
            parsed_intent="ORDER_CONFIRMATION",
            parsed_entities_json='{"po_number": "PO-1048", "status": "CONFIRMED", "dispatch_estimate": "1 day"}',
            sentiment="POSITIVE",
            confidence_score=98,
            po_reference_id=po1.id,
            status="PROCESSED"
        ),
        EmailMessage(
            message_id="msg-nova-1049-delay",
            thread_id="th-po-1049",
            sender="orders@novapackaging.com",
            recipient="procurement@enterprise.internal",
            subject="URGENT: Production Schedule Delay Notice - PO-1049",
            body=(
                "Attention Purchasing Operations,\n\n"
                "Regrettably, due to an unexpected raw cardboard pulp mill maintenance outage, "
                "shipment of PO-1049 (700 units of SKU-PACK-001) is delayed by approximately 8 business days.\n"
                "Revised target delivery date: 2026-10-14.\n"
                "We sincerely apologize for this disruption and can arrange partial dispatch of 250 units "
                "from our backup warehouse if required.\n\n"
                "Sincerely,\nMarcus Vance - Nova Packaging Solutions"
            ),
            direction="INBOUND",
            parsed_intent="SHIPMENT_DELAY",
            parsed_entities_json='{"po_number": "PO-1049", "delay_days": 8, "revised_delivery_date": "2026-10-14", "partial_dispatch_available": true}',
            sentiment="CRITICAL",
            confidence_score=96,
            po_reference_id=po2.id,
            status="ESCALATED"
        )
    ]
    db.add_all(sample_emails)
    db.commit()
    logger.info("Database seeding complete!")
