import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    BarChart3,
    FileSpreadsheet,
    Plus,
    Trash2,
    Send,
    History,
    Calendar as CalendarIcon,
    CheckCircle2,
    AlertCircle,
    PieChart as PieChartIcon,
    Clock,
    ExternalLink,
    Eye,
    Edit2,
    FileText,
    Layout
} from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    LineChart,
    Line,
    PieChart,
    Pie,
    Cell,
    Legend,
    AreaChart,
    Area,
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis
} from 'recharts';
import AdvancedAnalytics from './AdvancedAnalytics';

interface Entry {
    id?: number;
    date: string;
    zone: string;
    clerk: string;
    vehicle: string;
    route: string;
    time_out?: string;
    time_in?: string;
    tare_time?: string;
    fld_wgt: number;
    fact_wgt: number;
    scorch_kg: number;
    quality_pct: number;
}

const ZONES = [
    "ZONE 1 NORAH",
    "ZONE 2",
    "ZONE 3 DENNIS",
    "ZONE 4 WESTONE"
];

const COLORS = ['#22c55e', '#3b82f6', '#a855f7', '#f59e0b', '#ec4899'];

const canEdit = (createdAt?: string) => {
    if (!createdAt) return false;
    const created = new Date(createdAt.replace(' ', 'T'));
    const now = new Date();
    const diff = (now.getTime() - created.getTime()) / (1000 * 60 * 60);
    return diff < 48;
};

function App() {
    const [activeTab, setActiveTab] = useState<'entry' | 'history' | 'analysis' | 'reports'>('entry');
    const [isEditMode, setIsEditMode] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [entries, setEntries] = useState<Entry[]>([{
        date: new Date().toISOString().split('T')[0],
        zone: '',
        clerk: '',
        vehicle: '',
        route: '',
        time_out: '06:00',
        time_in: '',
        tare_time: '',
        fld_wgt: 0,
        fact_wgt: 0,
        scorch_kg: 0,
        quality_pct: 0
    }]);
    const [history, setHistory] = useState<Entry[]>([]);
    const [reportFiles, setReportFiles] = useState<string[]>([]);
    const [metadata, setMetadata] = useState<{ zones: string[], routes: string[], vehicles: string[] }>({
        zones: ZONES,
        routes: [],
        vehicles: []
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    useEffect(() => {
        fetchHistory();
        fetchMetadata();
        fetchReports();
    }, []);

    // Load existing entries when date changes
    useEffect(() => {
        const currentDate = entries[0].date;
        fetchEntriesForDate(currentDate);
    }, [entries[0].date]);

    const fetchEntriesForDate = async (date: string) => {
        try {
            const res = await axios.get(`/api/entries?date=${date}`);
            if (res.data.length > 0) {
                setEntries(res.data);
            } else {
                setEntries([{
                    date: date,
                    zone: '',
                    clerk: '',
                    vehicle: '',
                    route: '',
                    time_out: '06:00',
                    time_in: '',
                    tare_time: '',
                    fld_wgt: 0,
                    fact_wgt: 0,
                    scorch_kg: 0,
                    quality_pct: 0
                }]);
            }
        } catch (err) {
            console.error("Failed to fetch entries for date", err);
        }
    };

    const fetchHistory = async () => {
        try {
            const res = await axios.get('/api/entries');
            setHistory(res.data);
        } catch (err) {
            console.error("Failed to fetch history", err);
        }
    };

    const fetchMetadata = async () => {
        try {
            const res = await axios.get('/api/metadata');
            setMetadata(prev => ({
                ...prev,
                ...res.data,
                zones: res.data.zones.length > 0 ? res.data.zones : ZONES
            }));
        } catch (err) {
            console.error("Failed to fetch metadata", err);
        }
    };

    const fetchReports = async () => {
        try {
            const res = await axios.get('/api/reports');
            setReportFiles(res.data);
        } catch (err) {
            console.error("Failed to fetch reports", err);
        }
    };

    const addRow = () => {
        setEntries([...entries, {
            ...entries[entries.length - 1],
            clerk: '',
            vehicle: '',
            route: '',
            time_out: '06:00',
            time_in: '',
            tare_time: '',
            fld_wgt: 0,
            fact_wgt: 0,
            scorch_kg: 0,
            quality_pct: 0
        }]);
    };

    const removeRow = (index: number) => {
        if (entries.length > 1) {
            setEntries(entries.filter((_, i) => i !== index));
        }
    };

    const updateEntry = (index: number, field: keyof Entry, value: any) => {
        const newEntries = [...entries];
        newEntries[index] = { ...newEntries[index], [field]: value };
        setEntries(newEntries);
    };

    const handleEdit = (entry: Entry) => {
        setIsEditMode(true);
        setEditingId(entry.id || null);
        setEntries([entry]);
        setActiveTab('entry');
    };

    const cancelEdit = () => {
        setIsEditMode(false);
        setEditingId(null);
        setEntries([{
            date: new Date().toISOString().split('T')[0],
            zone: '',
            clerk: '',
            vehicle: '',
            route: '',
            time_out: '06:00',
            time_in: '',
            tare_time: '',
            fld_wgt: 0,
            fact_wgt: 0,
            scorch_kg: 0,
            quality_pct: 0
        }]);
    };

    const previewReport = async (type: 'pdf' | 'html') => {
        if (!entries[0]?.date) {
            setMessage({ type: 'error', text: 'Please select a date' });
            return;
        }
        setLoading(true);
        try {
            const response = await axios.post(`/api/preview/${type}`, {
                date: entries[0].date,
                entries: entries
            }, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data], { type: type === 'pdf' ? 'application/pdf' : 'text/html' }));
            window.open(url, '_blank');
            setMessage({ type: 'success', text: `Preview ${type.toUpperCase()} generated!` });
            setTimeout(() => setMessage(null), 3000);
        } catch (error) {
            console.error('Preview failed:', error);
            setMessage({ type: 'error', text: 'Failed to generate preview' });
        } finally {
            setLoading(false);
        }
    };

    const submitReport = async () => {
        setLoading(true);
        setMessage(null);
        try {
            if (isEditMode && editingId) {
                await axios.put(`/api/entries/${editingId}`, entries[0]);
                setMessage({ type: 'success', text: "Entry updated successfully!" });
                setIsEditMode(false);
                setEditingId(null);
            } else {
                const reportDate = entries[0].date;
                await axios.post('/api/submit', {
                    date: reportDate,
                    entries: entries
                });
                setMessage({ type: 'success', text: `Data saved successfully for ${reportDate}!` });
            }
            fetchHistory();
            fetchMetadata();
            fetchReports();
            fetchEntriesForDate(entries[0].date);
        } catch (err: any) {
            setMessage({ type: 'error', text: err.response?.data?.detail || "Failed to submit report" });
        } finally {
            setLoading(false);
        }
    };

    const sendEmail = async () => {
        const reportDate = entries[0].date;
        setLoading(true);
        try {
            await axios.post(`/api/reports/send/${reportDate}`);
            setMessage({ type: 'success', text: `Report sent to dmronoh.12@gmail.com!` });
        } catch (err: any) {
            setMessage({ type: 'error', text: err.response?.data?.detail || "Failed to send email" });
        } finally {
            setLoading(false);
        }
    };

    // Analysis helpers
    const zoneContribution = React.useMemo(() => {
        const totals: Record<string, number> = {};
        history.forEach(e => {
            const z = e.zone || 'Unknown';
            totals[z] = (totals[z] || 0) + e.fact_wgt;
        });
        return Object.entries(totals).map(([name, value]) => ({ name, value }));
    }, [history]);

    const routeComparator = React.useMemo(() => {
        const routes: Record<string, { route: string, field: number, factory: number }> = {};
        history.forEach(e => {
            if (!routes[e.route]) routes[e.route] = { route: e.route, field: 0, factory: 0 };
            routes[e.route].field += e.fld_wgt;
            routes[e.route].factory += e.fact_wgt;
        });
        return Object.values(routes).slice(-10);
    }, [history]);

    const qualityTrend = React.useMemo(() => {
        const daily: Record<string, { sum: number, count: number }> = {};
        history.forEach(e => {
            if (!daily[e.date]) daily[e.date] = { sum: 0, count: 0 };
            daily[e.date].sum += e.quality_pct;
            daily[e.date].count += 1;
        });
        return Object.entries(daily)
            .map(([date, data]) => ({ date, quality: data.sum / data.count }))
            .sort((a, b) => a.date.localeCompare(b.date))
            .slice(-15);
    }, [history]);

    const prodTrend = React.useMemo(() => {
        const grouped: Record<string, number> = {};
        history.forEach(e => {
            grouped[e.date] = (grouped[e.date] || 0) + e.fact_wgt;
        });
        return Object.entries(grouped)
            .map(([date, total]) => ({ date, total }))
            .sort((a, b) => a.date.localeCompare(b.date))
            .slice(-15);
    }, [history]);

    const radarData = React.useMemo(() => {
        const zones: Record<string, { weight: number, quality: number, count: number, variance: number }> = {};
        history.forEach(e => {
            const z = e.zone || 'Unknown';
            if (!zones[z]) zones[z] = { weight: 0, quality: 0, count: 0, variance: 0 };
            zones[z].weight += e.fact_wgt;
            zones[z].quality += e.quality_pct;
            zones[z].variance += Math.abs(e.fact_wgt - e.fld_wgt);
            zones[z].count += 1;
        });

        const maxWeight = Math.max(...Object.values(zones).map(z => z.weight)) || 1;
        const maxVariance = Math.max(...Object.values(zones).map(z => z.variance)) || 1;

        return Object.entries(zones).map(([name, data]) => ({
            name,
            weight: (data.weight / maxWeight) * 100,
            quality: data.quality / data.count,
            variance: (1 - (data.variance / maxVariance)) * 100 // Higher is better (less variance)
        }));
    }, [history]);

    // === NEW ADVANCED ANALYTICS DATA ===

    // 1. Time-Series Quality Trends (Quality % + Weight over time)
    const timeSeriesQuality = React.useMemo(() => {
        const daily: Record<string, { quality: number, weight: number, count: number }> = {};
        history.forEach(e => {
            if (!daily[e.date]) daily[e.date] = { quality: 0, weight: 0, count: 0 };
            daily[e.date].quality += e.quality_pct;
            daily[e.date].weight += e.fact_wgt;
            daily[e.date].count += 1;
        });
        return Object.entries(daily)
            .map(([date, data]) => ({
                date,
                avgQuality: data.quality / data.count,
                totalWeight: data.weight
            }))
            .sort((a, b) => a.date.localeCompare(b.date))
            .slice(-30); // Last 30 days
    }, [history]);

    // 2. Clerk Performance Comparison
    const clerkPerformance = React.useMemo(() => {
        const clerks: Record<string, { weight: number, quality: number, count: number }> = {};
        history.forEach(e => {
            const clerk = e.clerk || 'Unknown';
            if (!clerks[clerk]) clerks[clerk] = { weight: 0, quality: 0, count: 0 };
            clerks[clerk].weight += e.fact_wgt;
            clerks[clerk].quality += e.quality_pct;
            clerks[clerk].count += 1;
        });
        return Object.entries(clerks)
            .map(([name, data]) => ({
                name,
                totalWeight: data.weight,
                avgQuality: data.quality / data.count,
                collections: data.count,
                efficiency: (data.weight / data.count) // Avg weight per collection
            }))
            .sort((a, b) => b.totalWeight - a.totalWeight)
            .slice(0, 10); // Top 10 clerks
    }, [history]);

    // 3. Vehicle Utilization
    const vehicleUtilization = React.useMemo(() => {
        const vehicles: Record<string, { weight: number, routes: Set<string>, count: number }> = {};
        history.forEach(e => {
            const vehicle = e.vehicle || 'Unknown';
            if (!vehicles[vehicle]) vehicles[vehicle] = { weight: 0, routes: new Set(), count: 0 };
            vehicles[vehicle].weight += e.fact_wgt;
            vehicles[vehicle].routes.add(e.route);
            vehicles[vehicle].count += 1;
        });
        return Object.entries(vehicles)
            .map(([name, data]) => ({
                name,
                totalWeight: data.weight,
                routesCovered: data.routes.size,
                trips: data.count,
                utilization: (data.count / 30) * 100 // % of days used (assuming 30 day period)
            }))
            .sort((a, b) => b.totalWeight - a.totalWeight)
            .slice(0, 8); // Top 8 vehicles
    }, [history]);

    // 4. Heatmap Calendar Data (Last 90 days)
    const heatmapData = React.useMemo(() => {
        const daily: Record<string, number> = {};
        history.forEach(e => {
            daily[e.date] = (daily[e.date] || 0) + e.fact_wgt;
        });

        const today = new Date();
        const data = [];
        for (let i = 89; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            data.push({
                date: dateStr,
                value: daily[dateStr] || 0,
                day: date.getDay(),
                week: Math.floor(i / 7)
            });
        }
        return data;
    }, [history]);

    // 5. Comparative Analysis (Zone performance over time)
    const comparativeAnalysis = React.useMemo(() => {
        const zoneDaily: Record<string, Record<string, number>> = {};
        history.forEach(e => {
            const zone = e.zone || 'Unknown';
            if (!zoneDaily[zone]) zoneDaily[zone] = {};
            zoneDaily[zone][e.date] = (zoneDaily[zone][e.date] || 0) + e.fact_wgt;
        });

        // Get all unique dates
        const allDates = [...new Set(history.map(e => e.date))].sort();

        return allDates.slice(-20).map(date => {
            const dataPoint: any = { date };
            Object.keys(zoneDaily).forEach(zone => {
                dataPoint[zone] = zoneDaily[zone][date] || 0;
            });
            return dataPoint;
        });
    }, [history]);

    // 6. Predictive Trends (7-day moving average)
    const predictiveTrends = React.useMemo(() => {
        const daily: Record<string, number> = {};
        history.forEach(e => {
            daily[e.date] = (daily[e.date] || 0) + e.fact_wgt;
        });

        const sorted = Object.entries(daily)
            .map(([date, weight]) => ({ date, weight }))
            .sort((a, b) => a.date.localeCompare(b.date));

        // Calculate 7-day moving average
        const withMA = sorted.map((item, idx) => {
            const window = sorted.slice(Math.max(0, idx - 6), idx + 1);
            const ma = window.reduce((sum, d) => sum + d.weight, 0) / window.length;
            return { ...item, movingAvg: ma };
        });

        // Add forecast (simple projection)
        const lastMA = withMA[withMA.length - 1]?.movingAvg || 0;
        const trend = withMA.length > 1 ?
            (withMA[withMA.length - 1].movingAvg - withMA[withMA.length - 7]?.movingAvg || 0) / 7 : 0;

        const forecast = [];
        for (let i = 1; i <= 7; i++) {
            const lastDate = new Date(withMA[withMA.length - 1]?.date || new Date());
            lastDate.setDate(lastDate.getDate() + i);
            forecast.push({
                date: lastDate.toISOString().split('T')[0],
                weight: null,
                movingAvg: null,
                forecast: lastMA + (trend * i)
            });
        }

        return [...withMA.slice(-30), ...forecast];
    }, [history]);

    // Filter state for interactivity
    const [analysisFilters, setAnalysisFilters] = React.useState({
        dateRange: 'all' as 'all' | '7d' | '30d' | '90d',
        selectedZones: [] as string[],
        selectedRoutes: [] as string[],
        selectedClerks: [] as string[]
    });

    return (
        <div className="min-h-screen p-4 md:p-8 bg-slate-950">
            <div className="max-w-7xl mx-auto">
                <header className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-primary-600 rounded-xl shadow-lg shadow-primary-600/20">
                            <FileSpreadsheet className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">Greenfield Report System</h1>
                            <p className="text-slate-400 text-sm">{isEditMode ? 'Editing Existing Record' : 'Advanced Data Entry & Tracking'}</p>
                        </div>
                    </div>

                    <nav className="flex bg-slate-900/50 p-1 rounded-lg border border-slate-800 overflow-x-auto">
                        {[
                            { id: 'entry', label: 'Entry', icon: Plus },
                            { id: 'history', label: 'History', icon: History },
                            { id: 'analysis', label: 'Analysis', icon: BarChart3 },
                            { id: 'reports', label: 'Reports', icon: Eye }
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all whitespace-nowrap ${activeTab === tab.id
                                    ? 'bg-primary-600 text-white shadow-lg'
                                    : 'text-slate-400 hover:text-slate-200'
                                    }`}
                            >
                                <tab.icon className="w-4 h-4" />
                                <span className="text-sm font-medium">{tab.label}</span>
                            </button>
                        ))}
                    </nav>
                </header>

                {message && (
                    <div className={`mb-6 p-4 rounded-xl flex items-center gap-3 border transition-all ${message.type === 'success'
                        ? 'bg-green-500/10 border-green-500/20 text-green-400'
                        : 'bg-red-500/10 border-red-500/20 text-red-400'
                        }`}>
                        {message.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                        <span className="text-sm font-medium">{message.text}</span>
                    </div>
                )}

                {activeTab === 'entry' && (
                    <div className="space-y-6">
                        <div className="glass rounded-2xl p-6 overflow-x-auto">
                            <div className="flex items-center gap-4 mb-8">
                                <div className="flex-1 max-w-xs">
                                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Report Date</label>
                                    <div className="relative">
                                        <CalendarIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                        <input
                                            type="date"
                                            value={entries[0].date}
                                            onChange={(e) => updateEntry(0, 'date', e.target.value)}
                                            className="w-full bg-slate-900 border border-slate-800 rounded-lg py-2 pl-10 pr-4 text-white focus:ring-2 focus:ring-primary-500 outline-none"
                                        />
                                    </div>
                                </div>
                                <div className="flex gap-2 self-end">
                                    <button
                                        onClick={() => window.open(`http://localhost:8000/api/reports/html/${entries[0].date}`, '_blank')}
                                        className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-sm transition-all"
                                    >
                                        <Eye className="w-4 h-4" /> Preview HTML
                                    </button>
                                    <button
                                        onClick={() => window.open(`http://localhost:8000/api/reports/Report_${entries[0].date.replace(/-/g, '')}.pdf`, '_blank')}
                                        className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-sm transition-all"
                                    >
                                        <FileSpreadsheet className="w-4 h-4" /> Preview PDF
                                    </button>
                                    <button
                                        onClick={sendEmail}
                                        className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-lg shadow-primary-900/20 transition-all ml-2"
                                    >
                                        <Send className="w-4 h-4" /> Send Email
                                    </button>
                                </div>
                            </div>

                            <table className="w-full text-left border-collapse min-w-[1000px]">
                                <thead>
                                    <tr className="border-b border-slate-800">
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Zone</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Clerk</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Vehicle</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Route</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Out / In</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest w-20">Tare Time</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest w-20">Fld/Fact</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest w-16">Scrch</th>
                                        <th className="py-4 px-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest w-16">Qty%</th>
                                        <th className="py-4 px-2"></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/50">
                                    {entries.map((entry, idx) => (
                                        <tr key={idx} className="group hover:bg-white/[0.02]">
                                            <td className="py-3 px-2">
                                                <select
                                                    value={entry.zone}
                                                    onChange={(e) => updateEntry(idx, 'zone', e.target.value)}
                                                    className="w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-2 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none"
                                                >
                                                    <option value="">Select Zone</option>
                                                    {metadata.zones.map(z => <option key={z} value={z}>{z}</option>)}
                                                    {metadata.zones.length === 0 && ZONES.map(z => <option key={z} value={z}>{z}</option>)}
                                                    {entry.zone && entry.zone !== 'NEW_ZONE' && !metadata.zones.includes(entry.zone) && !ZONES.includes(entry.zone) && <option value={entry.zone}>{entry.zone}</option>}
                                                    <option value="NEW_ZONE">+ Add New Zone</option>
                                                </select>
                                                {entry.zone === 'NEW_ZONE' && (
                                                    <input
                                                        autoFocus
                                                        type="text"
                                                        placeholder="PRESS ENTER TO SAVE"
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter') {
                                                                updateEntry(idx, 'zone', (e.target as HTMLInputElement).value.toUpperCase());
                                                            }
                                                        }}
                                                        onBlur={(e) => updateEntry(idx, 'zone', e.target.value.toUpperCase())}
                                                        className="mt-2 w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-2 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none uppercase"
                                                    />
                                                )}
                                            </td>
                                            <td className="py-3 px-2">
                                                <input
                                                    type="text"
                                                    value={entry.clerk}
                                                    placeholder="NAME"
                                                    onChange={(e) => updateEntry(idx, 'clerk', e.target.value.toUpperCase())}
                                                    className="w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-2 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none uppercase"
                                                />
                                            </td>
                                            <td className="py-3 px-2">
                                                <input
                                                    list={`vehicles-${idx}`}
                                                    type="text"
                                                    value={entry.vehicle}
                                                    placeholder="e.g. KXX 000"
                                                    onChange={(e) => updateEntry(idx, 'vehicle', e.target.value.toUpperCase())}
                                                    className="w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-2 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none uppercase"
                                                />
                                                <datalist id={`vehicles-${idx}`}>
                                                    {metadata.vehicles.map(v => <option key={v} value={v} />)}
                                                </datalist>
                                            </td>
                                            <td className="py-3 px-2">
                                                <select
                                                    value={entry.route}
                                                    onChange={(e) => updateEntry(idx, 'route', e.target.value)}
                                                    className="w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-2 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none"
                                                >
                                                    <option value="">Select Route</option>
                                                    {metadata.routes.map(r => <option key={r} value={r}>{r}</option>)}
                                                    {entry.route && entry.route !== 'NEW_ROUTE' && !metadata.routes.includes(entry.route) && <option value={entry.route}>{entry.route}</option>}
                                                    <option value="NEW_ROUTE">+ Add New Route</option>
                                                </select>
                                                {entry.route === 'NEW_ROUTE' && (
                                                    <input
                                                        autoFocus
                                                        type="text"
                                                        placeholder="PRESS ENTER TO SAVE"
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter') {
                                                                updateEntry(idx, 'route', (e.target as HTMLInputElement).value.toUpperCase());
                                                            }
                                                        }}
                                                        onBlur={(e) => updateEntry(idx, 'route', e.target.value.toUpperCase())}
                                                        className="mt-2 w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-2 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none uppercase"
                                                    />
                                                )}
                                            </td>
                                            <td className="py-3 px-2">
                                                <div className="flex gap-1">
                                                    <input
                                                        type="time"
                                                        title="Time Out"
                                                        value={entry.time_out}
                                                        onChange={(e) => updateEntry(idx, 'time_out', e.target.value)}
                                                        className="w-[70px] bg-slate-900 border border-slate-800 rounded-md py-1.5 px-1 text-[10px] text-white focus:ring-1 focus:ring-primary-500 outline-none"
                                                    />
                                                    <input
                                                        type="time"
                                                        title="Time In"
                                                        value={entry.time_in}
                                                        onChange={(e) => updateEntry(idx, 'time_in', e.target.value)}
                                                        className="w-[70px] bg-slate-900 border border-slate-800 rounded-md py-1.5 px-1 text-[10px] text-white focus:ring-1 focus:ring-primary-500 outline-none"
                                                    />
                                                </div>
                                            </td>
                                            <td className="py-3 px-2">
                                                <input
                                                    type="time"
                                                    value={entry.tare_time}
                                                    onChange={(e) => updateEntry(idx, 'tare_time', e.target.value)}
                                                    className="w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-1 text-[10px] text-white focus:ring-1 focus:ring-primary-500 outline-none"
                                                />
                                            </td>
                                            <td className="py-3 px-2">
                                                <div className="space-y-1">
                                                    <input
                                                        type="number"
                                                        placeholder="Field"
                                                        value={entry.fld_wgt || ''}
                                                        onChange={(e) => updateEntry(idx, 'fld_wgt', parseFloat(e.target.value))}
                                                        className="w-full bg-slate-900 border border-slate-800 rounded-md py-1 px-2 text-[10px] text-white focus:ring-1 focus:ring-primary-500 outline-none text-right"
                                                    />
                                                    <input
                                                        type="number"
                                                        placeholder="Fact"
                                                        value={entry.fact_wgt || ''}
                                                        onChange={(e) => updateEntry(idx, 'fact_wgt', parseFloat(e.target.value))}
                                                        className="w-full bg-slate-900 border border-slate-800 rounded-md py-1 px-2 text-[10px] text-white focus:ring-1 focus:ring-primary-500 outline-none text-right"
                                                    />
                                                </div>
                                            </td>
                                            <td className="py-3 px-2">
                                                <input
                                                    type="number"
                                                    value={entry.scorch_kg || ''}
                                                    onChange={(e) => updateEntry(idx, 'scorch_kg', parseFloat(e.target.value))}
                                                    className="w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-1 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none text-right"
                                                />
                                            </td>
                                            <td className="py-3 px-2">
                                                <input
                                                    type="number"
                                                    value={entry.quality_pct || ''}
                                                    onChange={(e) => updateEntry(idx, 'quality_pct', parseFloat(e.target.value))}
                                                    className="w-full bg-slate-900 border border-slate-800 rounded-md py-1.5 px-1 text-xs text-white focus:ring-1 focus:ring-primary-500 outline-none text-right"
                                                />
                                            </td>
                                            <td className="py-3 px-2">
                                                <button
                                                    onClick={() => removeRow(idx)}
                                                    className="p-1.5 text-slate-600 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>

                            <div className="mt-8 flex justify-between items-center p-4 bg-white/[0.02] border border-white/5 rounded-xl">
                                <div className="flex gap-4">
                                    <button
                                        onClick={addRow}
                                        className="flex items-center gap-2 text-primary-400 hover:text-primary-300 transition-colors font-medium text-sm px-4 py-2 rounded-lg hover:bg-primary-400/5"
                                    >
                                        <Plus className="w-4 h-4" /> Add New Line
                                    </button>
                                    <button
                                        onClick={() => previewReport('pdf')}
                                        disabled={loading}
                                        className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-all text-sm"
                                    >
                                        <FileText className="w-4 h-4" /> Preview PDF
                                    </button>
                                    <button
                                        onClick={() => previewReport('html')}
                                        disabled={loading}
                                        className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-all text-sm"
                                    >
                                        <Layout className="w-4 h-4" /> Preview HTML
                                    </button>
                                    <button
                                        onClick={sendEmail}
                                        disabled={loading}
                                        className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 disabled:bg-primary-900 disabled:opacity-50 text-white font-bold py-2 px-6 rounded-lg transition-all shadow-lg shadow-primary-900/20 text-sm"
                                    >
                                        {loading ? (
                                            <Clock className="w-4 h-4 animate-spin" />
                                        ) : (
                                            <Send className="w-4 h-4" />
                                        )}
                                        Send Email
                                    </button>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Total Weight Today</p>
                                <p className="text-xl font-bold text-white mono">{entries.reduce((sum, e) => sum + (e.fact_wgt || 0), 0).toLocaleString()} <span className="text-xs text-slate-500">KG</span></p>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'history' && (
                    <div className="glass rounded-2xl p-6">
                        <h2 className="text-xl font-bold text-white mb-6">Collection History</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="border-b border-slate-800">
                                        <th className="py-4 px-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Date</th>
                                        <th className="py-4 px-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Route</th>
                                        <th className="py-4 px-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">Times</th>
                                        <th className="py-4 px-4 text-xs font-semibold text-slate-500 uppercase tracking-widest text-right">Factory (kg)</th>
                                        <th className="py-4 px-4 text-xs font-semibold text-slate-500 uppercase tracking-widest text-right">Varience</th>
                                        <th className="py-4 px-4"></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/50">
                                    {history.map((h, i) => (
                                        <tr key={h.id || i} className="hover:bg-white/[0.02]">
                                            <td className="py-4 px-4">
                                                <div className="text-sm text-white font-medium">{h.date}</div>
                                                <div className="text-[10px] text-slate-500 uppercase">{h.zone}</div>
                                            </td>
                                            <td className="py-4 px-4 text-sm text-slate-300">{h.route}</td>
                                            <td className="py-4 px-4 text-[10px] text-slate-400">
                                                {h.time_out && `Out: ${h.time_out}`}
                                                {h.time_in && ` / In: ${h.time_in}`}
                                                {h.tare_time && <div className="text-primary-500">Tare: {h.tare_time}</div>}
                                            </td>
                                            <td className="py-4 px-4 text-sm text-white text-right">{h.fact_wgt.toLocaleString()}</td>
                                            <td className={`py-4 px-4 text-sm text-right ${h.fact_wgt - h.fld_wgt >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                {(h.fact_wgt - h.fld_wgt).toFixed(1)}
                                            </td>
                                            <td className="py-4 px-4 text-right">
                                                {canEdit((h as any).created_at) && (
                                                    <button
                                                        onClick={() => handleEdit(h)}
                                                        className="p-2 text-primary-500 hover:bg-primary-500/10 rounded-lg transition-all"
                                                        title="Edit (within 48h)"
                                                    >
                                                        <Edit2 className="w-4 h-4" />
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {activeTab === 'reports' && (
                    <div className="space-y-6">
                        <h2 className="text-xl font-bold text-white">Generated Reports Gallery</h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {reportFiles.map((file) => (
                                <div key={file} className="glass group rounded-xl p-4 border border-slate-800 hover:border-primary-500/50 transition-all">
                                    <div className="aspect-[3/4] bg-slate-900 rounded-lg mb-4 flex items-center justify-center relative overflow-hidden">
                                        <FileSpreadsheet className="w-12 h-12 text-slate-700 group-hover:text-primary-600 transition-colors" />
                                        <div className="absolute inset-0 bg-primary-600/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                    <h4 className="text-sm font-medium text-slate-300 truncate mb-1">{file}</h4>
                                    <p className="text-[10px] text-slate-500 mb-3">{file.includes('_') ? file.split('_')[1].split('.')[0] : 'Report'}</p>
                                    <a
                                        href={`/api/reports/${file}`}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="flex items-center justify-center gap-2 w-full py-2 bg-slate-800 hover:bg-primary-600 text-white rounded-lg text-xs font-semibold transition-all"
                                    >
                                        <ExternalLink className="w-3 h-3" />
                                        Open PDF
                                    </a>
                                </div>
                            ))}
                            {reportFiles.length === 0 && (
                                <div className="col-span-full py-20 text-center text-slate-500 italic">No reports generated yet.</div>
                            )}
                        
                        {/* Advanced Analytics Section */}
                        <AdvancedAnalytics
                            timeSeriesQuality={timeSeriesQuality}
                            clerkPerformance={clerkPerformance}
                            vehicleUtilization={vehicleUtilization}
                            heatmapData={heatmapData}
                            comparativeAnalysis={comparativeAnalysis}
                            predictiveTrends={predictiveTrends}
                        />
</div>
                    </div>
                )}

                {activeTab === 'analysis' && (
                    <div className="space-y-8 animate-in fade-in duration-700">
                        {/* Summary Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {[
                                { label: 'Total Volume', value: `${zoneContribution.reduce((a, b) => a + b.value, 0).toLocaleString()} KG`, icon: FileSpreadsheet, color: 'from-green-600/20 to-emerald-600/20', text: 'text-green-400' },
                                { label: 'Avg Quality', value: `${(qualityTrend.reduce((a, b) => a + b.quality, 0) / (qualityTrend.length || 1)).toFixed(1)}%`, icon: CheckCircle2, color: 'from-blue-600/20 to-indigo-600/20', text: 'text-blue-400' },
                                { label: 'Active Zones', value: zoneContribution.length, icon: PieChartIcon, color: 'from-purple-600/20 to-pink-600/20', text: 'text-purple-400' },
                                { label: 'Total Collections', value: history.length, icon: Plus, color: 'from-orange-600/20 to-yellow-600/20', text: 'text-orange-400' }
                            ].map((stat, i) => (
                                <div key={i} className={`glass relative overflow-hidden rounded-2xl p-6 border border-white/5`}>
                                    <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${stat.color} blur-2xl -mr-8 -mt-8 opacity-50`} />
                                    <stat.icon className={`w-8 h-8 ${stat.text} mb-4`} />
                                    <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">{stat.label}</p>
                                    <h4 className="text-3xl font-bold text-white tracking-tight">{stat.value}</h4>
                                </div>
                            ))}
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Main Trend Chart */}
                            <div className="glass lg:col-span-2 rounded-3xl p-8 border border-white/5">
                                <div className="flex justify-between items-center mb-8">
                                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Growth Analytics</h3>
                                    <div className="flex gap-2">
                                        <span className="flex items-center gap-1.5 text-[10px] text-green-400 font-bold uppercase"><div className="w-2 h-2 rounded-full bg-green-400" /> Production</span>
                                    </div>
                                </div>
                                <div className="h-[300px]">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={prodTrend}>
                                            <defs>
                                                <linearGradient id="colorProd" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                                            <XAxis dataKey="date" stroke="#475569" fontSize={10} axisLine={false} tickLine={false} />
                                            <YAxis stroke="#475569" fontSize={10} axisLine={false} tickLine={false} />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '12px' }}
                                                itemStyle={{ color: '#fff' }}
                                            />
                                            <Area type="monotone" dataKey="total" stroke="#22c55e" strokeWidth={3} fillOpacity={1} fill="url(#colorProd)" />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Zone Comparison (Radar) */}
                            <div className="glass rounded-3xl p-8 border border-white/5">
                                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8 text-center">Zone Performance Radar</h3>
                                <div className="h-[300px]">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <RadarChart outerRadius="80%" data={radarData}>
                                            <PolarGrid stroke="#ffffff10" />
                                            <PolarAngleAxis dataKey="name" stroke="#64748b" fontSize={10} />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                                            />
                                            <Radar name="Score" dataKey="weight" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.5} />
                                            <Radar name="Quality" dataKey="quality" stroke="#a855f7" fill="#a855f7" fillOpacity={0.3} />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Route Efficiency */}
                            <div className="glass lg:col-span-2 rounded-3xl p-8 border border-white/5">
                                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Route Weight Distribution</h3>
                                <div className="h-[300px]">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={routeComparator} barSize={12}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                                            <XAxis dataKey="route" stroke="#475569" fontSize={10} axisLine={false} />
                                            <YAxis stroke="#475569" fontSize={10} axisLine={false} />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                                            />
                                            <Bar dataKey="factory" radius={[6, 6, 0, 0]}>
                                                {routeComparator.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} opacity={0.8} />
                                                ))}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Distribution Pie */}
                            <div className="glass rounded-3xl p-8 border border-white/5">
                                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8 text-center">Market Share (Volume)</h3>
                                <div className="h-[300px]">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={zoneContribution}
                                                innerRadius={70}
                                                outerRadius={100}
                                                paddingAngle={8}
                                                dataKey="value"
                                                stroke="none"
                                            >
                                                {zoneContribution.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                                            </Pie>
                                            <Tooltip />
                                            <Legend verticalAlign="bottom" height={36} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div >
    );
}

export default App;
