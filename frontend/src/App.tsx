import { useState, useEffect } from 'react';

function GenerationTab() {
  const [prompt, setPrompt] = useState("A stunning photorealistic portrait of an AI influencer, cinematic lighting, 8k resolution, highly detailed");
  const [status, setStatus] = useState("idle");
  const [images, setImages] = useState<string[]>([]);
  
  const handleGenerate = async () => {
    setStatus("generating...");
    setImages([]);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/generation/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, steps: 20 })
      });
      const data = await res.json();
      
      if (data.prompt_id) {
         setStatus("queued");
         pollStatus(data.prompt_id, apiUrl);
      } else {
         setStatus("error: no prompt_id returned");
      }
    } catch (e: any) {
      setStatus("error: " + e.message);
    }
  };

  const pollStatus = async (prompt_id: string, apiUrl: string) => {
    const interval = setInterval(async () => {
       try {
         const res = await fetch(`${apiUrl}/generation/status/${prompt_id}`);
         const data = await res.json();
         
         if (data.status === "complete") {
            clearInterval(interval);
            setStatus("complete!");
            // ComfyUI serves images on port 8188. We proxy this by modifying the URL.
            const comfyUrl = apiUrl.replace("8000", "8188");
            const imgUrls = data.images.map((img: string) => {
                const filename = img.split('/').pop();
                return `${comfyUrl}/view?filename=${filename}&type=output`;
            });
            setImages(imgUrls);
         } else if (data.status === "error") {
            clearInterval(interval);
            setStatus("failed: " + data.message);
         } else {
            setStatus("generating... (this takes about 30 seconds)");
         }
       } catch(e) {
           console.error("Polling error", e);
       }
    }, 3000);
  };

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out h-full flex flex-col">
      <div className="bg-[#111827]/80 backdrop-blur-sm border border-gray-800 rounded-2xl p-6 shadow-lg">
         <h3 className="text-xl font-bold text-white mb-4">✨ Generate Image (FLUX.1-dev)</h3>
         <textarea 
            className="w-full bg-[#0B0F19] border border-gray-700 rounded-xl p-4 text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all resize-none"
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
         />
         <div className="mt-4 flex justify-between items-center">
            <span className="text-sm text-gray-400">Status: <span className="text-blue-400 font-medium ml-1">{status}</span></span>
            <button 
               onClick={handleGenerate} 
               disabled={status.includes("generating")} 
               className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-medium rounded-xl transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.5)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
               {status.includes("generating") ? "Processing..." : "Generate Image"}
            </button>
         </div>
      </div>
      <div className="mt-6 flex-1 bg-[#111827]/30 border border-gray-800/50 rounded-2xl p-6 overflow-y-auto custom-scrollbar">
         {images.length > 0 ? (
           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             {images.map((img, i) => (
                <img key={i} src={img} className="w-full h-auto rounded-xl shadow-2xl border border-gray-700/50" alt="Generated Output" />
             ))}
           </div>
         ) : (
           <div className="h-full flex flex-col items-center justify-center text-gray-600 font-medium">
              <span className="text-5xl mb-4">🖼️</span>
              Generated images will appear here
           </div>
         )}
      </div>
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'datasets', label: 'Datasets', icon: '📁' },
    { id: 'training', label: 'Training', icon: '🧠' },
    { id: 'generation', label: 'Generation', icon: '✨' },
    { id: 'video', label: 'Video API', icon: '🎬' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="min-h-screen bg-[#0B0F19] text-gray-200 font-sans flex overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-[#111827] border-r border-gray-800 flex flex-col justify-between transition-all duration-300">
        <div>
          <div className="p-6">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(59,130,246,0.3)]">
              AI Influencer
            </h1>
            <p className="text-xs text-gray-500 mt-1 uppercase tracking-widest font-semibold">Studio</p>
          </div>
          
          <nav className="mt-6 px-4 space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group
                  ${activeTab === item.id 
                    ? 'bg-gradient-to-r from-blue-600/20 to-blue-500/10 text-blue-400 border border-blue-500/30 shadow-[inset_0px_0px_20px_rgba(59,130,246,0.15)]' 
                    : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                  }`}
              >
                <span className={`text-lg transition-transform duration-300 ${activeTab === item.id ? 'scale-110 drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]' : 'group-hover:scale-110'}`}>{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
        
        <div className="p-4">
          <div className="bg-[#1F2937] rounded-xl p-4 border border-gray-700/50 relative overflow-hidden group hover:border-blue-500/30 transition-colors">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="flex items-center gap-3 relative z-10">
              <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)] animate-pulse"></div>
              <span className="text-sm font-medium text-gray-300">RunPod Connected</span>
            </div>
            <div className="mt-2 flex justify-between text-xs text-gray-500 relative z-10">
              <span>RTX 4090</span>
              <span className="text-blue-400 font-semibold">24GB</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-900/10 via-[#0B0F19] to-[#0B0F19]">
        {/* Topbar */}
        <header className="h-16 border-b border-gray-800/60 backdrop-blur-md bg-[#0B0F19]/80 flex items-center justify-between px-8">
          <h2 className="text-xl font-semibold capitalize text-gray-100 drop-shadow-md">{activeTab}</h2>
          <div className="flex items-center gap-4">
            <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full animate-ping"></span>
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full"></span>
              🔔
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-sm shadow-[0_0_15px_rgba(59,130,246,0.4)] border border-white/10">
              AD
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          {activeTab === 'dashboard' && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { label: 'Models Trained', value: '4', trend: '+1 this week', color: 'blue' },
                  { label: 'Images Generated', value: '1,284', trend: '+142 today', color: 'purple' },
                  { label: 'GPU Utilization', value: '87%', trend: 'Stable', color: 'emerald' },
                ].map((stat, i) => (
                  <div key={i} className="bg-[#111827]/80 backdrop-blur-sm border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-colors shadow-lg hover:shadow-xl hover:-translate-y-1 duration-300 group">
                    <h3 className="text-gray-400 text-sm font-medium">{stat.label}</h3>
                    <div className="mt-4 flex items-baseline gap-3">
                      <span className="text-4xl font-bold text-white group-hover:scale-105 transition-transform origin-left">{stat.value}</span>
                      <span className={`text-xs text-${stat.color}-400 font-medium bg-${stat.color}-400/10 px-2 py-1 rounded-full`}>{stat.trend}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Placeholder for complex dashboard elements */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                 <div className="h-96 rounded-2xl border border-gray-800 bg-[#111827]/50 flex items-center justify-center backdrop-blur-sm shadow-inner relative overflow-hidden group">
                   <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                   <div className="text-center z-10">
                      <span className="text-4xl mb-4 block">📈</span>
                      <p className="text-gray-500 font-medium">Training Progress Chart</p>
                      <p className="text-xs text-gray-600 mt-2">Awaiting data...</p>
                   </div>
                 </div>
                 <div className="h-96 rounded-2xl border border-gray-800 bg-[#111827]/50 flex items-center justify-center backdrop-blur-sm shadow-inner relative overflow-hidden group">
                   <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                   <div className="text-center z-10">
                      <span className="text-4xl mb-4 block">🖼️</span>
                      <p className="text-gray-500 font-medium">Recent Generations</p>
                      <button className="mt-4 px-4 py-2 bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-lg text-sm font-medium hover:bg-blue-600/30 transition-colors shadow-[0_0_15px_rgba(59,130,246,0.15)]">View Gallery</button>
                   </div>
                 </div>
              </div>
            </div>
          )}

          {activeTab === 'generation' && (
            <GenerationTab />
          )}

          {activeTab !== 'dashboard' && activeTab !== 'generation' && (
            <div className="h-full flex flex-col items-center justify-center text-center animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out">
              <span className="text-6xl mb-6 opacity-80">{navItems.find(i => i.id === activeTab)?.icon}</span>
              <h3 className="text-2xl font-semibold text-gray-200 mb-2">{navItems.find(i => i.id === activeTab)?.label} Module</h3>
              <p className="text-gray-500 max-w-md">This module is currently under construction. Please check the implementation plan for Phase details.</p>
              
              <div className="mt-12 p-[1px] bg-gradient-to-r from-transparent via-gray-700 to-transparent w-64"></div>
            </div>
          )}
        </div>
      </main>

      {/* Global Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(17, 24, 39, 0.5);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(55, 65, 81, 0.8);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(75, 85, 99, 1);
        }
      `}</style>
    </div>
  );
}

export default App;
