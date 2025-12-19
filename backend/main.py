from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from .database import init_db, save_entry, get_all_entries, update_entry, get_entry_by_id, get_entries_by_date
from .excel_handler import update_excel_report
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Entry(BaseModel):
    date: str
    zone: str
    clerk: str
    vehicle: str
    route: str
    time_out: Optional[str] = None
    time_in: Optional[str] = None
    tare_time: Optional[str] = None
    fld_wgt: float
    fact_wgt: float
    scorch_kg: float
    quality_pct: float

class ReportRequest(BaseModel):
    date: str
    entries: List[Entry]

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/entries")
def get_entries(date: Optional[str] = None):
    if date:
        return get_entries_by_date(date)
    return get_all_entries()

@app.post("/api/submit")
def submit_report(request: ReportRequest, background_tasks: BackgroundTasks):
    # Save to database first
    for entry in request.entries:
        save_entry(entry.dict())
    
    # Fetch authoritative data from DB for this date
    # This ensures we capture all entries for the day and any DB-generated fields
    db_entries = get_entries_by_date(request.date)
    
    if not db_entries:
        # Fallback to request entries if DB read fails (unlikely if save worked)
        db_entries = [entry.dict() for entry in request.entries]

    # Generate Excel Report using DB data
    try:
        xl_file = update_excel_report(db_entries, request.date)
        pdf_file = xl_file if xl_file.endswith(".pdf") else None
        
        # Generate HTML Report using DB data
        html_file = save_html_report_to_file(request.date, db_entries)
        
        attachments = []
        if pdf_file: attachments.append(pdf_file)
        if html_file: attachments.append(html_file)
        
        if attachments:
            background_tasks.add_task(send_report_email, attachments, request.date)
            
        return {"status": "success", "file": xl_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preview/{file_type}")
def preview_report(file_type: str, request: ReportRequest):
    # 1. Save to database first (Ensure "Real Data")
    for entry in request.entries:
        save_entry(entry.dict())
    
    # 2. Fetch authoritative data
    db_entries = get_entries_by_date(request.date)
    if not db_entries:
        db_entries = [entry.dict() for entry in request.entries]

    try:
        file_path = None
        media_type = ""
        filename = ""

        if file_type == 'pdf':
            # Generate PDF via Excel handler
            generated_file = update_excel_report(db_entries, request.date)
            if generated_file.endswith(".pdf"):
                file_path = generated_file
                media_type = "application/pdf"
                filename = os.path.basename(file_path)
            else:
                 raise HTTPException(status_code=500, detail="PDF generation failed (returned Excel path)")
        
        elif file_type == 'html':
            # Generate Interactive HTML
            file_path = save_html_report_to_file(request.date, db_entries)
            media_type = "text/html"
            filename = os.path.basename(file_path)
            
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Use 'pdf' or 'html'")

        if file_path and os.path.exists(file_path):
            return FileResponse(file_path, media_type=media_type, filename=filename)
        else:
            raise HTTPException(status_code=500, detail=f"Failed to generate {file_type.upper()} file")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/entries/{entry_id}")
def update_existing_entry(entry_id: int, entry: Entry):
    db_entry = get_entry_by_id(entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # 48-hour check
    created_at = datetime.fromisoformat(db_entry['created_at'].replace(' ', 'T'))
    if datetime.now() - created_at > timedelta(hours=48):
        raise HTTPException(status_code=403, detail="Edit window (48h) has expired")
    
    update_entry(entry_id, entry.dict())
    return {"status": "success"}

def send_report_email(attachments: List[str], report_date: str):
    # RESTRICTED TO THIS EMAIL FOR DEVELOPMENT
    receiver_email = "dmronoh.12@gmail.com"
    
    # Placeholder SMTP - User needs to provide credentials for actual sending
    # For now, we'll log the attempt
    print(f"DEBUG: Attempting to send report with attachments {attachments} to {receiver_email}")
    
    # Logic for actual sending (requires SMTP credentials)
    # try:
    #     msg = MIMEMultipart()
    #     msg['From'] = "reports@greenfieldstea.co.ke"
    #     msg['To'] = receiver_email
    #     msg['Subject'] = f"GL Collection Report - {report_date}"
    #     msg.attach(MIMEText("Please find attached the GL collection report (PDF) and Interactive Dashboard (HTML) for today."))
    #     
    #     for file_path in attachments:
    #         if os.path.exists(file_path):
    #             with open(file_path, "rb") as f:
    #                 part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
    #                 part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    #                 msg.attach(part)
    #                 
    #     # server = smtplib.SMTP('smtp.gmail.com', 587)
    #     # server.starttls()
    #     # server.login("user", "pass")
    #     # server.send_message(msg)
    #     # server.quit()
    # except Exception as e:
    #     print(f"Email failed: {e}")

@app.get("/api/analysis")
def get_analysis_data():
    return get_all_entries()

@app.get("/api/metadata")
def get_metadata():
    entries = get_all_entries()
    zones = sorted(list(set(e['zone'] for e in entries if e['zone'])))
    routes = sorted(list(set(e['route'] for e in entries if e['route'])))
    vehicles = sorted(list(set(e['vehicle'] for e in entries if e['vehicle'])))
    return {
        "zones": zones,
        "routes": routes,
        "vehicles": vehicles
    }

@app.get("/api/reports")
def list_reports():
    records_dir = "PDF Records"
    if not os.path.exists(records_dir):
        return []
    files = [f for f in os.listdir(records_dir) if f.endswith(".pdf")]
    # Extract dates or just return filenames
    return sorted(files, reverse=True)

from fastapi.responses import FileResponse
@app.get("/api/reports/{filename}")
def get_report(filename: str):
    file_path = os.path.join("PDF Records", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

from fastapi.responses import HTMLResponse
@app.get("/api/reports/html/{report_date}", response_class=HTMLResponse)
def get_html_report(report_date: str):
    entries = get_entries_by_date(report_date)
    if not entries:
        raise HTTPException(status_code=404, detail="No data for this date")
    
    # Simple Interactive HTML Template
    html_content = generate_html_content(report_date, entries)
    return html_content

def save_html_report_to_file(report_date: str, entries: List[dict]) -> str:
    html_content = generate_html_content(report_date, entries)
    filename = f"Report_{report_date}.html"
    file_path = os.path.join("PDF Records", filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return file_path

def generate_html_content(report_date: str, entries: List[dict]) -> str:
    import json
    
    # Serialize entries to JSON
    json_data = json.dumps(entries, default=str)
    
    # HTML Template with placeholders
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GL Collection Report - {{REPORT_DATE}}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root { --primary: #16a34a; --bg: #020617; --glass: rgba(255,255,255,0.03); --border: rgba(255,255,255,0.05); }
            body { background-color: var(--bg); color: #e2e8f0; font-family: 'Inter', system-ui, sans-serif; }
            .glass { background: var(--glass); backdrop-filter: blur(10px); border: 1px solid var(--border); }
            .card { transition: transform 0.2s; }
            .card:hover { transform: translateY(-2px); border-color: rgba(255,255,255,0.1); }
            select, input { background: rgba(0,0,0,0.3); border: 1px solid var(--border); color: white; padding: 0.5rem; border-radius: 0.5rem; outline: none; }
            select:focus, input:focus { border-color: var(--primary); }
            th { text-align: left; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; padding: 1rem; }
            td { padding: 1rem; border-top: 1px solid var(--border); }
            tr:hover td { background: rgba(255,255,255,0.02); }
        </style>
    </head>
    <body class="min-h-screen p-4 md:p-8">
        <div class="max-w-7xl mx-auto space-y-8">
            <!-- Header -->
            <header class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-bold text-white tracking-tight">GL Collection Report</h1>
                    <p class="text-slate-500 mt-1 uppercase tracking-widest text-xs font-semibold">{{REPORT_DATE}}</p>
                </div>
                <div class="text-left md:text-right">
                    <p class="text-green-500 font-bold text-xl">GREENFIELDS TEA</p>
                    <p class="text-slate-500 text-xs">Interactive Digital Dashboard</p>
                </div>
            </header>

            <!-- Filters -->
            <div class="glass p-4 rounded-xl flex flex-wrap gap-4 items-center">
                <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-slate-500 uppercase">Filter By:</span>
                </div>
                <select id="zoneFilter" onchange="applyFilters()" class="min-w-[150px]">
                    <option value="">All Zones</option>
                </select>
                <select id="routeFilter" onchange="applyFilters()" class="min-w-[150px]">
                    <option value="">All Routes</option>
                </select>
                <input type="text" id="searchFilter" onkeyup="applyFilters()" placeholder="Search clerk, vehicle..." class="min-w-[200px]">
                <div class="ml-auto text-xs text-slate-400">
                    Showing <span id="countDisplay" class="font-bold text-white">0</span> records
                </div>
            </div>

            <!-- KPI Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="glass card p-6 rounded-2xl">
                    <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Total Weight</p>
                    <p class="text-3xl font-bold text-white"><span id="totalWeight">0</span> <span class="text-sm font-medium text-slate-500">KG</span></p>
                </div>
                <div class="glass card p-6 rounded-2xl">
                    <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Avg Quality</p>
                    <p class="text-3xl font-bold text-white"><span id="avgQuality">0</span>%</p>
                </div>
                <div class="glass card p-6 rounded-2xl">
                    <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Routes Active</p>
                    <p class="text-3xl font-bold text-white" id="totalRoutes">0</p>
                </div>
                <div class="glass card p-6 rounded-2xl">
                    <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Entry Count</p>
                    <p class="text-3xl font-bold text-white" id="totalCount">0</p>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass p-6 rounded-2xl">
                    <h3 class="text-sm font-bold text-slate-400 uppercase mb-4">Weight Distribution by Zone</h3>
                    <div class="h-64">
                         <canvas id="zoneChart"></canvas>
                    </div>
                </div>
                <div class="glass p-6 rounded-2xl">
                    <h3 class="text-sm font-bold text-slate-400 uppercase mb-4">Quality vs Weight (Top Routes)</h3>
                    <div class="h-64">
                        <canvas id="routeChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Data Table -->
            <div class="glass rounded-2xl overflow-hidden overflow-x-auto">
                <table class="w-full text-left font-mono text-sm">
                    <thead class="bg-white/5">
                        <tr>
                            <th class="cursor-pointer hover:text-white transition-colors" onclick="handleSort('zone')">
                                Zone <span id="sort-zone" class="ml-1 text-primary-400"></span>
                            </th>
                            <th class="cursor-pointer hover:text-white transition-colors" onclick="handleSort('route')">
                                Route <span id="sort-route" class="ml-1 text-primary-400"></span>
                            </th>
                            <th class="cursor-pointer hover:text-white transition-colors" onclick="handleSort('vehicle')">
                                Vehicle <span id="sort-vehicle" class="ml-1 text-primary-400"></span>
                            </th>
                            <th class="cursor-pointer hover:text-white transition-colors" onclick="handleSort('clerk')">
                                Clerk <span id="sort-clerk" class="ml-1 text-primary-400"></span>
                            </th>
                            <th class="text-right cursor-pointer hover:text-white transition-colors" onclick="handleSort('fact_wgt')">
                                Weight (KG) <span id="sort-fact_wgt" class="ml-1 text-primary-400"></span>
                            </th>
                            <th class="text-right cursor-pointer hover:text-white transition-colors" onclick="handleSort('quality_pct')">
                                Quality % <span id="sort-quality_pct" class="ml-1 text-primary-400"></span>
                            </th>
                        </tr>
                    </thead>
                    <tbody id="tableBody" class="divide-y divide-white/5 text-slate-300">
                        <!-- Rows rendered by JS -->
                    </tbody>
                </table>
            </div>
            
            <div class="flex justify-center gap-4 text-xs font-medium text-slate-500 uppercase tracking-widest py-8">
                <span>&copy; 2025 Greenfield Tea Factory</span>
                <span>&bull;</span>
                <span>Generated via Greenfield Report System</span>
            </div>
        </div>

        <script>
            // Embedded Data
            const rawData = {{JSON_DATA}};
            
            // State
            let filteredData = [...rawData];
            let currentSort = { field: 'zone', asc: true }; // Default sort
            let zoneChartInstance = null;
            let routeChartInstance = null;

            // Initialize
            document.addEventListener('DOMContentLoaded', () => {
                populateDropdowns();
                applyFilters();
            });

            function populateDropdowns() {
                const zones = [...new Set(rawData.map(d => d.zone))].sort();
                const routes = [...new Set(rawData.map(d => d.route))].sort();
                
                const zSelect = document.getElementById('zoneFilter');
                zones.forEach(z => {
                    const opt = document.createElement('option');
                    opt.value = z;
                    opt.textContent = z;
                    zSelect.appendChild(opt);
                });

                const rSelect = document.getElementById('routeFilter');
                routes.forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r;
                    opt.textContent = r;
                    rSelect.appendChild(opt);
                });
            }

            function applyFilters() {
                const zVal = document.getElementById('zoneFilter').value;
                const rVal = document.getElementById('routeFilter').value;
                const sVal = document.getElementById('searchFilter').value.toLowerCase();

                filteredData = rawData.filter(d => {
                    const matchZone = !zVal || d.zone === zVal;
                    const matchRoute = !rVal || d.route === rVal;
                    const matchSearch = !sVal || 
                        (d.clerk && d.clerk.toLowerCase().includes(sVal)) || 
                        (d.vehicle && d.vehicle.toLowerCase().includes(sVal));
                    return matchZone && matchRoute && matchSearch;
                });

                renderDashboard();
            }

            function handleSort(field) {
                if (currentSort.field === field) {
                    currentSort.asc = !currentSort.asc;
                } else {
                    currentSort.field = field;
                    currentSort.asc = true;
                }
                renderDashboard();
            }

            function renderDashboard() {
                // 0. Update Sort Icons
                ['zone', 'route', 'vehicle', 'clerk', 'fact_wgt', 'quality_pct'].forEach(f => {
                    const el = document.getElementById('sort-' + f);
                    if (el) el.textContent = '';
                });
                const sortIcon = document.getElementById('sort-' + currentSort.field);
                if (sortIcon) sortIcon.textContent = currentSort.asc ? '↑' : '↓';

                // 1. Sort Data
                if (currentSort.field) {
                    filteredData.sort((a, b) => {
                        let valA = a[currentSort.field];
                        let valB = b[currentSort.field];
                        
                        // Handle numbers
                        if (typeof valA === 'number' && typeof valB === 'number') {
                            return currentSort.asc ? valA - valB : valB - valA;
                        }
                        
                        // Handle strings
                        valA = String(valA || '').toLowerCase();
                        valB = String(valB || '').toLowerCase();
                        if (valA < valB) return currentSort.asc ? -1 : 1;
                        if (valA > valB) return currentSort.asc ? 1 : -1;
                        return 0;
                    });
                }

                // 2. KPIs
                const totalWgt = filteredData.reduce((sum, d) => sum + (d.fact_wgt || 0), 0);
                const avgQual = filteredData.length ? filteredData.reduce((sum, d) => sum + (d.quality_pct || 0), 0) / filteredData.length : 0;
                const uniqueRoutes = new Set(filteredData.map(d => d.route)).size;

                document.getElementById('totalWeight').textContent = totalWgt.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1});
                document.getElementById('avgQuality').textContent = avgQual.toFixed(1);
                document.getElementById('totalRoutes').textContent = uniqueRoutes;
                document.getElementById('totalCount').textContent = filteredData.length;
                document.getElementById('countDisplay').textContent = filteredData.length;

                // 3. Table
                const tbody = document.getElementById('tableBody');
                tbody.innerHTML = filteredData.map(d => `
                    <tr class="hover:bg-white/5 transition-colors">
                        <td class="font-medium text-white">${d.zone}</td>
                        <td>${d.route}</td>
                        <td>${d.vehicle}</td>
                        <td>${d.clerk}</td>
                        <td class="text-right text-green-400 font-bold">${d.fact_wgt.toFixed(1)}</td>
                        <td class="text-right">${d.quality_pct}%</td>
                    </tr>
                `).join('');

                // 4. Charts
                renderCharts();
            }

            function renderCharts() {
                // Prepare Data
                const zoneMap = {};
                const routeMap = {};
                
                filteredData.forEach(d => {
                    // Zone Aggregation
                    if (!zoneMap[d.zone]) zoneMap[d.zone] = 0;
                    zoneMap[d.zone] += d.fact_wgt;
                    
                    // Route Aggregation (Top 10 by weight)
                    if (!routeMap[d.route]) routeMap[d.route] = { wgt: 0, qual: 0, count: 0 };
                    routeMap[d.route].wgt += d.fact_wgt;
                    routeMap[d.route].qual += d.quality_pct;
                    routeMap[d.route].count++;
                });

                // Zone Chart Data
                const zoneLabels = Object.keys(zoneMap).sort();
                const zoneValues = zoneLabels.map(l => zoneMap[l]);

                // Route Chart Data (Top 7)
                const topRoutes = Object.entries(routeMap)
                    .sort((a, b) => b[1].wgt - a[1].wgt)
                    .slice(0, 7);
                const routeLabels = topRoutes.map(x => x[0]);
                const routeWeights = topRoutes.map(x => x[1].wgt);
                const routeQuals = topRoutes.map(x => (x[1].qual / x[1].count).toFixed(1));

                // Destroy old instances
                if (zoneChartInstance) zoneChartInstance.destroy();
                if (routeChartInstance) routeChartInstance.destroy();

                // Render Zone Chart (Bar)
                zoneChartInstance = new Chart(document.getElementById('zoneChart'), {
                    type: 'bar',
                    data: {
                        labels: zoneLabels,
                        datasets: [{
                            label: 'Weight (KG)',
                            data: zoneValues,
                            backgroundColor: '#22c55e',
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                            x: { grid: { display: false } }
                        }
                    }
                });

                // Render Route Chart (Line/Mixed)
                routeChartInstance = new Chart(document.getElementById('routeChart'), {
                    type: 'line',
                    data: {
                        labels: routeLabels,
                        datasets: [
                            {
                                label: 'Avg Quality (%)',
                                data: routeQuals,
                                borderColor: '#eab308',
                                backgroundColor: '#eab308',
                                yAxisID: 'y1',
                                tension: 0.3
                            },
                            {
                                label: 'Total Weight (KG)',
                                data: routeWeights,
                                backgroundColor: 'rgba(34, 197, 94, 0.2)',
                                borderColor: 'rgba(34, 197, 94, 0.5)',
                                fill: true,
                                yAxisID: 'y',
                                tension: 0.3
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: { mode: 'index', intersect: false },
                        scales: {
                            y: { 
                                type: 'linear', display: true, position: 'left',
                                grid: { color: 'rgba(255,255,255,0.05)' } 
                            },
                            y1: { 
                                type: 'linear', display: true, position: 'right', grid: { display: false },
                                min: 0, max: 100
                            },
                            x: { grid: { display: false } }
                        }
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    
    return html_template.replace("{{REPORT_DATE}}", report_date).replace("{{JSON_DATA}}", json_data)

@app.post("/api/reports/send/{report_date}")
def trigger_email(report_date: str, background_tasks: BackgroundTasks):
    # This just triggers the existing email logic for a specific date
    # In a real app, we'd regenerate the PDF first to ensure it's current
    entries = get_entries_by_date(report_date)
    if not entries:
         raise HTTPException(status_code=404, detail="No data for this date")
    
    xl_file = update_excel_report(entries, report_date)
    pdf_file = xl_file if xl_file.endswith(".pdf") else None
    
    # Generate HTML Report
    html_file = save_html_report_to_file(report_date, entries)
    
    attachments = []
    if pdf_file: attachments.append(pdf_file)
    if html_file: attachments.append(html_file)
    
    if attachments:
        background_tasks.add_task(send_report_email, attachments, report_date)
        return {"status": "success", "message": f"Report sent to dmronoh.12@gmail.com"}
    
    raise HTTPException(status_code=500, detail="Failed to generate report for email")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
