// ProcurePulse AI Frontend Controller
let currentApprovalId = null;

document.addEventListener('DOMContentLoaded', () => {
  loadKPIs();
  loadInventory();
  loadApprovals();
  loadOrders();
  loadEmails();
  loadSuppliers();
  loadRAGDocs();
  loadAuditLogs();
});

// Tab Navigation
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.nav-tab').forEach(el => {
    el.classList.remove('text-sky-400', 'border-sky-400');
    el.classList.add('text-slate-400', 'border-transparent');
  });

  const targetView = document.getElementById(`view-${tabId}`);
  const targetTab = document.getElementById(`tab-${tabId}`);

  if (targetView && targetTab) {
    targetView.classList.remove('hidden');
    targetTab.classList.add('text-sky-400', 'border-sky-400');
    targetTab.classList.remove('text-slate-400', 'border-transparent');
  }

  // Refresh data when opening specific tabs
  if (tabId === 'inventory') loadInventory();
  if (tabId === 'approvals') loadApprovals();
  if (tabId === 'orders') loadOrders();
  if (tabId === 'emails') loadEmails();
  if (tabId === 'suppliers') loadSuppliers();
  if (tabId === 'audit') loadAuditLogs();
}

// 1. KPI Metrics
async function loadKPIs() {
  try {
    const [invRes, appRes, ordRes, supRes] = await Promise.all([
      fetch('/api/inventory'),
      fetch('/api/approvals?status=PENDING'),
      fetch('/api/orders'),
      fetch('/api/suppliers')
    ]);

    const inventory = await invRes.json();
    const approvals = await appRes.json();
    const orders = await ordRes.json();
    const suppliers = await supRes.json();

    // Critical stock count
    const criticalCount = inventory.filter(p => p.is_critical_stockout_risk).length;
    document.getElementById('kpi-critical-stock').textContent = criticalCount;

    // Approvals count
    const pendingCount = approvals.length;
    document.getElementById('kpi-pending-approvals').textContent = pendingCount;
    const badge = document.getElementById('badge-pending-approvals');
    if (pendingCount > 0) {
      badge.textContent = pendingCount;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }

    // Total Spend
    const totalSpend = orders.reduce((sum, o) => sum + (o.total_amount || 0), 0);
    document.getElementById('kpi-total-spend').textContent = `$${totalSpend.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    // Reliability
    const avgRel = suppliers.length ? (suppliers.reduce((sum, s) => sum + (s.reliability_score || 0), 0) / suppliers.length).toFixed(1) : '95.0';
    document.getElementById('kpi-avg-reliability').textContent = `${avgRel}%`;

  } catch (err) {
    console.error('Error loading KPIs:', err);
  }
}

// 2. Workflow Trigger & Console Streaming
async function executeSelectedWorkflow() {
  const targetSku = document.getElementById('select-target-sku').value;
  const consoleEl = document.getElementById('workflow-console-output');
  const statusPill = document.getElementById('workflow-status-pill');

  statusPill.textContent = 'Executing LangGraph...';
  statusPill.className = 'text-xs px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-400 font-semibold border border-sky-500/40 animate-pulse';

  consoleEl.innerHTML = `<div class="text-sky-400 font-semibold">🚀 Initializing LangGraph multi-agent orchestration...</div>
  <div class="text-slate-400">[01] Triage Node: Scanning inbound events & demand triggers...</div>`;

  try {
    const res = await fetch('/api/workflow/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        trigger_type: targetSku ? 'MANUAL_SKU' : 'SCHEDULED_REPLENISHMENT',
        target_sku: targetSku || null
      })
    });

    const data = await res.json();

    statusPill.textContent = data.status;
    if (data.status === 'COMPLETED') {
      statusPill.className = 'text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/40';
    } else if (data.status === 'ESCALATED_TO_HUMAN') {
      statusPill.className = 'text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-semibold border border-amber-500/40';
    } else {
      statusPill.className = 'text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold';
    }

    let outHtml = `
      <div class="text-cyan-400 font-bold">✓ LangGraph Execution Finished (Trace: ${data.trace_id})</div>
      <div class="text-slate-300 font-semibold">${data.summary_message}</div>
      <div class="border-t border-slate-800 pt-2 space-y-2">
    `;

    if (data.recommendations && data.recommendations.length > 0) {
      outHtml += `<div class="text-indigo-400 font-semibold">🔍 Sourcing Evaluations:</div>`;
      data.recommendations.forEach(r => {
        outHtml += `
          <div class="bg-slate-900 p-2.5 rounded-lg border border-slate-800">
            <div class="flex justify-between font-bold text-slate-200">
              <span>${r.sku} (${r.product_name})</span>
              <span class="text-emerald-400">$${r.total_cost.toFixed(2)} USD</span>
            </div>
            <div class="text-[11px] text-slate-400 mt-1">${r.rationale}</div>
          </div>
        `;
      });
    }

    if (data.escalations && data.escalations.length > 0) {
      outHtml += `<div class="text-amber-400 font-semibold mt-2">⚠️ Escalated to Buyer Approvals:</div>`;
      data.escalations.forEach(e => {
        outHtml += `
          <div class="bg-amber-950/20 border border-amber-900/40 p-2 rounded text-[11px] text-amber-300">
            <strong>${e.po_number}</strong> (${e.risk_level} Risk): ${e.reasons.join('; ')}
          </div>
        `;
      });
    }

    if (data.generated_pos && data.generated_pos.length > 0) {
      outHtml += `<div class="text-emerald-400 font-semibold mt-2">📦 Autonomously Transmitted Orders:</div>`;
      data.generated_pos.forEach(p => {
        outHtml += `
          <div class="bg-emerald-950/20 border border-emerald-900/40 p-2 rounded text-[11px] text-emerald-300">
            <strong>${p.po_number}</strong> to ${p.supplier_name} - Total: $${p.total_amount.toFixed(2)}
          </div>
        `;
      });
    }

    outHtml += `</div>`;
    consoleEl.innerHTML = outHtml;

    // Refresh KPI counters and other tabs
    loadKPIs();
    loadApprovals();
    loadOrders();
    loadInventory();

  } catch (err) {
    statusPill.textContent = 'Error';
    statusPill.className = 'text-xs px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400 font-semibold border border-rose-500/40';
    consoleEl.innerHTML += `<div class="text-rose-400 font-bold mt-2">Error during workflow execution: ${err.message}</div>`;
  }
}

function triggerReplenishmentScan() {
  document.getElementById('select-target-sku').value = '';
  switchTab('overview');
  executeSelectedWorkflow();
}

// 3. Inventory & Replenishment Monitor
async function loadInventory() {
  const tbody = document.getElementById('inventory-table-body');
  try {
    const res = await fetch('/api/inventory');
    const products = await res.json();

    if (!products.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-500">No inventory products found.</td></tr>`;
      return;
    }

    tbody.innerHTML = products.map(p => {
      let badge = `<span class="px-2 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-[10px] font-semibold">HEALTHY</span>`;
      if (p.is_critical_stockout_risk) {
        badge = `<span class="px-2 py-0.5 rounded bg-rose-500/20 border border-rose-500/30 text-rose-400 text-[10px] font-semibold animate-pulse">CRITICAL RISK</span>`;
      } else if (p.is_below_reorder_point) {
        badge = `<span class="px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/30 text-amber-400 text-[10px] font-semibold">REORDER TRIGGER</span>`;
      }

      const stockPct = Math.min(100, Math.round((p.current_stock / p.target_stock) * 100));
      const barColor = p.is_critical_stockout_risk ? 'bg-rose-500' : p.is_below_reorder_point ? 'bg-amber-500' : 'bg-emerald-500';

      return `
        <tr class="hover:bg-slate-900/50 transition">
          <td class="py-3 px-4">
            <div class="font-bold text-slate-200">${p.sku}</div>
            <div class="text-[11px] text-slate-400 truncate max-w-xs">${p.name}</div>
          </td>
          <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">${p.category}</span></td>
          <td class="py-3 px-4 font-mono">
            <div class="font-bold text-slate-100">${p.current_stock} ${p.unit_of_measure}</div>
            <div class="w-24 bg-slate-800 rounded-full h-1.5 mt-1 overflow-hidden">
              <div class="${barColor} h-1.5 rounded-full" style="width: ${stockPct}%"></div>
            </div>
          </td>
          <td class="py-3 px-4 font-mono text-slate-300">${p.reorder_point}</td>
          <td class="py-3 px-4 font-mono text-slate-400">${p.safety_stock}</td>
          <td class="py-3 px-4 font-mono font-bold ${p.days_of_supply < 7 ? 'text-rose-400' : 'text-slate-200'}">${p.days_of_supply}d</td>
          <td class="py-3 px-4">${badge}</td>
          <td class="py-3 px-4 text-right">
            <button onclick="triggerReplenishSku('${p.sku}')" class="px-2.5 py-1 rounded bg-sky-500/20 hover:bg-sky-500/30 border border-sky-500/40 text-sky-300 font-semibold text-[11px] transition">
              Replenish
            </button>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-rose-400">Failed to load inventory: ${err.message}</td></tr>`;
  }
}

function triggerReplenishSku(sku) {
  document.getElementById('select-target-sku').value = sku;
  switchTab('overview');
  executeSelectedWorkflow();
}

// 4. Human-In-The-Loop Approvals
async function loadApprovals() {
  const container = document.getElementById('approvals-container');
  try {
    const res = await fetch('/api/approvals');
    const approvals = await res.json();

    if (!approvals.length) {
      container.innerHTML = `<div class="text-center py-10 text-slate-500 text-xs">No pending approvals! All procurement tasks operating autonomously.</div>`;
      return;
    }

    container.innerHTML = approvals.map(app => {
      const isPending = app.status === 'PENDING';
      const riskColor = app.risk_level === 'CRITICAL' ? 'border-rose-500/60 bg-rose-950/20' : app.risk_level === 'HIGH' ? 'border-amber-500/60 bg-amber-950/20' : 'border-sky-500/60 bg-sky-950/20';

      return `
        <div class="glass-card p-4 rounded-xl border ${riskColor} space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${app.risk_level === 'CRITICAL' ? 'bg-rose-500/30 text-rose-400' : 'bg-amber-500/30 text-amber-400'}">
                ${app.risk_level} RISK
              </span>
              <span class="text-xs font-mono font-bold text-slate-200">PO ID: ${app.po_id}</span>
              <span class="text-xs text-slate-400">• Threshold: ${app.required_role}</span>
            </div>
            <div class="text-xs font-mono font-bold text-slate-100">
              Amount: <span class="text-emerald-400">$${app.requested_amount.toFixed(2)} USD</span>
            </div>
          </div>

          <div class="p-3 bg-slate-950/80 rounded-lg border border-slate-800 text-xs space-y-1.5">
            <div class="font-semibold text-amber-300">Escalation Trigger:</div>
            <div class="text-slate-300">${app.trigger_reason}</div>
            <div class="font-semibold text-sky-300 mt-2">Agent Sourcing Rationale:</div>
            <div class="text-slate-400 italic">${app.agent_reasoning}</div>
          </div>

          ${isPending ? `
            <div class="flex items-center justify-end space-x-2 pt-1">
              <button onclick="openApprovalModal(${app.id}, '${app.trigger_reason.replace(/'/g, "\\'")}', '${app.agent_reasoning.replace(/'/g, "\\'")}', ${app.requested_amount})" class="px-4 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs shadow transition">
                <i class="fa-solid fa-pen-to-square mr-1"></i>Review & Decide
              </button>
            </div>
          ` : `
            <div class="text-right text-[11px] font-semibold text-slate-400">
              Resolved: <span class="${app.status === 'APPROVED' ? 'text-emerald-400' : 'text-rose-400'}">${app.status}</span> by ${app.reviewer_user || 'Buyer'}
            </div>
          `}
        </div>
      `;
    }).join('');

  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-center py-6 text-xs">Error loading approvals: ${err.message}</div>`;
  }
}

function openApprovalModal(appId, reason, rationale, amount) {
  currentApprovalId = appId;
  document.getElementById('modal-app-reason').textContent = reason;
  document.getElementById('modal-app-rationale').textContent = rationale;
  document.getElementById('modal-app-price').value = (amount / 100).toFixed(2);
  document.getElementById('modal-app-qty').value = 100;
  document.getElementById('modal-approval').classList.remove('hidden');
}

function closeApprovalModal() {
  document.getElementById('modal-approval').classList.add('hidden');
  currentApprovalId = null;
}

async function submitApprovalDecision(decision) {
  if (!currentApprovalId) return;

  const notes = document.getElementById('modal-app-notes').value;
  const qty = parseInt(document.getElementById('modal-app-qty').value, 10);
  const price = parseFloat(document.getElementById('modal-app-price').value);

  try {
    const res = await fetch(`/api/approvals/${currentApprovalId}/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        decision: decision,
        reviewer_user: 'category_buyer@enterprise.internal',
        reviewer_notes: notes,
        modified_quantity: decision === 'MODIFY' ? qty : null,
        modified_price: decision === 'MODIFY' ? price : null
      })
    });

    const data = await res.json();
    closeApprovalModal();
    loadApprovals();
    loadKPIs();
    loadOrders();
    alert(`Decision '${decision}' executed for approval #${currentApprovalId}. Order updated.`);
  } catch (err) {
    alert(`Failed to submit decision: ${err.message}`);
  }
}

// 5. Purchase Orders
async function loadOrders() {
  const tbody = document.getElementById('orders-table-body');
  try {
    const res = await fetch('/api/orders');
    const orders = await res.json();

    if (!orders.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-500">No purchase orders on file.</td></tr>`;
      return;
    }

    tbody.innerHTML = orders.map(o => {
      let statusColor = 'text-slate-400 bg-slate-800';
      if (o.status === 'TRANSMITTED') statusColor = 'text-cyan-400 bg-cyan-950/40 border-cyan-800';
      if (o.status === 'ACKNOWLEDGED') statusColor = 'text-emerald-400 bg-emerald-950/40 border-emerald-800';
      if (o.status === 'PENDING_APPROVAL') statusColor = 'text-amber-400 bg-amber-950/40 border-amber-800';
      if (o.status === 'REJECTED') statusColor = 'text-rose-400 bg-rose-950/40 border-rose-800';

      const dDate = o.expected_delivery_date ? new Date(o.expected_delivery_date).toLocaleDateString() : 'N/A';

      return `
        <tr class="hover:bg-slate-900/50 transition">
          <td class="py-3 px-4 font-mono font-bold text-sky-400">${o.po_number}</td>
          <td class="py-3 px-4 font-semibold text-slate-200">Supplier #${o.supplier_id}</td>
          <td class="py-3 px-4 font-mono font-bold text-slate-100">$${o.total_amount.toFixed(2)}</td>
          <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-mono">${o.approval_tier}</span></td>
          <td class="py-3 px-4">
            <span class="px-2 py-0.5 rounded border text-[10px] font-bold ${statusColor}">${o.status}</span>
          </td>
          <td class="py-3 px-4">
            <span class="text-[10px] ${o.agent_generated ? 'text-cyan-400 font-bold' : 'text-slate-400'}">
              ${o.agent_generated ? '🤖 AI Autonomous' : '👤 Manual'}
            </span>
          </td>
          <td class="py-3 px-4 text-slate-400">${dDate}</td>
          <td class="py-3 px-4 text-right">
            <span class="text-[11px] text-slate-500 font-mono">${o.line_items ? o.line_items.length : 1} Item(s)</span>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-rose-400">Failed to load orders: ${err.message}</td></tr>`;
  }
}

// 6. Supplier Communications & Inbound Email
async function loadEmails() {
  const container = document.getElementById('emails-list-container');
  try {
    const res = await fetch('/api/emails');
    const emails = await res.json();

    if (!emails.length) {
      container.innerHTML = `<div class="text-center py-10 text-slate-500 text-xs">No email communication logs found.</div>`;
      return;
    }

    container.innerHTML = emails.map(e => {
      const isInbound = e.direction === 'INBOUND';
      let intentBadge = '';
      if (e.parsed_intent) {
        let color = 'bg-slate-800 text-slate-300';
        if (e.parsed_intent === 'SHIPMENT_DELAY') color = 'bg-rose-500/20 text-rose-400 border border-rose-500/30';
        if (e.parsed_intent === 'ORDER_CONFIRMATION') color = 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        if (e.parsed_intent === 'PRICE_INCREASE') color = 'bg-amber-500/20 text-amber-400 border border-amber-500/30';

        intentBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold ${color}">${e.parsed_intent}</span>`;
      }

      return `
        <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-2">
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="px-1.5 py-0.2 rounded text-[10px] font-bold ${isInbound ? 'bg-cyan-500/20 text-cyan-400' : 'bg-emerald-500/20 text-emerald-400'}">
                ${isInbound ? 'INBOUND' : 'OUTBOUND'}
              </span>
              <span class="font-semibold text-slate-200">${e.sender}</span>
            </div>
            <span class="text-slate-500 text-[11px]">${new Date(e.created_at).toLocaleTimeString()}</span>
          </div>

          <div class="font-bold text-slate-100 text-xs">${e.subject}</div>
          <div class="p-2.5 bg-slate-950 rounded-lg text-slate-300 text-xs font-mono whitespace-pre-line border border-slate-800/60 max-h-32 overflow-y-auto">${e.body}</div>

          <div class="flex items-center justify-between pt-1 text-[11px]">
            <div>${intentBadge}</div>
            <div class="text-slate-400">Status: <span class="text-slate-200 font-semibold">${e.status}</span></div>
          </div>
        </div>
      `;
    }).join('');

  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-center py-6 text-xs">Failed to load emails: ${err.message}</div>`;
  }
}

function loadEmailTemplate(type) {
  const sender = document.getElementById('sim-sender');
  const subject = document.getElementById('sim-subject');
  const body = document.getElementById('sim-body');

  if (type === 'delay') {
    sender.value = 'orders@novapackaging.com';
    subject.value = 'URGENT: Production Schedule Delay Notice - PO-1049';
    body.value = 'Attention Purchasing Operations,\n\nRegrettably, due to an unexpected raw cardboard pulp mill maintenance outage, shipment of PO-1049 (700 units of SKU-PACK-001) is delayed by approximately 8 business days.\nRevised target delivery date: 2026-10-18.\n\nSincerely,\nMarcus Vance - Nova Packaging Solutions';
  } else if (type === 'confirm') {
    sender.value = 'sales@apexelectronics.com';
    subject.value = 'Order Confirmation & Tracking: PO-1048 STM32F407';
    body.value = 'Dear Procurement Team,\n\nWe confirm acceptance of PO-1048 (500 units of SKU-ELEC-001 at $8.45). Goods have been packed and handed over to carrier.\nEstimated delivery date: 2026-10-02.\n\nBest regards,\nSarah Chen - Apex Electronics';
  } else if (type === 'price') {
    sender.value = 'supply@titanfasteners.com';
    subject.value = 'Notice: Contract Price Revision for Stainless Hardware';
    body.value = 'Dear Procurement Department,\n\nDue to the recent 14% global increase in nickel and raw stainless alloy indices, all future orders of SKU-MECH-001 will increase from $3.20 to $3.58 effective immediately.\n\nRegards,\nElena Rostova - Titan Fasteners';
  }
}

async function submitSimulatedEmail(e) {
  e.preventDefault();
  const sender = document.getElementById('sim-sender').value;
  const subject = document.getElementById('sim-subject').value;
  const body = document.getElementById('sim-body').value;

  try {
    const res = await fetch('/api/emails/inbound', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender, subject, body, recipient: 'procurement@enterprise.internal' })
    });
    const data = await res.json();
    loadEmails();
    loadKPIs();
    loadApprovals();
    alert('Simulated email ingested! Multi-agent triage pipeline automatically triggered.');
  } catch (err) {
    alert(`Failed to simulate email: ${err.message}`);
  }
}

function openEmailModal() {
  switchTab('emails');
}

// 7. Supplier Intelligence & Scorecard Memory
async function loadSuppliers() {
  const grid = document.getElementById('suppliers-grid');
  try {
    const res = await fetch('/api/suppliers');
    const suppliers = await res.json();

    if (!suppliers.length) {
      grid.innerHTML = `<div class="col-span-3 text-center py-10 text-slate-500 text-xs">No suppliers found.</div>`;
      return;
    }

    grid.innerHTML = suppliers.map(s => {
      return `
        <div class="glass-card p-4 rounded-xl border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="font-bold text-slate-100 text-xs flex items-center space-x-1.5">
                <span>${s.name}</span>
                ${s.is_preferred ? '<i class="fa-solid fa-star text-amber-400 text-[10px]" title="Preferred Vendor"></i>' : ''}
              </div>
              <div class="text-[11px] text-slate-400 font-mono">${s.code} • ${s.contact_email}</div>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${s.is_approved ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">
              ${s.is_approved ? 'APPROVED' : 'UNAPPROVED'}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-[11px] bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
            <div>
              <span class="text-slate-400">Reliability Score:</span>
              <div class="font-bold text-sky-400 text-sm">${s.reliability_score}%</div>
            </div>
            <div>
              <span class="text-slate-400">On-Time Delivery:</span>
              <div class="font-bold text-emerald-400 text-sm">${s.on_time_delivery_rate}%</div>
            </div>
            <div>
              <span class="text-slate-400">Payment Terms:</span>
              <div class="font-medium text-slate-200">${s.payment_terms}</div>
            </div>
            <div>
              <span class="text-slate-400">Quality Rating:</span>
              <div class="font-medium text-amber-400">${s.quality_rating} / 5.0</div>
            </div>
          </div>

          <div class="text-[11px] text-slate-400 line-clamp-2 italic">
            "${s.notes || 'Tier-1 supply partner with active master service agreement.'}"
          </div>
        </div>
      `;
    }).join('');

  } catch (err) {
    grid.innerHTML = `<div class="col-span-3 text-rose-400 text-center py-6 text-xs">Failed to load suppliers: ${err.message}</div>`;
  }
}

// 8. RAG Policy Explorer
async function loadRAGDocs() {
  const grid = document.getElementById('rag-docs-grid');
  try {
    const res = await fetch('/api/rag/docs');
    const docs = await res.json();

    grid.innerHTML = docs.map(d => {
      return `
        <div class="bg-slate-900 border border-slate-800 p-3 rounded-xl space-y-1">
          <div class="flex items-center justify-between text-[10px] text-slate-400 font-mono">
            <span>${d.id || 'DOC'}</span>
            <span class="px-1.5 py-0.2 rounded bg-indigo-950/60 text-indigo-400">${d.category}</span>
          </div>
          <div class="font-bold text-xs text-slate-200">${d.title}</div>
          <div class="text-[11px] text-slate-400 line-clamp-2">${d.content}</div>
        </div>
      `;
    }).join('');

  } catch (err) {
    console.error('Error loading RAG docs:', err);
  }
}

async function executeRAGSearch() {
  const query = document.getElementById('rag-search-input').value.trim();
  const container = document.getElementById('rag-results-container');
  if (!query) return;

  container.innerHTML = `<div class="text-center py-4 text-indigo-400 text-xs">Querying hybrid vector store...</div>`;

  try {
    const res = await fetch('/api/rag/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query, top_k: 4 })
    });
    const data = await res.json();

    if (!data.results.length) {
      container.innerHTML = `<div class="text-center py-4 text-slate-500 text-xs">No matching policy or agreement found for query.</div>`;
      return;
    }

    container.innerHTML = data.results.map(r => {
      const matchPct = Math.round(r.similarity_score * 100);
      return `
        <div class="glass-card p-4 rounded-xl border border-indigo-900/40 space-y-2">
          <div class="flex items-center justify-between">
            <div class="font-bold text-xs text-indigo-300 flex items-center space-x-2">
              <i class="fa-solid fa-file-contract text-indigo-400"></i>
              <span>${r.title} (${r.doc_id})</span>
            </div>
            <span class="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-[10px] font-bold">
              ${matchPct}% Match
            </span>
          </div>
          <div class="bg-slate-950 p-3 rounded-lg text-slate-300 text-xs whitespace-pre-line border border-slate-800/80 font-mono">
            ${r.content}
          </div>
        </div>
      `;
    }).join('');

  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-center py-4 text-xs">Search failed: ${err.message}</div>`;
  }
}

// 9. Audit Logs & Agent Reasoning Traces
async function loadAuditLogs() {
  const container = document.getElementById('audit-logs-container');
  try {
    const res = await fetch('/api/audit/logs?limit=40');
    const logs = await res.json();

    if (!logs.length) {
      container.innerHTML = `<div class="text-center py-10 text-slate-500 text-xs">No audit logs recorded yet.</div>`;
      return;
    }

    container.innerHTML = logs.map(l => {
      let statusColor = 'text-emerald-400 bg-emerald-950/40 border-emerald-800';
      if (l.status === 'WARNING') statusColor = 'text-amber-400 bg-amber-950/40 border-amber-800';
      if (l.status === 'FAILED') statusColor = 'text-rose-400 bg-rose-950/40 border-rose-800';

      return `
        <div class="glass-card p-3 rounded-xl border border-slate-800 text-xs space-y-1.5">
          <div class="flex items-center justify-between text-[11px]">
            <div class="flex items-center space-x-2">
              <span class="font-mono text-sky-400 font-bold">${l.trace_id}</span>
              <span class="text-slate-400">•</span>
              <span class="font-semibold text-slate-200">${l.agent_name}</span>
              <span class="px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-mono text-[10px]">${l.step_name}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.2 rounded border text-[10px] font-bold ${statusColor}">${l.event_type}</span>
              <span class="text-slate-500 text-[10px]">${new Date(l.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
          <div class="bg-slate-950 p-2 rounded text-[11px] font-mono text-slate-400 overflow-x-auto">
            ${l.output_payload || l.input_payload || 'Action executed successfully.'}
          </div>
        </div>
      `;
    }).join('');

  } catch (err) {
    container.innerHTML = `<div class="text-rose-400 text-center py-6 text-xs">Failed to load audit logs: ${err.message}</div>`;
  }
}
