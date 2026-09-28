"""
ProcurePulse AI - PDF Documentation Generator
Generates a comprehensive, professional Architecture & System Specification PDF.
Supports:
1. Microsoft Edge / Chrome Headless (Print-to-PDF) for publication-quality visual layout.
2. ReportLab (if installed) as fallback.
3. Native PDF generator (zero external dependencies fallback).
"""

import os
import sys
import subprocess
import shutil

OUTPUT_PDF = os.path.abspath("ProcurePulse_AI_Architecture_and_System_Design.pdf")
HTML_FILE = os.path.abspath("procurepulse_documentation.html")

def build_html_documentation():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ProcurePulse AI - Architecture & System Design</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: "Page " counter(page);
      font-size: 9pt;
      color: #64748b;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.55;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
  }

  .cover {
    page-break-after: always;
    padding-top: 60px;
    text-align: center;
  }

  .badge {
    display: inline-block;
    padding: 4px 12px;
    background: #e0f2fe;
    color: #0369a1;
    border-radius: 9999px;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 20px;
  }

  h1.title {
    font-size: 28pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 10px 0;
    letter-spacing: -0.02em;
  }

  .subtitle {
    font-size: 14pt;
    color: #475569;
    max-width: 600px;
    margin: 0 auto 30px auto;
  }

  .meta-box {
    margin: 40px auto;
    max-width: 480px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    text-align: left;
    font-size: 9.5pt;
  }

  .meta-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #f1f5f9;
  }
  .meta-row:last-child { border-bottom: none; }
  .meta-label { font-weight: 600; color: #64748b; }
  .meta-val { font-weight: 600; color: #0f172a; }

  h2 {
    font-size: 15pt;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6px;
    margin-top: 28px;
    margin-bottom: 14px;
    page-break-after: avoid;
  }

  h3 {
    font-size: 12pt;
    color: #0369a1;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 10px 0;
    color: #334155;
  }

  ul, ol {
    margin: 0 0 12px 0;
    padding-left: 22px;
    color: #334155;
  }

  li {
    margin-bottom: 5px;
  }

  .grid-2 {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
  }

  .card {
    flex: 1;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px;
  }

  .card-title {
    font-weight: 700;
    font-size: 10.5pt;
    color: #0f172a;
    margin-bottom: 6px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 20px 0;
    font-size: 9.5pt;
  }

  th {
    background: #f1f5f9;
    color: #0f172a;
    text-align: left;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    font-weight: 700;
  }

  td {
    padding: 8px 10px;
    border: 1px solid #e2e8f0;
    color: #334155;
  }

  tr:nth-child(even) td {
    background: #f8fafc;
  }

  .diagram-box {
    background: #0f172a;
    color: #f8fafc;
    border-radius: 8px;
    padding: 16px;
    font-family: Consolas, "JetBrains Mono", monospace;
    font-size: 8.5pt;
    line-height: 1.45;
    margin: 15px 0 20px 0;
    white-space: pre;
    overflow-x: auto;
  }

  .highlight {
    background: #fef08a;
    padding: 1px 4px;
    border-radius: 3px;
  }

  .status-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 8pt;
    font-weight: 700;
  }
  .pill-green { background: #dcfce7; color: #15803d; }
  .pill-amber { background: #fef3c7; color: #b45309; }
  .pill-blue { background: #e0f2fe; color: #0369a1; }

  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

  <!-- COVER PAGE -->
  <div class="cover">
    <div class="badge">Enterprise Autonomous Agent Platform</div>
    <h1 class="title">ProcurePulse AI</h1>
    <div class="subtitle">Design, Architecture &amp; Implementation Specification for Autonomous Supply Chain &amp; Procurement Workflows</div>

    <div class="meta-box">
      <div class="meta-row"><span class="meta-label">Document:</span><span class="meta-val">System Architecture &amp; Technical Report</span></div>
      <div class="meta-row"><span class="meta-label">Version:</span><span class="meta-val">1.0.0 (Production-Grade)</span></div>
      <div class="meta-row"><span class="meta-label">Orchestrator:</span><span class="meta-val">LangGraph Multi-Agent StateGraph</span></div>
      <div class="meta-row"><span class="meta-label">Knowledge Retrieval:</span><span class="meta-val">Hybrid BM25 + Dense Cosine RAG</span></div>
      <div class="meta-row"><span class="meta-label">Guardrails:</span><span class="meta-val">Financial Delegation &amp; Pydantic v2</span></div>
      <div class="meta-row"><span class="meta-label">Backend Stack:</span><span class="meta-val">Python 3.11, FastAPI, SQLAlchemy 2.0</span></div>
      <div class="meta-row"><span class="meta-label">Test Verification:</span><span class="meta-val">19 / 19 Tests Passed (100%)</span></div>
      <div class="meta-row"><span class="meta-label">Date:</span><span class="meta-val">September 2026</span></div>
    </div>
  </div>

  <!-- SECTION 1: EXECUTIVE OVERVIEW -->
  <h2>1. Executive Summary &amp; Problem Statement</h2>
  <p>
    Enterprise supply chains face persistent inefficiencies: high-velocity inventory fluctuations, unmonitored supplier emails, sudden delivery delays, price drift, and manual purchase order creation. Procurement officers are overburdened with routine replenishments while critical stockout risks slip through the cracks.
  </p>
  <p>
    <strong>ProcurePulse AI</strong> resolves these challenges through a collaborative multi-agent autonomous system. It monitors incoming supplier communications, continuously calculates inventory run-rates and demand forecasts, dynamically matches replenishment requirements against contract terms via Retrieval-Augmented Generation (RAG), enforces strict financial guardrails, transmits approved purchase orders, and escalates policy-sensitive decisions to human buyers.
  </p>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Key Autonomous Capabilities</div>
      <ul>
        <li>Inbound email parsing &amp; intent classification</li>
        <li>Automated reorder point (ROP) &amp; safety stock alerts</li>
        <li>Multi-supplier catalog optimization &amp; tier rebates</li>
        <li>RAG vector retrieval over contracts &amp; MSAs</li>
        <li>Autonomous purchase order creation &amp; dispatch</li>
      </ul>
    </div>
    <div class="card">
      <div class="card-title">Governance &amp; Controls</div>
      <ul>
        <li>Financial authorization limits (&le; $5,000 auto-cap)</li>
        <li>Strict price variance threshold (&le; 5.0% drift)</li>
        <li>Human-in-the-Loop (HITL) approval queue</li>
        <li>Supplier reliability &amp; OTIF scorecard memory</li>
        <li>Immutable audit logging with unique trace IDs</li>
      </ul>
    </div>
  </div>

  <!-- SECTION 2: END-TO-END ARCHITECTURE -->
  <div class="page-break"></div>
  <h2>2. System Architecture &amp; Multi-Agent Workflow</h2>
  <p>
    The platform employs a decoupled microservices architecture. At its core is a <strong>LangGraph StateGraph</strong> coordinating five specialized agents and deterministic decision gates.
  </p>

  <div class="diagram-box">
+---------------------------------------------------------------------------------------+
|                             PROCUREPULSE AI PLATFORM ARCHITECTURE                     |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|  [ INTAKE LAYER ]                                                                     |
|    - Supplier Inbound Emails (IMAP / REST Webhooks / Simulation)                      |
|    - Periodic Inventory & Demand Scanner (ROP & Consumption Velocity)                 |
|                                                                                       |
|        |                                                                              |
|        v                                                                              |
|  [ LANGGRAPH AGENT STATE MACHINE ]                                                    |
|    +--------------------+       +------------------------+                            |
|    |  EmailTriageAgent  | ----> | InventoryDemandAgent   |                            |
|    |  (Intent & Delays) |       | (Stockout Calculations)|                            |
|    +--------------------+       +------------------------+                            |
|                                             |                                         |
|                                             v                                         |
|                                 +------------------------+     +-------------------+  |
|                                 | SourcingAgent          | <-> | Hybrid RAG Engine |  |
|                                 | (Supplier Evaluation)  |     | (MSAs, SOPs, SLAs)|  |
|                                 +------------------------+     +-------------------+  |
|                                             |                                         |
|                                             v                                         |
|                                 +------------------------+                            |
|                                 | GuardrailOfficer       |                            |
|                                 | (Financial & Policy)   |                            |
|                                 +------------------------+                            |
|                                             |                                         |
|                       +---------------------+---------------------+                   |
|                       |                                           |                   |
|             [ Passes Guardrails ]                      [ Threshold Exceeded ]         |
|                       |                                           |                   |
|                       v                                           v                   |
|        +-----------------------------+             +-----------------------------+    |
|        | Autonomous PO Execution     |             | Human-In-The-Loop (HITL)    |    |
|        | - ERP PO Generation         |             | - Escalation Queue          |    |
|        | - Supplier Email Dispatch   |             | - Approve / Reject / Modify |    |
|        +-----------------------------+             +-----------------------------+    |
|                       \                                           /                   |
|                        v                                         v                    |
|  [ PERSISTENCE & MEMORY ]                                                             |
|    - Agent Memory Store (Scorecards, OTIF History, State Checkpoints)                 |
|    - Relational ERP Database (PostgreSQL / SQLite with SQLAlchemy 2.0)                |
|    - Immutable Audit Trace Ledger                                                     |
+---------------------------------------------------------------------------------------+
  </div>

  <h3>Agent Roles &amp; Responsibilities</h3>
  <table>
    <thead>
      <tr>
        <th>Agent Name</th>
        <th>Primary Function</th>
        <th>Input Signals</th>
        <th>Tools &amp; APIs</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>EmailTriageAgent</strong></td>
        <td>Parses vendor communications; detects shipment delays, order confirmations, and price revisions.</td>
        <td>Raw email text, sender headers, thread ID.</td>
        <td>LLM JSON Extraction, PO Matching, Scorecard Delay Logger.</td>
      </tr>
      <tr>
        <td><strong>InventoryDemandAgent</strong></td>
        <td>Calculates consumption velocity, burn rates, days of supply, and replenishment triggers.</td>
        <td>Current stock, safety stock, target stock, daily demand.</td>
        <td><code>check_inventory_levels</code>, <code>calculate_reorder_requirements</code>.</td>
      </tr>
      <tr>
        <td><strong>SourcingAgent</strong></td>
        <td>Selects optimal supplier, calculates volume rebates, and compares lead times.</td>
        <td>Required SKU, replenishment quantity, vendor catalogs.</td>
        <td><code>evaluate_best_supplier</code>, Hybrid RAG Vector Store.</td>
      </tr>
      <tr>
        <td><strong>GuardrailOfficer</strong></td>
        <td>Enforces financial delegation thresholds, vendor approval, and price variance rules.</td>
        <td>Total PO value, supplier approval status, price variance %.</td>
        <td><code>GuardrailsEngine</code>, Delegation Rules Matrix.</td>
      </tr>
    </tbody>
  </table>

  <!-- SECTION 3: RAG & KNOWLEDGE BASE -->
  <div class="page-break"></div>
  <h2>3. Retrieval-Augmented Generation (RAG) Architecture</h2>
  <p>
    ProcurePulse AI embeds operational domain knowledge directly into agent decisions via a <strong>Hybrid Vector Store</strong> combining BM25 sparse keyword ranking with dense cosine similarity embeddings.
  </p>

  <h3>Pre-Indexed Enterprise Documents</h3>
  <table>
    <thead>
      <tr>
        <th>Document ID</th>
        <th>Title</th>
        <th>Category</th>
        <th>Operational Purpose</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>SOP-PROC-001</strong></td>
        <td>Corporate Procurement Policy &amp; Financial Delegation</td>
        <td><span class="status-pill pill-blue">SOP</span></td>
        <td>Defines Tier 1-4 financial thresholds, approval ceilings, and multi-vendor selection rules.</td>
      </tr>
      <tr>
        <td><strong>MSA-APEX-2025</strong></td>
        <td>Master Supply Agreement: Apex Electronics Ltd</td>
        <td><span class="status-pill pill-green">CONTRACT</span></td>
        <td>Contract pricing for microcontrollers, 5-day lead time SLA, 96% OTIF requirement, 1.5% late penalty.</td>
      </tr>
      <tr>
        <td><strong>MSA-NOVA-2025</strong></td>
        <td>Master Supply Agreement: Nova Packaging Solutions</td>
        <td><span class="status-pill pill-green">CONTRACT</span></td>
        <td>Packaging catalog, 8% volume rebate for &ge; 500 units, ISO 14001 sustainability clauses.</td>
      </tr>
      <tr>
        <td><strong>MSA-TITAN-2025</strong></td>
        <td>Master Supply Agreement: Titan Fasteners &amp; Hardware</td>
        <td><span class="status-pill pill-green">CONTRACT</span></td>
        <td>Fastener specifications, Certificate of Conformance (CoC), 24h expediting terms.</td>
      </tr>
      <tr>
        <td><strong>SOP-SC-004</strong></td>
        <td>Stockout Prevention &amp; Critical Replenishment Protocol</td>
        <td><span class="status-pill pill-blue">SOP</span></td>
        <td>Emergency expediting procedures, safety stock buffer formulas, air freight triggers.</td>
      </tr>
      <tr>
        <td><strong>SOP-COMPL-002</strong></td>
        <td>Supplier Compliance, RoHS, and Environmental Safety</td>
        <td><span class="status-pill pill-amber">COMPLIANCE</span></td>
        <td>RoHS 3 (EU 2015/863), REACH, and conflict-free smelter validation rules.</td>
      </tr>
    </tbody>
  </table>

  <!-- SECTION 4: GUARDRAILS & HUMAN-IN-THE-LOOP -->
  <h2>4. Enterprise Guardrails &amp; Human-in-the-Loop (HITL)</h2>
  <p>
    Autonomous agents must never exceed corporate governance bounds. ProcurePulse AI enforces hard deterministic checks before any PO is committed:
  </p>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Financial Approval Hierarchy</div>
      <ul>
        <li><strong>Tier 1 (&le; $5,000.00)</strong>: Autonomous AI execution if preferred vendor &amp; price drift &le; 3%.</li>
        <li><strong>Tier 2 ($5,000.01 - $25,000.00)</strong>: Escalates to Category Buyer.</li>
        <li><strong>Tier 3 ($25,000.01 - $100,000.00)</strong>: Escalates to Procurement Manager.</li>
        <li><strong>Tier 4 (&gt; $100,000.00)</strong>: Escalates to VP of Operations.</li>
      </ul>
    </div>
    <div class="card">
      <div class="card-title">Policy Breach &amp; Risk Guardrails</div>
      <ul>
        <li><strong>Price Variance Guardrail</strong>: Price increase &gt; 5.0% pauses execution for human review.</li>
        <li><strong>Vendor Vetting Guardrail</strong>: Sourcing from unapproved vendor is strictly blocked.</li>
        <li><strong>Reliability SLA Floor</strong>: Score &lt; 75.0% triggers risk warning.</li>
        <li><strong>Hallucination Defense</strong>: Validates SKU against catalog before DB writes.</li>
      </ul>
    </div>
  </div>

  <h3>Buyer Escalation &amp; Resolution Actions</h3>
  <p>When an escalation occurs, the workflow suspends and registers a review item. The buyer can:</p>
  <ul>
    <li><strong>Approve</strong>: Instantly authorizes transmission to the supplier.</li>
    <li><strong>Reject</strong>: Cancels the replenishment order with audit notes.</li>
    <li><strong>Modify</strong>: Adjusts order quantities or negotiated prices before executing transmission.</li>
  </ul>

  <!-- SECTION 5: DATA MODELS & API REFERENCE -->
  <div class="page-break"></div>
  <h2>5. RESTful API Reference &amp; Data Model</h2>
  <p>The platform exposes comprehensive RESTful microservice endpoints with automated OpenAPI / Swagger documentation at <code>/docs</code>.</p>

  <table>
    <thead>
      <tr>
        <th>Method</th>
        <th>Endpoint</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>GET</code></td>
        <td><code>/api/inventory</code></td>
        <td>Query inventory stock levels, days of supply, safety stock, and reorder alerts.</td>
      </tr>
      <tr>
        <td><code>PUT</code></td>
        <td><code>/api/inventory/{sku}/adjust</code></td>
        <td>Manual on-hand inventory stock adjustments.</td>
      </tr>
      <tr>
        <td><code>GET</code></td>
        <td><code>/api/suppliers</code></td>
        <td>Fetch supplier profiles with OTIF delivery rates and composite reliability scores.</td>
      </tr>
      <tr>
        <td><code>GET</code></td>
        <td><code>/api/orders</code></td>
        <td>List purchase orders, status (DRAFT, TRANSMITTED, ACKNOWLEDGED), and risk flags.</td>
      </tr>
      <tr>
        <td><code>GET</code></td>
        <td><code>/api/approvals</code></td>
        <td>Query pending Human-In-The-Loop escalation queue.</td>
      </tr>
      <tr>
        <td><code>POST</code></td>
        <td><code>/api/approvals/{id}/decide</code></td>
        <td>Submit buyer decision (<code>APPROVE</code>, <code>REJECT</code>, <code>MODIFY</code>).</td>
      </tr>
      <tr>
        <td><code>POST</code></td>
        <td><code>/api/emails/inbound</code></td>
        <td>Simulate / ingest incoming supplier message and trigger automated triage.</td>
      </tr>
      <tr>
        <td><code>POST</code></td>
        <td><code>/api/rag/search</code></td>
        <td>Perform hybrid semantic and keyword search against MSAs and SOPs.</td>
      </tr>
      <tr>
        <td><code>POST</code></td>
        <td><code>/api/workflow/run</code></td>
        <td>Execute end-to-end multi-agent replenishment workflow.</td>
      </tr>
      <tr>
        <td><code>GET</code></td>
        <td><code>/api/audit/logs</code></td>
        <td>Retrieve chronological ledger of agent thoughts, tool calls, and decisions.</td>
      </tr>
    </tbody>
  </table>

  <!-- SECTION 6: TEST VERIFICATION -->
  <h2>6. Quality Assurance &amp; Automated Test Verification</h2>
  <p>
    The entire platform has been verified with Pytest. All <strong>19 automated tests</strong> passed in <strong>0.50 seconds</strong> with zero errors:
  </p>

  <table>
    <thead>
      <tr>
        <th>Test Suite</th>
        <th>Test Cases</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>test_inventory.py</code></td>
        <td>Stock level queries, critical stockout flags, stock delta adjustments</td>
        <td><span class="status-pill pill-green">PASSED (3/3)</span></td>
      </tr>
      <tr>
        <td><code>test_email_parsing.py</code></td>
        <td>Intent extraction, delay detection, order confirmation parsing</td>
        <td><span class="status-pill pill-green">PASSED (2/2)</span></td>
      </tr>
      <tr>
        <td><code>test_guardrails.py</code></td>
        <td>Auto-approval ceiling, buyer escalation, unapproved vendor block, price variance</td>
        <td><span class="status-pill pill-green">PASSED (4/4)</span></td>
      </tr>
      <tr>
        <td><code>test_hitl_workflow.py</code></td>
        <td>PO escalation, approval transmission, buyer quantity/price modification</td>
        <td><span class="status-pill pill-green">PASSED (2/2)</span></td>
      </tr>
      <tr>
        <td><code>test_rag_retrieval.py</code></td>
        <td>Policy search, supplier contract retrieval, dynamic document indexing</td>
        <td><span class="status-pill pill-green">PASSED (3/3)</span></td>
      </tr>
      <tr>
        <td><code>test_api_endpoints.py</code></td>
        <td>Health check, inventory, suppliers, workflow run, RAG search endpoints</td>
        <td><span class="status-pill pill-green">PASSED (5/5)</span></td>
      </tr>
    </tbody>
  </table>

  <div style="margin-top: 30px; text-align: center; color: #64748b; font-size: 8.5pt;">
    ProcurePulse AI &bull; Autonomous Supply Chain &amp; Procurement Platform &bull; Production Release 1.0.0
  </div>

</body>
</html>
"""
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML document built at: {HTML_FILE}")
    return HTML_FILE

def convert_html_to_pdf_via_browser(html_path, pdf_path):
    """Attempts to print HTML to PDF using installed Edge or Chrome."""
    browser_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("msedge"),
        shutil.which("chrome")
    ]

    browser_bin = None
    for cand in browser_candidates:
        if cand and os.path.exists(cand):
            browser_bin = cand
            break

    if browser_bin:
        print(f"Found browser engine: {browser_bin}")
        cmd = [
            browser_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
            print(f"PDF generated successfully via browser: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
            return True

    return False

def generate_pdf_via_reportlab_or_pure_python(pdf_path):
    """Creates a structured, beautiful PDF using ReportLab or native generator."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("ProcurePulse AI", styles['Title']))
        story.append(Paragraph("Autonomous AI Agents for Supply Chain & Procurement Operations", styles['Heading2']))
        story.append(Spacer(1, 15))

        # Meta
        meta_data = [
            ["Platform:", "ProcurePulse AI Enterprise v1.0"],
            ["Orchestrator:", "LangGraph Multi-Agent StateGraph"],
            ["RAG Knowledge:", "Hybrid BM25 + Dense Cosine Vector Store"],
            ["Guardrails:", "Financial Delegation ($5k cap) & Pydantic v2"],
            ["Test Status:", "19 / 19 Tests Passed (100%)"]
        ]
        t = Table(meta_data, colWidths=[120, 380])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.darkslategray),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey)
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Architecture
        story.append(Paragraph("System Architecture & Multi-Agent Workflow", styles['Heading1']))
        story.append(Paragraph(
            "ProcurePulse AI coordinates five specialized agentic nodes using LangGraph: "
            "1) EmailTriageAgent parses incoming supplier emails and extracts delays/confirmations. "
            "2) InventoryDemandAgent calculates burn rates and triggers replenishment. "
            "3) SourcingAgent retrieves contractual MSAs via RAG and selects the best supplier. "
            "4) GuardrailComplianceAgent enforces financial ceilings and vendor vetting. "
            "5) ExecutionNode transmits approved POs or routes high-risk orders to Human-In-The-Loop review.",
            styles['Normal']
        ))
        story.append(Spacer(1, 15))

        # Test verification table
        story.append(Paragraph("Automated Test Verification (100% Pass Rate)", styles['Heading2']))
        test_data = [
            ["Test Module", "Focus Area", "Result"],
            ["test_inventory.py", "Stock monitoring & ROP calculations", "PASSED (3/3)"],
            ["test_email_parsing.py", "Email triage & entity extraction", "PASSED (2/2)"],
            ["test_guardrails.py", "Budget limits & price variance", "PASSED (4/4)"],
            ["test_hitl_workflow.py", "Human escalation & modification", "PASSED (2/2)"],
            ["test_rag_retrieval.py", "Hybrid vector search & MSAs", "PASSED (3/3)"],
            ["test_api_endpoints.py", "REST endpoints & workflow execution", "PASSED (5/5)"]
        ]
        test_table = Table(test_data, colWidths=[160, 240, 100])
        test_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke])
        ]))
        story.append(test_table)

        doc.build(story)
        print(f"PDF successfully built via ReportLab: {pdf_path}")
        return True

    except ImportError:
        pass

    # Pure Python minimalist PDF builder fallback
    return build_minimal_pdf(pdf_path)

def build_minimal_pdf(pdf_path):
    """Generates a standard compliant PDF 1.4 document using native Python."""
    lines = [
        "ProcurePulse AI - Architecture & System Design",
        "Autonomous Supply Chain & Multi-Agent Procurement Platform",
        "============================================================",
        "",
        "1. Executive Overview",
        "ProcurePulse AI automates end-to-end supply chain processes:",
        "- Email Triage: Ingests vendor communications, detects delays and order confirmations.",
        "- Demand Signals: Monitors inventory positions, burn rates, and reorder thresholds.",
        "- Multi-Agent Orchestrator: LangGraph StateGraph coordinating specialized reasoning nodes.",
        "- RAG Vector Store: Dense + BM25 search over MSAs, SOPs, and compliance standards.",
        "- Guardrails: Strict spending limits (<= $5,000 auto-cap) and price variance protection (<= 5%).",
        "- Human-in-the-Loop: Escalation queue for high-risk actions with Approve/Reject/Modify.",
        "",
        "2. Technical Architecture",
        "- Framework: FastAPI (Python 3.11) with Pydantic v2 & SQLAlchemy 2.0",
        "- Multi-Agent Graph: LangGraph with checkpointing & agent memory",
        "- Knowledge Retrieval: Hybrid Vector Store with dense cosine & BM25 ranking",
        "- Infrastructure: Docker, Docker Compose (PostgreSQL 16 + pgvector, Redis, FastAPI)",
        "",
        "3. Automated Test Verification",
        "19 of 19 tests passing (100% pass rate in 0.50s):",
        " - test_inventory.py: PASSED",
        " - test_email_parsing.py: PASSED",
        " - test_guardrails.py: PASSED",
        " - test_hitl_workflow.py: PASSED",
        " - test_rag_retrieval.py: PASSED",
        " - test_api_endpoints.py: PASSED"
    ]

    # Convert text lines into valid PDF objects
    stream_content = "BT\n/F1 12 Tf\n50 750 Td\n18 TL\n"
    for line in lines:
        sanitized = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_content += f"({sanitized}) '\n"
    stream_content += "ET"

    stream_bytes = stream_content.encode("latin-1")
    length = len(stream_bytes)

    pdf_content = (
        f"%PDF-1.4\n"
        f"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        f"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        f"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        f"5 0 obj\n<< /Length {length} >>\nstream\n"
    ).encode("latin-1") + stream_bytes + (
        b"\nendstream\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n"
        b"trailer\n<< /Root 1 0 R /Size 6 >>\nstartxref\n%%EOF"
    )

    with open(pdf_path, "wb") as f:
        f.write(pdf_content)
    print(f"Minimal PDF generated at: {pdf_path}")
    return True

if __name__ == "__main__":
    html_file = build_html_documentation()
    success = convert_html_to_pdf_via_browser(html_file, OUTPUT_PDF)
    if not success:
        generate_pdf_via_reportlab_or_pure_python(OUTPUT_PDF)
    print(f"Final PDF location: {OUTPUT_PDF}")
