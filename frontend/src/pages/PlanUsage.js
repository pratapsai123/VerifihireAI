import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import './PlanUsage.css';

const BILLING_LABEL = { monthly: 'Monthly', biannual: '6 Months', annual: 'Annual' };

const METHOD_ICON = {
  upi: '📱',
  card: '💳',
  netbanking: '🏦',
  wallet: '👛',
  emi: '📋',
  other: '💰',
};

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
}

function formatAmount(amount) {
  return `₹${parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function daysLeft(endDateIso) {
  if (!endDateIso) return null;
  const diff = new Date(endDateIso) - new Date();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

export default function PlanUsage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(null); // tracks which invoice is downloading
  const invoiceRef = useRef(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/plan-usage/`);
        setData(res.data);
      } catch (e) {
        setError(e.response?.data?.error || 'Failed to load plan details.');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const buildInvoiceHtml = (inv, withPrint = false) => {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Invoice #${inv.id} - VerifiHireAI</title>
        <style>
          body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 40px; color: #1e293b; background: #fff; }
          .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #4f46e5; padding-bottom: 24px; margin-bottom: 32px; }
          .logo { font-size: 26px; font-weight: 800; color: #4f46e5; }
          .logo span { color: #f59e0b; }
          .invoice-title { font-size: 32px; font-weight: 700; color: #1e293b; }
          .invoice-meta { font-size: 13px; color: #64748b; margin-top: 4px; }
          .section { margin-bottom: 28px; }
          .section-title { font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
          table { width: 100%; border-collapse: collapse; }
          th { background: #f1f5f9; padding: 12px 16px; text-align: left; font-size: 13px; font-weight: 600; color: #475569; }
          td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
          .total-row td { font-weight: 700; font-size: 16px; background: #f8fafc; }
          .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: #ede9fe; color: #7c3aed; }
          .footer { margin-top: 48px; border-top: 1px solid #e2e8f0; padding-top: 20px; font-size: 12px; color: #94a3b8; text-align: center; }
          .print-btn { display: ${withPrint ? 'none' : 'inline-flex'}; align-items: center; gap: 8px; background: #4f46e5; color: #fff; border: none; border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600; cursor: pointer; margin-bottom: 24px; }
          .print-btn:hover { background: #4338ca; }
          @media print { .print-btn { display: none !important; } }
        </style>
      </head>
      <body>
        ${!withPrint ? '<button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>' : ''}
        <div class="header">
          <div>
            <div class="logo">Verifi<span>Hire</span>AI</div>
            <div style="font-size:13px; color:#64748b; margin-top:4px;">Trust in Every Hire</div>
          </div>
          <div style="text-align:right;">
            <div class="invoice-title">TAX INVOICE</div>
            <div class="invoice-meta">Invoice #${inv.id}</div>
            <div class="invoice-meta">Date: ${formatDate(inv.created_at)}</div>
          </div>
        </div>

        <div class="section">
          <div class="section-title">Billed To</div>
          <div style="font-size:15px; font-weight:600;">${data?.company_name || ''}</div>
        </div>

        <div class="section">
          <div class="section-title">Order Details</div>
          <table>
            <thead>
              <tr>
                <th>Description</th>
                <th>Billing Cycle</th>
                <th>Period</th>
                <th style="text-align:right;">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>${inv.plan_name}</strong> Plan Subscription</td>
                <td><span class="badge">${BILLING_LABEL[inv.billing_cycle] || inv.billing_cycle}</span></td>
                <td>${formatDate(inv.plan_start_date)} → ${formatDate(inv.plan_end_date)}</td>
                <td style="text-align:right;">${formatAmount(inv.amount_paid)}</td>
              </tr>
              <tr class="total-row">
                <td colspan="3">Total Amount Paid</td>
                <td style="text-align:right; color:#4f46e5;">${formatAmount(inv.amount_paid)}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="section">
          <div class="section-title">Payment Information</div>
          <table>
            <tr><td style="color:#64748b;">Payment Method</td><td><strong>${inv.payment_method_display || inv.payment_method}</strong>${inv.payment_method_detail ? ` — ${inv.payment_method_detail}` : ''}</td></tr>
            <tr><td style="color:#64748b;">Payment ID</td><td>${inv.razorpay_payment_id || '—'}</td></tr>
            <tr><td style="color:#64748b;">Order ID</td><td>${inv.razorpay_order_id || '—'}</td></tr>
          </table>
        </div>

        <div class="footer">
          This is a computer-generated invoice and does not require a physical signature.<br/>
          VerifiHireAI | support@verifihire.ai
        </div>
        ${withPrint ? '<script>window.onload = () => { window.print(); }</script>' : ''}
      </body>
      </html>
    `;
  };

  const handleViewInvoice = (inv) => {
    const win = window.open('', '_blank');
    win.document.write(buildInvoiceHtml(inv, false));
    win.document.close();
  };

  const handleDownloadInvoice = useCallback(async (inv) => {
    setDownloading(inv.id);
    try {
      // Build hidden invoice div
      const container = document.createElement('div');
      container.style.cssText = 'position:fixed;left:-9999px;top:0;width:794px;background:#fff;padding:40px;font-family:Segoe UI,Arial,sans-serif;color:#1e293b;box-sizing:border-box;';
      container.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px solid #4f46e5;padding-bottom:24px;margin-bottom:32px;">
          <div>
            <div style="font-size:26px;font-weight:800;color:#4f46e5;">Verifi<span style="color:#f59e0b;">Hire</span>AI</div>
            <div style="font-size:13px;color:#64748b;margin-top:4px;">Trust in Every Hire</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:28px;font-weight:700;">TAX INVOICE</div>
            <div style="font-size:13px;color:#64748b;margin-top:4px;">Invoice #${inv.id}</div>
            <div style="font-size:13px;color:#64748b;">Date: ${formatDate(inv.created_at)}</div>
          </div>
        </div>
        <div style="margin-bottom:24px;">
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Billed To</div>
          <div style="font-size:15px;font-weight:600;">${data?.company_name || ''}</div>
        </div>
        <div style="margin-bottom:24px;">
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Order Details</div>
          <table style="width:100%;border-collapse:collapse;">
            <thead><tr style="background:#f1f5f9;">
              <th style="padding:12px;text-align:left;font-size:13px;">Description</th>
              <th style="padding:12px;text-align:left;font-size:13px;">Billing Cycle</th>
              <th style="padding:12px;text-align:left;font-size:13px;">Period</th>
              <th style="padding:12px;text-align:right;font-size:13px;">Amount</th>
            </tr></thead>
            <tbody>
              <tr>
                <td style="padding:12px;border-bottom:1px solid #e2e8f0;"><strong>${inv.plan_name}</strong> Plan Subscription</td>
                <td style="padding:12px;border-bottom:1px solid #e2e8f0;"><span style="background:#ede9fe;color:#7c3aed;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;">${BILLING_LABEL[inv.billing_cycle] || inv.billing_cycle}</span></td>
                <td style="padding:12px;border-bottom:1px solid #e2e8f0;font-size:13px;">${formatDate(inv.plan_start_date)} → ${formatDate(inv.plan_end_date)}</td>
                <td style="padding:12px;border-bottom:1px solid #e2e8f0;text-align:right;">${formatAmount(inv.amount_paid)}</td>
              </tr>
              <tr style="background:#f8fafc;">
                <td colspan="3" style="padding:12px;font-weight:700;">Total Amount Paid</td>
                <td style="padding:12px;text-align:right;font-weight:700;font-size:16px;color:#4f46e5;">${formatAmount(inv.amount_paid)}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div style="margin-bottom:24px;">
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Payment Information</div>
          <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:10px;color:#64748b;width:160px;">Payment Method</td><td style="padding:10px;"><strong>${inv.payment_method_display || inv.payment_method}</strong>${inv.payment_method_detail ? ' — ' + inv.payment_method_detail : ''}</td></tr>
            <tr><td style="padding:10px;color:#64748b;">Payment ID</td><td style="padding:10px;">${inv.razorpay_payment_id || '—'}</td></tr>
            <tr><td style="padding:10px;color:#64748b;">Order ID</td><td style="padding:10px;">${inv.razorpay_order_id || '—'}</td></tr>
          </table>
        </div>
        <div style="margin-top:48px;border-top:1px solid #e2e8f0;padding-top:20px;font-size:12px;color:#94a3b8;text-align:center;">
          This is a computer-generated invoice and does not require a physical signature.<br/>VerifiHireAI | support@verifihire.ai
        </div>
      `;
      document.body.appendChild(container);

      const canvas = await html2canvas(container, { scale: 2, useCORS: true, logging: false });
      document.body.removeChild(container);

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: 'a4' });
      const pdfW = pdf.internal.pageSize.getWidth();
      const pdfH = (canvas.height * pdfW) / canvas.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfW, pdfH);
      pdf.save(`VerifiHire-Invoice-${inv.id}-${inv.plan_name}.pdf`);
    } catch (e) {
      console.error('PDF generation failed:', e);
      alert('PDF generation failed. Please try the View button and print from there.');
    } finally {
      setDownloading(null);
    }
  }, [data]);

  if (loading) {
    return (
      <div className="pu-loading">
        <div className="pu-spinner"></div>
        <p>Loading your plan details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pu-error">
        <span>⚠️</span>
        <p>{error}</p>
      </div>
    );
  }

  const { plan, plan_start_date, plan_end_date, invoices = [], company_name } = data;
  const remaining = daysLeft(plan_end_date);
  const totalDays = plan_start_date && plan_end_date
    ? Math.ceil((new Date(plan_end_date) - new Date(plan_start_date)) / (1000 * 60 * 60 * 24))
    : 30;
  const progressPct = remaining !== null ? Math.max(0, Math.round((remaining / totalDays) * 100)) : 100;

  return (
    <div className="pu-container">
      {/* ── Page Header ── */}
      <div className="pu-page-header">
        <div>
          <h1 className="pu-page-title">Plan &amp; Billing</h1>
          <p className="pu-page-subtitle">{company_name} — subscription details &amp; invoice history</p>
        </div>
      </div>

      {/* ── Active Plan Card ── */}
      {plan ? (
        <div className="pu-plan-card" style={{ '--plan-color': plan.color_theme || '#4f46e5' }}>
          <div className="pu-plan-badge">Active Plan</div>
          <div className="pu-plan-top">
            <div>
              <h2 className="pu-plan-name">{plan.name}</h2>
              <p className="pu-plan-price">
                {parseFloat(plan.base_price_monthly) === 0 ? 'Free' :
                  parseFloat(plan.base_price_monthly) < 0 ? 'Custom Pricing' :
                  `₹${parseFloat(plan.base_price_monthly).toLocaleString('en-IN')}/mo`}
              </p>
            </div>
            <div className="pu-dates-grid">
              <div className="pu-date-box">
                <span className="pu-date-label">Start Date</span>
                <span className="pu-date-val">{formatDate(plan_start_date)}</span>
              </div>
              <div className="pu-date-box">
                <span className="pu-date-label">End Date</span>
                <span className="pu-date-val">{formatDate(plan_end_date)}</span>
              </div>
            </div>
          </div>

          {/* Subscription progress bar */}
          <div className="pu-progress-wrap">
            <div className="pu-progress-labels">
              <span>{remaining !== null ? `${remaining} days remaining` : 'Active'}</span>
              <span>{progressPct}%</span>
            </div>
            <div className="pu-progress-track">
              <div className="pu-progress-bar" style={{ width: `${progressPct}%` }}></div>
            </div>
          </div>
        </div>
      ) : (
        <div className="pu-no-plan">No active subscription found.</div>
      )}

      {/* ── Features included ── */}
      {plan && plan.features && plan.features.length > 0 && (
        <div className="pu-section">
          <h3 className="pu-section-title">What's Included</h3>
          <div className="pu-features-grid">
            {plan.features.map((f, i) => (
              <div key={i} className="pu-feature-chip">
                <span className="pu-feature-check">✓</span>
                {f}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Quota limits ── */}
      {plan && (
        <div className="pu-section">
          <h3 className="pu-section-title">Invitation Quotas</h3>
          <div className="pu-quota-grid">
            {[
              { label: 'AI Assessments', val: plan.max_ai_assessments },
              { label: 'AI Interviews', val: plan.max_ai_interviews },
              { label: 'Coding Assessments', val: plan.max_coding_assessments },
              { label: 'Live Interviews', val: plan.max_live_interviews },
              { label: 'Resume Screening', val: plan.max_resume_screening },
              { label: 'HR Managers', val: plan.max_hr_managers },
              { label: 'HR Members', val: plan.max_hrs },
              { label: 'Interviewers', val: plan.max_interviewers },
              { label: 'Custom Questions', val: plan.max_custom_questions },
            ].map(({ label, val }) => (
              <div key={label} className="pu-quota-card">
                <span className="pu-quota-val">{val === 0 ? '∞' : val === -1 ? 'Unlimited' : val}</span>
                <span className="pu-quota-label">{label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Invoice History ── */}
      <div className="pu-section" ref={invoiceRef}>
        <h3 className="pu-section-title">Billing History</h3>
        {invoices.length === 0 ? (
          <div className="pu-no-invoices">No invoices found yet.</div>
        ) : (
          <div className="pu-invoice-table-wrap">
            <table className="pu-invoice-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Plan</th>
                  <th>Billing Cycle</th>
                  <th>Period</th>
                  <th>Payment Method</th>
                  <th>Amount</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td>
                      <div className="pu-inv-id">#{inv.id}</div>
                      <div className="pu-inv-date">{formatDate(inv.created_at)}</div>
                    </td>
                    <td><span className="pu-plan-pill">{inv.plan_name}</span></td>
                    <td><span className="pu-cycle-pill">{BILLING_LABEL[inv.billing_cycle] || inv.billing_cycle}</span></td>
                    <td>
                      <div className="pu-period">
                        <span>{formatDate(inv.plan_start_date)}</span>
                        <span className="pu-period-arrow">→</span>
                        <span>{formatDate(inv.plan_end_date)}</span>
                      </div>
                    </td>
                    <td>
                      <div className="pu-method">
                        <span className="pu-method-icon">{METHOD_ICON[inv.payment_method] || '💰'}</span>
                        <div>
                          <div className="pu-method-name">{inv.payment_method_display || inv.payment_method}</div>
                          {inv.payment_method_detail && <div className="pu-method-detail">{inv.payment_method_detail}</div>}
                        </div>
                      </div>
                    </td>
                    <td><span className="pu-amount">{formatAmount(inv.amount_paid)}</span></td>
                    <td>
                      <div className="pu-action-btns">
                        <button className="pu-view-btn" onClick={() => handleViewInvoice(inv)}>
                          👁 View
                        </button>
                        <button className="pu-download-btn" onClick={() => handleDownloadInvoice(inv)} disabled={downloading === inv.id}>
                          {downloading === inv.id ? '⏳ Generating...' : '⬇ Download PDF'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
