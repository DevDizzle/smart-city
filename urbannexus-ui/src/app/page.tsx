'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Brain, Map as MapIcon, Shield, Zap, Wifi } from 'lucide-react';
import { Zone, Goal, Constraint } from '@/types'; // We'll define these types next

// Dynamic import for Map to avoid SSR issues with Leaflet
const MapComponent = dynamic(() => import('@/components/Map'), { 
  ssr: false,
  loading: () => <div className="w-full h-full bg-slate-200 animate-pulse flex items-center justify-center text-slate-400">Loading Map...</div>
});

export default function Home() {
  const [zones, setZones] = useState<Zone[]>([]);
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null);
  const [goals, setGoals] = useState<Goal[]>([
    { type: 'Safety', description: 'Increase student safety at night', priority: 'High', enabled: true },
    { type: 'Energy', description: 'Reduce campus carbon footprint', priority: 'High', enabled: true },
    { type: 'Connectivity', description: 'Provide outdoor WiFi for students', priority: 'Medium', enabled: true }
  ]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [events, setEvents] = useState<any[]>([]);
  const [errorMsg, setErrorMsg] = useState<string>("");

  const BACKEND_URL = "https://urbannexus-backend-550651297425.us-central1.run.app";

  // Fetch zones on mount
  useEffect(() => {
    fetch(`${BACKEND_URL}/zones`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        if(data.zones) setZones(data.zones);
      })
      .catch(err => {
        console.error("Failed to fetch zones:", err);
        setErrorMsg(err.toString());
      });
  }, []);

  const runAnalysis = async () => {
    if (!selectedZone) return;
    
    setIsAnalyzing(true);
    setEvents([]);

    const payload = {
      zone_id: selectedZone.zone_id,
      goals: goals.filter(g => g.enabled),
      constraints: []
    };

    try {
      const response = await fetch(`${BACKEND_URL}/analyze/v2`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete line

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6);
            try {
              const event = JSON.parse(jsonStr);
              setEvents(prev => [...prev, event]);
            } catch (e) {
              console.error("Error parsing event:", e);
            }
          }
        }
      }
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="flex h-screen w-full bg-slate-50 overflow-hidden">
      {/* Sidebar: Controls & Info */}
      <div className="w-96 bg-white border-r border-slate-200 flex flex-col shadow-xl z-20">
        <div className="p-6 border-b border-slate-200 bg-slate-900 text-white">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-400" />
            UrbanNexus <span className="text-slate-400 font-light text-sm">Smart City</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">Infrastructure Optimization Engine</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          
          {/* Section: Zone Selection */}
          <section>
            <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">1. Select Zone</h2>
            {selectedZone ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-bold text-blue-900">{selectedZone.name}</h3>
                <p className="text-xs text-blue-700 mt-1">{selectedZone.description}</p>
                <button 
                  onClick={() => setSelectedZone(null)}
                  className="mt-2 text-xs text-blue-600 underline hover:text-blue-800"
                >
                  Change Zone
                </button>
              </div>
            ) : (
              <div className="text-sm text-slate-400 italic border-2 border-dashed border-slate-200 rounded-lg p-4 text-center">
                Select a zone on the map to begin.
              </div>
            )}
          </section>

          {/* Section: Goals */}
          <section>
            <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">2. Strategic Goals</h2>
            <div className="space-y-3">
              {goals.map((goal, idx) => (
                <div key={idx} className={`flex items-start gap-3 p-3 rounded-md border cursor-pointer transition-all ${goal.enabled ? 'bg-white border-slate-300 shadow-sm' : 'bg-slate-50 border-slate-100 opacity-60'}`}
                     onClick={() => {
                       const newGoals = [...goals];
                       newGoals[idx].enabled = !newGoals[idx].enabled;
                       setGoals(newGoals);
                     }}
                >
                  <div className={`mt-1 ${goal.enabled ? 'text-green-500' : 'text-slate-300'}`}>
                    {goal.type === 'Safety' && <Shield size={16} />}
                    {goal.type === 'Energy' && <Zap size={16} />}
                    {goal.type === 'Connectivity' && <Wifi size={16} />}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-900">{goal.type}</div>
                    <div className="text-xs text-slate-500">{goal.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Debug Status */}
          <section className="bg-slate-100 p-3 rounded text-xs font-mono text-slate-500">
            <div>System Status:</div>
            <div>Zones Loaded: {zones.length}</div>
            {errorMsg && (
              <div className="bg-red-100 border border-red-400 text-red-700 p-2 mt-2 rounded">
                <strong>Error:</strong> {errorMsg}
              </div>
            )}
            <div className="mt-1 text-[10px] break-all text-slate-400">
              Backend: {BACKEND_URL}
            </div>
          </section>

          {/* Action */}
          <button
            onClick={runAnalysis}
            disabled={!selectedZone || isAnalyzing}
            className={`w-full py-4 rounded-lg font-bold text-white shadow-lg transition-all transform active:scale-95 ${!selectedZone || isAnalyzing ? 'bg-slate-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-blue-500/25'}`}
          >
            {isAnalyzing ? 'Optimizing...' : 'Run Analysis'}
          </button>

        </div>
      </div>

      {/* Main Content: Map */}
      <div className="flex-1 relative bg-slate-100">
         <MapComponent zones={zones} selectedZone={selectedZone} onSelectZone={setSelectedZone} />
         
         {/* Overlay: Recommendations (Only when complete) */}
         {/* We can pass results to MapComponent to render markers */}
      </div>

      {/* Right Panel: Live Trace */}
      <div className="w-[450px] bg-white border-l border-slate-200 flex flex-col z-20 shadow-xl">
         <div className="p-4 border-b border-slate-200 bg-slate-50">
           <h2 className="font-semibold text-slate-700 flex items-center gap-2">
             <div className={`w-2 h-2 rounded-full ${isAnalyzing ? 'bg-amber-500 animate-pulse' : 'bg-slate-300'}`} />
             Live Agent Trace
           </h2>
         </div>
         <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 font-mono text-sm">
            {events.length === 0 && !isAnalyzing && (
              <div className="text-slate-400 text-center mt-10">
                Waiting for analysis...
              </div>
            )}
            
            {events.map((evt, i) => (
              <div key={i} className="bg-white rounded border border-slate-200 shadow-sm p-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-bold text-blue-600 uppercase">{evt.agent || 'System'}</span>
                  <span className="text-[10px] text-slate-400">{evt.step}</span>
                </div>
                
                {/* Render specific outputs based on step */}
                {evt.step === 'assessment' && (
                  <div className="text-xs text-slate-600">
                    Loaded data for <strong>{evt.outputs_ref?.name}</strong>.
                  </div>
                )}

                {evt.step === 'value_analysis' && (
                  <div className="space-y-2 mt-1">
                    {evt.outputs_ref?.proposals?.map((p: any, j: number) => (
                      <div key={j} className="text-xs bg-green-50 text-green-800 p-2 rounded border border-green-100">
                        <strong>+ Proposal:</strong> {p.hardware.sku} <br/>
                        <span className="italic opacity-75">{p.value_proposition}</span>
                      </div>
                    ))}
                  </div>
                )}

                {evt.step === 'risk_analysis' && (
                   <div className="space-y-1 mt-1">
                     {evt.outputs_ref?.risks?.length > 0 ? (
                        evt.outputs_ref.risks.map((r: any, k: number) => (
                          <div key={k} className="text-xs bg-red-50 text-red-800 p-2 rounded border border-red-100">
                            <strong>! Risk ({r.severity}):</strong> {r.description}
                          </div>
                        ))
                     ) : (
                       <div className="text-xs text-green-600 flex items-center gap-1">
                         <Shield size={12}/> No risks identified.
                       </div>
                     )}
                   </div>
                )}

                {evt.step === 'synthesis' && (
                  <div className={`mt-2 p-2 rounded text-center font-bold text-white ${evt.decision_state === 'GO' ? 'bg-green-600' : 'bg-amber-500'}`}>
                    DECISION: {evt.decision_state}
                  </div>
                )}

              </div>
            ))}
            <div className="h-4" /> {/* Spacer */}
         </div>
      </div>
    </main>
  );
}