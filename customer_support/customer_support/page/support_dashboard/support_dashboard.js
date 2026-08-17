frappe.pages["support_dashboard"].on_page_load = function (wrapper) {
	render_dashboard(wrapper);
};

frappe.pages["support_dashboard"].refresh = function (wrapper) {
	render_dashboard(wrapper);
};

function build_top_customers_spotlight(rows) {
	if (!rows.length) {
		return '<div class="tc-empty">No customer activity in this period.</div>';
	}
	const top = rows[0];
	const rest = rows.slice(1);
	const denom = top.open || 1;
	const list_html = rest
		.map((r, i) => {
			const rank = i + 2;
			const pct = Math.min((r.open / denom) * 100, 100);
			const barWidth = Math.max(pct, r.open ? 4 : 0);
			return `
		<div class="tcl-row">
			<div class="tcl-rank">${rank}</div>
			<div class="tcl-main">
				<div class="tcl-name">${r.customer}</div>
				<div class="tcl-bar"><span style="width:${barWidth}%"></span></div>
			</div>
			<div class="tcl-tier">${r.tier}</div>
			<div class="tcl-count">${r.open}</div>
		</div>`;
		})
		.join("");
	return `
		<div class="tc-spotlight">
			<div class="tc-spotlight-card">
				<div class="tc-spotlight-circle"></div>
				<div class="tc-spotlight-label">HIGHEST VOLUME</div>
				<div class="tc-spotlight-name">${top.customer}</div>
				<div class="tc-spotlight-tier">${top.tier} plan</div>
				<div class="tc-spotlight-number">${top.open}</div>
				<div class="tc-spotlight-caption">open tickets</div>
				<div class="tc-spotlight-divider"></div>
				<div class="tc-spotlight-stats">
					<div class="tc-spotlight-stat">
						<div class="tc-spotlight-stat-value">${top.resolved_30d}</div>
						<div class="tc-spotlight-stat-label">resolved 30d</div>
					</div>
					<div class="tc-spotlight-stat">
						<div class="tc-spotlight-stat-value">${top.avg_response}</div>
						<div class="tc-spotlight-stat-label">avg response</div>
					</div>
					<div class="tc-spotlight-stat">
						<div class="tc-spotlight-stat-value">${top.urgent_share}%</div>
						<div class="tc-spotlight-stat-label">urgent share</div>
					</div>
				</div>
			</div>
			<div class="tc-list">${list_html}</div>
		</div>`;
}

function build_top_customers_donut_grid(rows) {
	if (!rows.length) {
		return '<div class="tcd-empty">No customer activity in this period.</div>';
	}
	const PRIO = [
		{ key: "urgent", color: "#ef4444", label: "Urgent" },
		{ key: "high", color: "#f59e0b", label: "High" },
		{ key: "medium", color: "#3b82f6", label: "Medium" },
		{ key: "low", color: "#2db89a", label: "Low" },
	];
	return rows
		.map((r, i) => {
			const u = r.urgent || 0, h = r.high || 0, m = r.medium || 0, l = r.low || 0;
			const total = u + h + m + l;
			const rank = i + 1;
			const donut = render_donut(u, h, m, l, total);
			const legend = PRIO
				.filter((p) => (r[p.key] || 0) > 0)
				.map(
					(p) =>
						`<div class="tcd-legend-item"><span class="tcd-dot" style="background:${p.color}"></span><span class="tcd-label">${p.label}</span><span class="tcd-value">${r[p.key]}</span></div>`
				)
				.join("");
			return `
		<div class="tcd-card">
			<div class="tcd-card-head">
				<div class="tcd-id">
					<div class="tcd-avatar">${r.initials}</div>
					<div class="tcd-meta">
						<div class="tcd-name">${r.customer}</div>
						<div class="tcd-tier">${r.tier}</div>
					</div>
				</div>
				<div class="tcd-rank">#${rank}</div>
			</div>
			<div class="tcd-card-body">
				<div class="tcd-donut">${donut}<div class="tcd-total">${total}</div></div>
				<div class="tcd-legend">${legend}</div>
			</div>
		</div>`;
		})
		.join("");
}

function render_donut(u, h, m, l, total) {
	const r = 22;
	const c = 2 * Math.PI * r;
	const size = 60;
	const cx = size / 2;
	const cy = size / 2;
	const sw = 8;
	if (!total) {
		return `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" role="img" aria-label="No tickets">
			<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#e2e8f0" stroke-width="${sw}"></circle>
		</svg>`;
	}
	const segs = [
		{ v: u, color: "#ef4444" },
		{ v: h, color: "#f59e0b" },
		{ v: m, color: "#3b82f6" },
		{ v: l, color: "#2db89a" },
	].filter((s) => s.v > 0);
	const circ = c;
	let acc = 0;
	const circles = segs
		.map((s) => {
			const len = (s.v / total) * circ;
			const offset = -acc;
			acc += len;
			return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${s.color}" stroke-width="${sw}" stroke-dasharray="${len} ${circ - len}" stroke-dashoffset="${offset}" transform="rotate(-90 ${cx} ${cy})" stroke-linecap="butt"></circle>`;
		})
		.join("");
	return `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" role="img" aria-label="Priority breakdown">
		<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#f1f5f9" stroke-width="${sw}"></circle>
		${circles}
	</svg>`;
}

function relative_time(iso) {
	if (!iso) {
		return "—";
	}
	const d = new Date(iso.replace(" ", "T"));
	const diff = (Date.now() - d.getTime()) / 1000;
	if (diff < 60) {
		return "just now";
	}
	if (diff < 3600) {
		return Math.floor(diff / 60) + "m ago";
	}
	if (diff < 86400) {
		return Math.floor(diff / 3600) + "h ago";
	}
	return Math.floor(diff / 86400) + "d ago";
}

function build_customers_rows(rows) {
	if (!rows.length) {
		return '<tr><td colspan="6" class="customers-empty">No customer activity in this period.</td></tr>';
	}
	return rows
		.map(
			(r) => `
		<tr data-priority="${r.priority || ""}" data-customer="${(r.customer || "").toLowerCase()}">
			<td>
				<div class="customer-cell">
					<div class="customer-avatar">${r.initials}</div>
					<div class="customer-meta">
						<div class="customer-name">${r.customer}</div>
						<div class="customer-tier">${r.tier}</div>
					</div>
				</div>
			</td>
			<td>${
				r.priority
					? `<span class="priority-pill" data-prio="${r.priority}"><span class="dot"></span>${r.priority}</span>`
					: '<span class="rel">—</span>'
			}</td>
			<td class="num">${r.open}</td>
			<td>
				<div class="resolved-cell">
					<div class="resolved-top"><span class="num">${r.resolved_30d}</span> · <span class="rate">${r.resolved_rate}%</span></div>
					<div class="resolved-bar"><span style="width:${Math.min(r.resolved_rate, 100)}%"></span></div>
				</div>
			</td>
			<td class="num">${r.avg_response}</td>
			<td class="rel">${relative_time(r.last_ticket_dt)}</td>
		</tr>`
		)
		.join("");
}

function export_customers_csv(rows) {
	const headers = [
		"Customer",
		"Tier",
		"Priority",
		"Open",
		"Resolved 30D",
		"Resolved Rate %",
		"Avg Response",
		"Last Ticket",
		"Total",
	];
	const esc = (v) => '"' + String(v == null ? "" : v).replace(/"/g, '""') + '"';
	const lines = [headers.join(",")].concat(
		rows.map((r) =>
			[
				esc(r.customer),
				esc(r.tier),
				esc(r.priority || ""),
				r.open,
				r.resolved_30d,
				r.resolved_rate,
				esc(r.avg_response),
				esc(r.last_ticket_dt || ""),
				r.total,
			].join(",")
		)
	);
	const blob = new Blob(["﻿" + lines.join("\n")], { type: "text/csv;charset=utf-8;" });
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = "customers_overview.csv";
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
}

function render_dashboard(wrapper) {
	$(wrapper).html("");
	frappe.call({
		method: "customer_support.customer_support.page.support_dashboard.support_dashboard.get_ticket_summary",
		callback: function (r) {
			const summary = r.message || {};
			const status_counts = summary.status_counts || {};
			const status_deltas = summary.status_deltas || { Open: 0, Resolved: 0, Closed: 0 };
			const priority_counts = summary.priority_counts || { Urgent: 0, High: 0, Medium: 0, Low: 0 };
			const closed_this_month = summary.closed_this_month || 0;
			const queue_total = summary.ticket_queue || 0;

			const cards = [
				{ key: "Open", icon: "🗨", tone: "red", value: status_counts.Open || 0, delta: status_deltas.Open || 0, prefix: "↑ " },
				{ key: "Resolved", icon: "✓", tone: "green", value: status_counts.Resolved || 0, delta: status_deltas.Resolved || 0, prefix: "↑ " },
				{ key: "Closed", icon: "✓", tone: "gray", value: status_counts.Closed || 0, delta: 0, prefix: "" },
				{ key: "Replied", icon: "💬", tone: "blue", value: status_counts.Replied || 0, delta: 0, prefix: "" },
				{ key: "Completed", icon: "✔", tone: "teal", value: status_counts.Completed || 0, delta: 0, prefix: "" },
				{ key: "Out of Scope", icon: "⊘", tone: "slate", value: status_counts["Out of Scope"] || 0, delta: 0, prefix: "" },
				{ key: "Not Completed", icon: "✕", tone: "amber", value: status_counts["Not Completed"] || 0, delta: 0, prefix: "" },
			];

			const summary_html = cards
				.map((card) => {
					const delta_text =
						card.key === "Closed"
							? `<div class="metric-status"><span>this month • <strong>${closed_this_month}</strong> total</span></div>`
							: card.delta >= 0 && (card.key === "Open" || card.key === "Resolved")
							? `<div class="metric-status"><span class="trend up ${card.tone}">${card.prefix}</span><span>${card.delta} since yesterday</span></div>`
							: "";

					return `
						<div class="metric-card">
							<div class="metric-header">
								<div class="metric-title">${card.key}</div>
								<div class="metric-icon ${card.tone}">${card.icon}</div>
							</div>
							<div class="metric-value">${card.value}</div>
							${delta_text}
							<div class="metric-progress ${card.tone}"><span style="width:100%"></span></div>
						</div>
					`;
				})
				.join("");

			const priorities = [
				{ key: "Urgent", color: "#ef4444", value: priority_counts.Urgent || 0 },
				{ key: "High", color: "#f59e0b", value: priority_counts.High || 0 },
				{ key: "Medium", color: "#3b82f6", value: priority_counts.Medium || 0 },
				{ key: "Low", color: "#2db89a", value: priority_counts.Low || 0 },
			];

			const total = priorities.reduce((sum, item) => sum + item.value, 0) || queue_total;
			const track_html = priorities
				.map((item) => {
					const width = total ? (item.value / total) * 100 : 0;
					return `<span class="priority-segment" style="background:${item.color}; width:${width}%"></span>`;
				})
				.join("");

			const legend_html = priorities
				.map(
					(item) => `
					<div class="legend-item">
						<span class="legend-dot" style="background:${item.color}"></span>
						<span class="legend-label">${item.key}</span>
						<span class="legend-value">${item.value}</span>
					</div>
				`
				)
				.join("");

			const top_customers = summary.top_customers || [];
			const customers = summary.customers || [];

			const now = new Date();
			const date_str = now.toLocaleDateString("en-GB", {
				weekday: "long",
				day: "numeric",
				month: "long",
				year: "numeric",
			});

			$(wrapper).html(`
				<style>
					.support-dashboard-page {
						font-family: Inter, "Segoe UI", sans-serif;
						background:
							radial-gradient(1200px 600px at 0% 0%, rgba(99,102,241,0.08), transparent 60%),
							radial-gradient(1000px 500px at 100% 0%, rgba(236,72,153,0.07), transparent 60%),
							linear-gradient(180deg, #f5f7fb 0%, #eef1f6 100%);
						min-height: 100vh;
						padding: 14px 18px 18px;
						color: #0f172a;
					}
					.support-dashboard-header {
						margin-bottom: 14px;
						display: flex;
						align-items: flex-end;
						justify-content: space-between;
						gap: 16px;
						flex-wrap: wrap;
					}
					.support-dashboard-header h1 {
						margin: 0 0 6px;
						font-size: clamp(1.4rem, 2vw, 1.75rem);
						font-weight: 800;
						letter-spacing: -0.035em;
						background: linear-gradient(135deg, #0f172a 0%, #475569 100%);
						-webkit-background-clip: text;
						background-clip: text;
						color: transparent;
					}
					.support-dashboard-subtitle { color: #64748b; font-size: 12.5px; font-weight: 500; }
					.support-dashboard-subtitle .sync-dot {
						display: inline-block;
						width: 8px; height: 8px;
						border-radius: 50%;
						background: #10b981;
						box-shadow: 0 0 0 3px rgba(16,185,129,0.15);
						margin-right: 6px;
						vertical-align: middle;
						animation: pulse 2s ease-in-out infinite;
					}
					@keyframes pulse {
						0%, 100% { opacity: 1; transform: scale(1); }
						50% { opacity: 0.6; transform: scale(0.85); }
					}

					.dashboard-summary {
						display: grid;
						grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
						gap: 12px;
						margin-bottom: 12px;
					}

					.metric-card {
						position: relative;
						background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.65) 100%);
						border: 1px solid rgba(255,255,255,0.8);
						border-radius: 16px;
						box-shadow:
							0 1px 2px rgba(15,23,42,0.04),
							0 8px 24px -12px rgba(15,23,42,0.12);
						backdrop-filter: blur(8px);
						-webkit-backdrop-filter: blur(8px);
						padding: 13px 15px 11px;
						min-height: 100px;
						display: flex;
						flex-direction: column;
						overflow: hidden;
						transition: transform 0.2s ease, box-shadow 0.2s ease;
						animation: fadeUp 0.4s ease both;
					}
					.metric-card:hover {
						transform: translateY(-2px);
						box-shadow:
							0 2px 4px rgba(15,23,42,0.05),
							0 16px 32px -12px rgba(15,23,42,0.18);
					}
					.metric-card::before {
						content: "";
						position: absolute;
						top: 0; left: 0;
						width: 4px;
						height: 100%;
						border-radius: 16px 0 0 16px;
						opacity: 0.9;
					}
					.metric-card.red::before    { background: linear-gradient(180deg, #f43f5e, #e11d48); }
					.metric-card.green::before  { background: linear-gradient(180deg, #10b981, #059669); }
					.metric-card.gray::before   { background: linear-gradient(180deg, #94a3b8, #64748b); }
					.metric-card.blue::before   { background: linear-gradient(180deg, #3b82f6, #2563eb); }
					.metric-card.teal::before   { background: linear-gradient(180deg, #14b8a6, #0d9488); }
					.metric-card.slate::before  { background: linear-gradient(180deg, #64748b, #475569); }
					.metric-card.amber::before  { background: linear-gradient(180deg, #f59e0b, #d97706); }

					.metric-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
					.metric-title { font-size: 13px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.04em; }
					.metric-icon {
						width: 30px; height: 30px;
						border-radius: 8px;
						display: flex; align-items: center; justify-content: center;
						font-size: 13px; font-weight: 700;
						box-shadow: inset 0 0 0 1px rgba(255,255,255,0.6);
					}
					.metric-icon.red    { background: linear-gradient(135deg, #ffe4e6, #fecdd3); color: #be123c; }
					.metric-icon.green  { background: linear-gradient(135deg, #d1fae5, #a7f3d0); color: #047857; }
					.metric-icon.gray   { background: linear-gradient(135deg, #f1f5f9, #e2e8f0); color: #475569; }
					.metric-icon.blue   { background: linear-gradient(135deg, #dbeafe, #bfdbfe); color: #1d4ed8; }
					.metric-icon.teal   { background: linear-gradient(135deg, #ccfbf1, #99f6e4); color: #0f766e; }
					.metric-icon.slate  { background: linear-gradient(135deg, #e2e8f0, #cbd5e1); color: #334155; }
					.metric-icon.amber  { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #b45309; }

					.metric-value {
						font-size: clamp(1.5rem, 2.2vw, 1.9rem);
						line-height: 1;
						font-weight: 800;
						letter-spacing: -0.04em;
						color: #0f172a;
						margin-bottom: 5px;
					}
					.metric-status { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #64748b; margin-top: auto; }
					.trend { font-size: 13px; font-weight: 700; }
					.trend.up.red { color: #dc2626; }
					.trend.up.green { color: #059669; }
					.trend.up.blue { color: #2563eb; }
					.trend.up.teal { color: #0d9488; }

					.metric-progress {
						margin-top: 8px;
						height: 5px;
						background: rgba(15,23,42,0.06);
						border-radius: 999px;
						overflow: hidden;
						width: 100%;
					}
					.metric-progress > span { display: block; height: 100%; border-radius: inherit; }
					.metric-progress.red > span    { background: linear-gradient(90deg, #fb7185, #e11d48); }
					.metric-progress.green > span  { background: linear-gradient(90deg, #34d399, #059669); }
					.metric-progress.gray > span   { background: linear-gradient(90deg, #cbd5e1, #64748b); }
					.metric-progress.blue > span   { background: linear-gradient(90deg, #60a5fa, #2563eb); }
					.metric-progress.teal > span   { background: linear-gradient(90deg, #2dd4bf, #0d9488); }
					.metric-progress.slate > span  { background: linear-gradient(90deg, #cbd5e1, #475569); }
					.metric-progress.amber > span  { background: linear-gradient(90deg, #fbbf24, #d97706); }

					.priority-panel {
						position: relative;
						background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.65) 100%);
						border: 1px solid rgba(255,255,255,0.8);
						border-radius: 16px;
						box-shadow:
							0 1px 2px rgba(15,23,42,0.04),
							0 8px 24px -12px rgba(15,23,42,0.12);
						backdrop-filter: blur(8px);
						-webkit-backdrop-filter: blur(8px);
						padding: 14px 18px 12px;
						margin-bottom: 12px;
						animation: fadeUp 0.5s ease both;
					}
					.panel-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
					.panel-header h2 { margin: 0; font-size: clamp(1rem, 1.4vw, 1.15rem); font-weight: 700; letter-spacing: -0.03em; color: #0f172a; }
					.panel-meta {
						color: #475569;
						font-size: 12.5px;
						font-weight: 600;
						background: linear-gradient(135deg, #eef2ff, #fdf2f8);
						border: 1px solid rgba(99,102,241,0.15);
						padding: 4px 10px;
						border-radius: 999px;
					}
					.priority-track {
						width: 100%;
						height: 12px;
						display: flex;
						border-radius: 999px;
						overflow: hidden;
						background: rgba(15,23,42,0.06);
						margin-bottom: 10px;
						box-shadow: inset 0 1px 2px rgba(15,23,42,0.06);
					}
					.priority-segment { height: 100%; display: block; transition: filter 0.2s ease; }
					.priority-segment:hover { filter: brightness(1.08); }

					.priority-legend { display: flex; flex-wrap: wrap; gap: 14px 18px; align-items: center; }

					.chart-panel {
						position: relative;
						background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.65) 100%);
						border: 1px solid rgba(255,255,255,0.8);
						border-radius: 16px;
						box-shadow:
							0 1px 2px rgba(15,23,42,0.04),
							0 8px 24px -12px rgba(15,23,42,0.12);
						backdrop-filter: blur(8px);
						-webkit-backdrop-filter: blur(8px);
						padding: 18px 20px 14px;
						animation: fadeUp 0.6s ease both;
					}
					.chart-wrapper { padding-top: 4px; }
					.chart-empty {
						color: #64748b;
						font-size: 13px;
						padding: 32px 0;
						text-align: center;
					}

					.tc-panel {
						position: relative;
						background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.65) 100%);
						border: 1px solid rgba(255,255,255,0.8);
						border-radius: 16px;
						box-shadow:
							0 1px 2px rgba(15,23,42,0.04),
							0 8px 24px -12px rgba(15,23,42,0.12);
						backdrop-filter: blur(8px);
						-webkit-backdrop-filter: blur(8px);
						padding: 16px 20px 18px;
						margin-bottom: 12px;
						animation: fadeUp 0.55s ease both;
					}
					.tc-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
					.tc-header h2 { margin: 0 0 4px; font-size: clamp(1.15rem, 1.6vw, 1.35rem); font-weight: 700; letter-spacing: -0.03em; color: #0f172a; }
					.tc-subtitle { color: #64748b; font-size: 12.5px; font-weight: 500; }
					.tc-subhead {
						font-size: 12px;
						font-weight: 700;
						letter-spacing: 0.04em;
						text-transform: uppercase;
						color: #64748b;
						margin: 18px 0 10px;
					}
					.tc-period-pill {
						background: #f1f5f9;
						color: #0f172a;
						border: 1px solid #e2e8f0;
						border-radius: 999px;
						padding: 6px 12px;
						font-size: 12px;
						font-weight: 600;
						letter-spacing: -0.01em;
					}

					.tc-spotlight {
						display: grid;
						grid-template-columns: 340px minmax(0, 1fr);
						gap: 28px;
						align-items: stretch;
					}
					@media (max-width: 1100px) { .tc-spotlight { grid-template-columns: 1fr; gap: 24px; } }

					.tc-spotlight-card {
						position: relative;
						background: linear-gradient(155deg, #4f46e5 0%, #4338ca 45%, #312e81 100%);
						border-radius: 16px;
						padding: 22px 22px 20px;
						color: #fff;
						overflow: hidden;
						min-height: 400px;
						box-shadow: 0 20px 40px -20px rgba(67,56,202,0.55);
						animation: fadeUp 0.5s ease both;
					}
					.tc-spotlight-circle {
						position: absolute;
						top: -90px;
						right: -90px;
						width: 240px;
						height: 240px;
						border-radius: 50%;
						background: rgba(255,255,255,0.08);
						pointer-events: none;
					}
					.tc-spotlight-label {
						font-size: 11px;
						font-weight: 700;
						letter-spacing: 0.18em;
						opacity: 0.85;
						margin-bottom: 10px;
						position: relative;
					}
					.tc-spotlight-name {
						font-size: 28px;
						font-weight: 700;
						letter-spacing: -0.02em;
						line-height: 1.1;
						position: relative;
					}
					.tc-spotlight-tier {
						font-size: 13px;
						opacity: 0.85;
						font-weight: 500;
						margin-top: 4px;
						position: relative;
					}
					.tc-spotlight-number {
						font-size: 54px;
						font-weight: 700;
						line-height: 1;
						margin-top: 32px;
						font-variant-numeric: tabular-nums;
						letter-spacing: -0.03em;
						position: relative;
					}
					.tc-spotlight-caption {
						font-size: 13px;
						opacity: 0.85;
						margin-top: 4px;
						font-weight: 500;
						position: relative;
					}
					.tc-spotlight-divider {
						height: 1px;
						background: rgba(255,255,255,0.18);
						margin: 22px 0 16px;
						position: relative;
					}
					.tc-spotlight-stats {
						display: grid;
						grid-template-columns: repeat(3, minmax(0, 1fr));
						gap: 12px;
						position: relative;
					}
					.tc-spotlight-stat-value {
						font-size: 18px;
						font-weight: 700;
						font-variant-numeric: tabular-nums;
						letter-spacing: -0.01em;
					}
					.tc-spotlight-stat-label {
						font-size: 11px;
						opacity: 0.8;
						margin-top: 2px;
						font-weight: 500;
					}

					.tc-list {
						display: flex;
						flex-direction: column;
					}
					.tcl-row {
						display: grid;
						grid-template-columns: 28px minmax(0,1fr) 90px 48px;
						gap: 14px;
						align-items: center;
						padding: 11px 2px;
						border-bottom: 1px solid #f1f5f9;
						animation: fadeUp 0.5s ease both;
					}
					.tcl-row:nth-child(1) { animation-delay: 0.04s; }
					.tcl-row:nth-child(2) { animation-delay: 0.08s; }
					.tcl-row:nth-child(3) { animation-delay: 0.12s; }
					.tcl-row:nth-child(4) { animation-delay: 0.16s; }
					.tcl-row:nth-child(5) { animation-delay: 0.20s; }
					.tcl-row:nth-child(6) { animation-delay: 0.24s; }
					.tcl-row:nth-child(7) { animation-delay: 0.28s; }
					.tcl-row:nth-child(8) { animation-delay: 0.32s; }
					.tcl-row:nth-child(9) { animation-delay: 0.36s; }
					.tcl-row:nth-child(10) { animation-delay: 0.40s; }
					.tcl-row:nth-child(11) { animation-delay: 0.44s; }
					.tcl-row:nth-child(12) { animation-delay: 0.48s; }
					.tcl-row:nth-child(13) { animation-delay: 0.52s; }
					.tcl-row:last-child { border-bottom: none; }
					.tcl-rank {
						font-family: "SF Mono", "Menlo", monospace;
						font-size: 12.5px;
						font-weight: 600;
						color: #94a3b8;
						text-align: center;
					}
					.tcl-main { min-width: 0; }
					.tcl-name {
						font-weight: 700;
						color: #0f172a;
						font-size: 14px;
						letter-spacing: -0.01em;
						margin-bottom: 7px;
						white-space: nowrap;
						overflow: hidden;
						text-overflow: ellipsis;
					}
					.tcl-bar {
						height: 6px;
						background: #eef2ff;
						border-radius: 999px;
						overflow: hidden;
					}
					.tcl-bar span {
						display: block;
						height: 100%;
						background: linear-gradient(90deg, #818cf8, #4f46e5);
						border-radius: 999px;
					}
					.tcl-tier {
						color: #64748b;
						font-size: 12.5px;
						font-weight: 500;
						text-align: right;
					}
					.tcl-count {
						color: #0f172a;
						font-weight: 700;
						font-size: 16px;
						font-variant-numeric: tabular-nums;
						text-align: right;
					}

					.tc-empty { color: #64748b; font-size: 13px; padding: 28px 0; text-align: center; }

					.tc-grid {
						display: grid;
						grid-template-columns: repeat(4, minmax(0, 1fr));
						gap: 12px;
					}
					@media (max-width: 1100px) { .tc-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
					@media (max-width: 860px)  { .tc-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
					@media (max-width: 560px)  { .tc-grid { grid-template-columns: 1fr; } }

					.tcd-card {
						background: #ffffff;
						border: 1px solid #e2e8f0;
						border-radius: 12px;
						padding: 12px 14px 12px;
						box-shadow: 0 1px 2px rgba(15,23,42,0.03);
						transition: transform 0.18s ease, box-shadow 0.18s ease;
						animation: fadeUp 0.5s ease both;
					}
					.tcd-card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px -10px rgba(15,23,42,0.18); }
					.tcd-card:nth-child(1) { animation-delay: 0.02s; }
					.tcd-card:nth-child(2) { animation-delay: 0.06s; }
					.tcd-card:nth-child(3) { animation-delay: 0.10s; }
					.tcd-card:nth-child(4) { animation-delay: 0.14s; }
					.tcd-card:nth-child(5) { animation-delay: 0.18s; }
					.tcd-card:nth-child(6) { animation-delay: 0.22s; }
					.tcd-card:nth-child(7) { animation-delay: 0.26s; }
					.tcd-card:nth-child(8) { animation-delay: 0.30s; }
					.tcd-card:nth-child(9) { animation-delay: 0.34s; }
					.tcd-card:nth-child(10) { animation-delay: 0.38s; }
					.tcd-card:nth-child(11) { animation-delay: 0.42s; }
					.tcd-card:nth-child(12) { animation-delay: 0.46s; }

					.tcd-card-head {
						display: flex; align-items: flex-start; justify-content: space-between; gap: 10px;
						margin-bottom: 10px;
					}
					.tcd-id { display: flex; align-items: center; gap: 10px; min-width: 0; }
					.tcd-avatar {
						width: 36px; height: 36px; border-radius: 10px;
						display: flex; align-items: center; justify-content: center;
						font-weight: 700; font-size: 12px; color: #fff;
						background: linear-gradient(135deg, #818cf8, #4338ca);
						box-shadow: 0 2px 6px rgba(99,102,241,0.25);
						flex-shrink: 0;
					}
					.tcd-meta { min-width: 0; }
					.tcd-name {
						font-weight: 700; color: #0f172a; font-size: 14px;
						white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
						letter-spacing: -0.01em;
					}
					.tcd-tier { color: #64748b; font-size: 11.5px; font-weight: 500; margin-top: 2px; }
					.tcd-rank {
						color: #2563eb; font-weight: 700; font-size: 12.5px;
						font-variant-numeric: tabular-nums; flex-shrink: 0;
					}

					.tcd-card-body {
						display: flex; align-items: center; gap: 14px;
					}
					.tcd-donut {
						position: relative; width: 60px; height: 60px; flex-shrink: 0;
						display: flex; align-items: center; justify-content: center;
					}
					.tcd-donut svg { display: block; }
					.tcd-total {
						position: absolute; inset: 0;
						display: flex; align-items: center; justify-content: center;
						font-weight: 700; color: #0f172a; font-size: 14px;
						font-variant-numeric: tabular-nums; letter-spacing: -0.02em;
					}
					.tcd-legend {
						display: flex; flex-direction: column; gap: 3px; min-width: 0; flex: 1;
					}
					.tcd-legend-item {
						display: grid; grid-template-columns: 8px 1fr auto;
						align-items: center; gap: 8px;
						font-size: 12px; color: #334155; font-weight: 500;
					}
					.tcd-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
					.tcd-label { white-space: nowrap; }
					.tcd-value { font-weight: 700; color: #0f172a; font-variant-numeric: tabular-nums; }
					.tcd-empty { color: #64748b; font-size: 13px; padding: 28px 0; text-align: center; }

					.customers-panel {
						position: relative;
						background: linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.65) 100%);
						border: 1px solid rgba(255,255,255,0.8);
						border-radius: 16px;
						box-shadow:
							0 1px 2px rgba(15,23,42,0.04),
							0 8px 24px -12px rgba(15,23,42,0.12);
						backdrop-filter: blur(8px);
						-webkit-backdrop-filter: blur(8px);
						padding: 16px 20px 12px;
						margin-top: 12px;
						animation: fadeUp 0.7s ease both;
					}
					.customers-header { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom: 10px; gap: 12px; }
					.customers-header h2 { margin: 0 0 4px; font-size: clamp(1.15rem, 1.6vw, 1.35rem); font-weight: 700; letter-spacing: -0.03em; color: #0f172a; }
					.customers-subtitle { color: #64748b; font-size: 12.5px; font-weight: 500; }

					.customers-controls { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
					.customers-search { position: relative; flex: 1; min-width: 220px; }
					.customers-search .search-icon { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); font-size: 12px; opacity: 0.55; pointer-events: none; }
					.customers-search input {
						width: 100%; padding: 9px 12px 9px 32px;
						border-radius: 10px; border: 1px solid #e2e8f0;
						background: #f8fafc; font-size: 13px; color: #0f172a;
						outline: none; transition: border 0.15s ease, background 0.15s ease;
					}
					.customers-search input::placeholder { color: #94a3b8; }
					.customers-search input:focus { border-color: #818cf8; background: #fff; }

					.customers-filters { display: flex; gap: 6px; }
					.filter-pill {
						padding: 7px 14px; border-radius: 8px;
						border: 1px solid #e2e8f0; background: #fff;
						font-size: 12.5px; font-weight: 600; color: #475569;
						cursor: pointer; transition: all 0.15s ease;
					}
					.filter-pill:hover { border-color: #cbd5e1; }
					.filter-pill.active {
						background: linear-gradient(135deg, #eef2ff, #e0e7ff);
						border-color: #818cf8; color: #4338ca;
					}

					.export-csv-btn {
						padding: 7px 14px; border-radius: 8px;
						border: 1px solid #c7d2fe; background: #eef2ff;
						font-size: 12.5px; font-weight: 600; color: #4338ca;
						cursor: pointer; transition: all 0.15s ease;
					}
					.export-csv-btn:hover { background: #e0e7ff; }

					.customers-table { width: 100%; border-collapse: collapse; font-size: 13px; }
					.customers-table thead th {
						text-align: left; padding: 8px 12px;
						font-size: 10.5px; font-weight: 600; color: #64748b;
						text-transform: uppercase; letter-spacing: 0.06em;
						border-bottom: 1px solid #e2e8f0;
					}
					.customers-table tbody tr {
						border-bottom: 1px solid #f1f5f9;
						transition: background 0.12s ease;
					}
					.customers-table tbody tr:hover { background: rgba(248,250,252,0.7); }
					.customers-table tbody tr:last-child { border-bottom: none; }
					.customers-table tbody td { padding: 11px 12px; vertical-align: middle; color: #1f2937; }

					.customer-cell { display: flex; align-items: center; gap: 12px; }
					.customer-avatar {
						width: 40px; height: 40px; border-radius: 10px;
						display: flex; align-items: center; justify-content: center;
						font-weight: 700; font-size: 13px; color: #fff;
						background: linear-gradient(135deg, #818cf8, #4338ca);
						flex-shrink: 0; box-shadow: 0 2px 6px rgba(99,102,241,0.25);
					}
					.customer-meta { display: flex; flex-direction: column; min-width: 0; }
					.customer-name { font-weight: 600; color: #0f172a; font-size: 13.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
					.customer-tier { color: #64748b; font-size: 11.5px; font-weight: 500; }

					.priority-pill { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; font-size: 12.5px; }
					.priority-pill .dot { width: 8px; height: 8px; border-radius: 50%; }
					.priority-pill[data-prio="Urgent"] { color: #dc2626; } .priority-pill[data-prio="Urgent"] .dot { background: #dc2626; }
					.priority-pill[data-prio="High"]   { color: #d97706; } .priority-pill[data-prio="High"]   .dot { background: #f59e0b; }
					.priority-pill[data-prio="Medium"] { color: #2563eb; } .priority-pill[data-prio="Medium"] .dot { background: #3b82f6; }
					.priority-pill[data-prio="Low"]    { color: #16a34a; } .priority-pill[data-prio="Low"]    .dot { background: #22c55e; }

					.num { font-weight: 600; color: #0f172a; font-variant-numeric: tabular-nums; }
					.rel { color: #475569; font-size: 12.5px; }

					.resolved-cell { display: flex; flex-direction: column; gap: 6px; min-width: 150px; }
					.resolved-top { display: flex; align-items: center; gap: 4px; font-size: 12.5px; color: #475569; }
					.resolved-top .num { font-weight: 700; color: #0f172a; }
					.resolved-top .rate { color: #16a34a; font-weight: 600; }
					.resolved-bar { width: 100%; height: 6px; background: #ecfdf5; border-radius: 999px; overflow: hidden; }
					.resolved-bar > span { display: block; height: 100%; background: linear-gradient(90deg, #34d399, #10b981); border-radius: inherit; }

					.customers-empty { text-align: center; color: #64748b; padding: 28px 0; }
					.legend-item {
						display: inline-flex;
						align-items: center;
						gap: 8px;
						font-size: 12.5px;
						color: #1f2937;
						font-weight: 500;
						padding: 4px 10px 4px 8px;
						border-radius: 999px;
						background: rgba(248,250,252,0.7);
						border: 1px solid rgba(15,23,42,0.05);
						transition: background 0.15s ease;
					}
					.legend-item:hover { background: #fff; }
					.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; box-shadow: 0 0 0 2px rgba(255,255,255,0.9); }
					.legend-label { font-weight: 600; color: #334155; }
					.legend-value { color: #64748b; margin-left: 2px; font-variant-numeric: tabular-nums; }

					@keyframes fadeUp {
						from { opacity: 0; transform: translateY(6px); }
						to   { opacity: 1; transform: translateY(0); }
					}
					.metric-card:nth-child(1) { animation-delay: 0.02s; }
					.metric-card:nth-child(2) { animation-delay: 0.06s; }
					.metric-card:nth-child(3) { animation-delay: 0.10s; }
					.metric-card:nth-child(4) { animation-delay: 0.14s; }
					.metric-card:nth-child(5) { animation-delay: 0.18s; }
					.metric-card:nth-child(6) { animation-delay: 0.22s; }
					.metric-card:nth-child(7) { animation-delay: 0.26s; }

					@media (max-width: 980px) {
						.dashboard-summary { grid-template-columns: 1fr; }
						.panel-header { flex-direction: column; align-items: flex-start; }
					}
				</style>
				<div class="support-dashboard-page">
					<div class="support-dashboard-header">
						<div>
							<h1>Support overview</h1>
							<div class="support-dashboard-subtitle"><span class="sync-dot"></span>${date_str} · Last synced just now</div>
						</div>
					</div>
					<div class="dashboard-summary">${summary_html}</div>
					<div class="priority-panel">
						<div class="panel-header">
							<h2>Open ticket load by priority</h2>
							<div class="panel-meta">${total} tickets in queue</div>
						</div>
						<div class="priority-track">${track_html}</div>
						<div class="priority-legend">${legend_html}</div>
					</div>
					<div class="tc-panel">
						<div class="tc-header">
							<div>
								<h2>Top customers by ticket volume</h2>
								<div class="tc-subtitle">Spotlight on the #1 account, priority split per account below</div>
							</div>
							<div class="tc-period-pill">Last 90 days</div>
						</div>
						<div class="tc-spotlight-wrap">${build_top_customers_spotlight(top_customers)}</div>
						<div class="tc-subhead">Priority split by account</div>
						<div class="tc-grid">${build_top_customers_donut_grid(top_customers)}</div>
					</div>
					<div class="customers-panel">
						<div class="customers-header">
							<div>
								<h2>Customers</h2>
								<div class="customers-subtitle">Full account detail across support activity</div>
							</div>
							<div class="panel-meta">Last 90 days</div>
						</div>
						<div class="customers-controls">
							<div class="customers-search">
								<span class="search-icon">🔍</span>
								<input id="customers-search-input" type="text" placeholder="Search customers..." />
							</div>
							<div class="customers-filters">
								<button class="filter-pill active" data-priority="All">All</button>
								<button class="filter-pill" data-priority="Urgent">Urgent</button>
								<button class="filter-pill" data-priority="High">High</button>
								<button class="filter-pill" data-priority="Medium">Medium</button>
								<button class="filter-pill" data-priority="Low">Low</button>
							</div>
							<button class="export-csv-btn" id="customers-export-btn">Export CSV</button>
						</div>
						<table class="customers-table">
							<thead>
								<tr>
									<th>Customer</th>
									<th>Priority</th>
									<th>Open</th>
									<th>Resolved 30D</th>
									<th>Avg Response</th>
									<th>Last Ticket</th>
								</tr>
							</thead>
							<tbody id="customers-tbody"></tbody>
						</table>
					</div>
				</div>
			`);

			const $wrap = $(wrapper);
			const $tbody = $wrap.find("#customers-tbody");
			$tbody.html(build_customers_rows(customers));

			function get_filtered() {
				const q = ($wrap.find("#customers-search-input").val() || "").toLowerCase().trim();
				const prio = $wrap.find(".filter-pill.active").data("priority") || "All";
				return customers.filter((r) => {
					const match_search = !q || (r.customer || "").toLowerCase().includes(q);
					const match_prio = prio === "All" || r.priority === prio;
					return match_search && match_prio;
				});
			}

			function rerender() {
				$tbody.html(build_customers_rows(get_filtered()));
			}

			$wrap.find("#customers-search-input").on("input", rerender);
			$wrap.find(".filter-pill").on("click", function () {
				$wrap.find(".filter-pill").removeClass("active");
				$(this).addClass("active");
				rerender();
			});
			$wrap.find("#customers-export-btn").on("click", function () {
				export_customers_csv(get_filtered());
			});
		},
	});
}
