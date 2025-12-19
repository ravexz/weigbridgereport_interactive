import React from 'react';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Cell
} from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#a855f7', '#f59e0b', '#ec4899'];

interface AdvancedAnalyticsProps {
    timeSeriesQuality: Array<{ date: string; avgQuality: number; totalWeight: number }>;
    clerkPerformance: Array<{ name: string; totalWeight: number; avgQuality: number; collections: number; efficiency: number }>;
    vehicleUtilization: Array<{ name: string; totalWeight: number; routesCovered: number; trips: number; utilization: number }>;
    heatmapData: Array<{ date: string; value: number; day: number; week: number }>;
    comparativeAnalysis: Array<any>;
    predictiveTrends: Array<{ date: string; weight: number | null; movingAvg: number | null; forecast?: number }>;
}

const AdvancedAnalytics: React.FC<AdvancedAnalyticsProps> = ({
    timeSeriesQuality,
    clerkPerformance,
    vehicleUtilization,
    heatmapData,
    comparativeAnalysis,
    predictiveTrends
}) => {
    return (
        <div className="space-y-8 mt-12">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Advanced Analytics</h2>
                <div className="flex gap-2">
                    <button className="px-3 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all">7D</button>
                    <button className="px-3 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all">30D</button>
                    <button className="px-3 py-1 text-xs bg-primary-600 text-white rounded-lg">90D</button>
                </div>
            </div>

            {/* 1. Time-Series Quality Trends */}
            <div className="glass rounded-3xl p-8 border border-white/5">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Quality & Weight Trends</h3>
                <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={timeSeriesQuality}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" />
                            <XAxis dataKey="date" stroke="#475569" fontSize={10} />
                            <YAxis yAxisId="left" stroke="#3b82f6" fontSize={10} />
                            <YAxis yAxisId="right" orientation="right" stroke="#22c55e" fontSize={10} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                            <Legend />
                            <Line yAxisId="left" type="monotone" dataKey="avgQuality" stroke="#3b82f6" strokeWidth={2} name="Avg Quality %" />
                            <Line yAxisId="right" type="monotone" dataKey="totalWeight" stroke="#22c55e" strokeWidth={2} name="Total Weight (KG)" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* 2. Clerk Performance */}
                <div className="glass rounded-3xl p-8 border border-white/5">
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Clerk Performance (Top 10)</h3>
                    <div className="h-[400px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={clerkPerformance} layout="vertical" barSize={20}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" />
                                <XAxis type="number" stroke="#475569" fontSize={10} />
                                <YAxis dataKey="name" type="category" stroke="#475569" fontSize={10} width={100} />
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                                <Bar dataKey="totalWeight" fill="#22c55e" radius={[0, 6, 6, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* 3. Vehicle Utilization */}
                <div className="glass rounded-3xl p-8 border border-white/5">
                    <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Vehicle Utilization</h3>
                    <div className="h-[400px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={vehicleUtilization}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" />
                                <XAxis dataKey="name" stroke="#475569" fontSize={10} angle={-45} textAnchor="end" height={80} />
                                <YAxis stroke="#475569" fontSize={10} />
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                                <Bar dataKey="totalWeight" stackId="a" fill="#3b82f6" />
                                <Bar dataKey="trips" stackId="b" fill="#a855f7" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* 4. Heatmap Calendar */}
            <div className="glass rounded-3xl p-8 border border-white/5">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Collection Heatmap (Last 90 Days)</h3>
                <div className="overflow-x-auto">
                    <div className="inline-flex flex-col gap-1">
                        {[0, 1, 2, 3, 4, 5, 6].map(day => (
                            <div key={day} className="flex gap-1">
                                {heatmapData.filter(d => d.day === day).map((d, i) => {
                                    const maxValue = Math.max(...heatmapData.map(x => x.value));
                                    const intensity = d.value / (maxValue || 1);
                                    const color = intensity > 0.75 ? '#22c55e' : intensity > 0.5 ? '#3b82f6' : intensity > 0.25 ? '#a855f7' : '#334155';
                                    return (
                                        <div
                                            key={i}
                                            className="w-3 h-3 rounded-sm transition-all hover:scale-150 cursor-pointer"
                                            style={{ backgroundColor: color }}
                                            title={`${d.date}: ${d.value.toFixed(0)} KG`}
                                        />
                                    );
                                })}</div>
                        ))}</div>
                    <div className="flex gap-2 mt-4 text-xs text-slate-500">
                        <span>Less</span>
                        <div className="flex gap-1">
                            {['#334155', '#a855f7', '#3b82f6', '#22c55e'].map((c, i) => (
                                <div key={i} className="w-3 h-3 rounded-sm" style={{ backgroundColor: c }} />
                            ))}
                        </div>
                        <span>More</span>
                    </div>
                </div>
            </div>

            {/* 5. Comparative Analysis */}
            <div className="glass rounded-3xl p-8 border border-white/5">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Zone Comparison Over Time</h3>
                <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={comparativeAnalysis}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" />
                            <XAxis dataKey="date" stroke="#475569" fontSize={10} />
                            <YAxis stroke="#475569" fontSize={10} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                            <Legend />
                            {Object.keys(comparativeAnalysis[0] || {}).filter(k => k !== 'date').map((zone, i) => (
                                <Line key={zone} type="monotone" dataKey={zone} stroke={COLORS[i % COLORS.length]} strokeWidth={2} />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* 6. Predictive Trends */}
            <div className="glass rounded-3xl p-8 border border-white/5">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Predictive Trends (7-Day Forecast)</h3>
                <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={predictiveTrends}>
                            <defs>
                                <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.2} />
                                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" />
                            <XAxis dataKey="date" stroke="#475569" fontSize={10} />
                            <YAxis stroke="#475569" fontSize={10} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
                            <Legend />
                            <Area type="monotone" dataKey="weight" stroke="#22c55e" fill="url(#colorActual)" name="Actual" />
                            <Area type="monotone" dataKey="movingAvg" stroke="#3b82f6" fill="none" strokeWidth={2} name="7-Day MA" />
                            <Area type="monotone" dataKey="forecast" stroke="#f59e0b" fill="url(#colorForecast)" strokeDasharray="5 5" name="Forecast" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default AdvancedAnalytics;
