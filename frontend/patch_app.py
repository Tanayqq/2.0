import os

file_path = r"C:\Users\Tanay Kumar\Desktop\2.0\frontend\src\App.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
if "import { Dashboard }" not in content:
    content = content.replace(
        'import { InlineCitation } from "./components/InlineCitation";',
        'import { InlineCitation } from "./components/InlineCitation";\nimport { Dashboard } from "./components/Dashboard";\nimport { ClinicalAudit } from "./components/ClinicalAudit";'
    )
    
    # Replace lucide imports
    content = content.replace(
        "} from \"lucide-react\";",
        ", Database, BarChart, Server, LayoutDashboard, MessageSquare, TestTube2, Workflow, Clock } from \"lucide-react\";"
    )

# 2. State
if "activeTab" not in content:
    content = content.replace(
        'const [activeHistoryIndex, setActiveHistoryIndex] = useState<number>(-1);',
        'const [activeHistoryIndex, setActiveHistoryIndex] = useState<number>(-1);\n  const [activeTab, setActiveTab] = useState<"chat" | "dashboard">("chat");'
    )

# 3. Sidebar Navigation
if "onClick={() => setActiveTab" not in content:
    sidebar_injection = """
        {/* Navigation Tabs */}
        <div className="flex flex-col gap-1 px-4 mt-4">
          <button
            onClick={() => setActiveTab("chat")}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold font-mono-dash transition-colors duration-200 ${
              activeTab === "chat" 
                ? "bg-cyan-950/40 text-cyan-400 border border-cyan-800/50" 
                : "text-slate-500 hover:text-slate-300 hover:bg-[#1e293b]/50 border border-transparent"
            }`}
          >
            <MessageSquare className="h-4 w-4" /> CLINICAL ENGINE
          </button>
          <button
            onClick={() => setActiveTab("dashboard")}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold font-mono-dash transition-colors duration-200 ${
              activeTab === "dashboard" 
                ? "bg-emerald-950/40 text-emerald-400 border border-emerald-800/50" 
                : "text-slate-500 hover:text-slate-300 hover:bg-[#1e293b]/50 border border-transparent"
            }`}
          >
            <LayoutDashboard className="h-4 w-4" /> CORPUS DASHBOARD
          </button>
        </div>
"""
    content = content.replace(
        '{/* Audit Cache Trail Section */}',
        sidebar_injection + '\n        {/* Audit Cache Trail Section */}'
    )

# 4. Main View conditional render
if "activeTab === \"dashboard\"" not in content:
    content = content.replace(
        '<main className="flex-1 flex flex-col min-w-0 bg-[#060b13] relative z-10">',
        '<main className="flex-1 flex flex-col min-w-0 bg-[#060b13] relative z-10">\n        {activeTab === "dashboard" ? (\n          <Dashboard />\n        ) : (\n        <>'
    )
    # Be careful matching </main>
    # The last </main> is at the bottom of the file
    last_main_idx = content.rfind('</main>')
    if last_main_idx != -1:
        content = content[:last_main_idx] + '        </>\n        )}\n      </main>' + content[last_main_idx+7:]

# 5. Drug Information Card
drug_card = """
                    {/* DRUG INFORMATION CARD */}
                    {activeItem?.a.metadata?.identity_profile && (
                      <div className="mb-6 p-4 rounded-xl border border-slate-700 bg-[#0e1726]/80 flex flex-col gap-3">
                        <div className="flex items-center gap-2 border-b border-slate-700 pb-2 mb-2">
                          <Database className="h-4 w-4 text-cyan-400" />
                          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono-dash">Drug Information Card</h3>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Generic Name</span>
                            <span className="text-sm text-emerald-400 font-bold">{activeItem.a.metadata.identity_profile.data?.generic_name?.value || "-"}</span>
                          </div>
                          
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Brand Names</span>
                            <span className="text-xs text-slate-300">{activeItem.a.metadata.identity_profile.data?.brand_names?.value?.join(", ") || "-"}</span>
                          </div>
                          
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Drug Class</span>
                            <span className="text-xs text-slate-300">{activeItem.a.metadata.identity_profile.data?.drug_class?.value?.[0] || "-"}</span>
                          </div>

                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Prescription</span>
                            <span className="text-xs text-slate-300">{activeItem.a.metadata.identity_profile.data?.prescription_status?.value || "-"}</span>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Primary Indications</span>
                            <span className="text-xs text-slate-300">{activeItem.a.metadata.identity_profile.data?.indications?.value?.join(", ") || "-"}</span>
                          </div>
                          
                          <div className="flex flex-col">
                            <span className="text-[10px] text-slate-500 font-bold uppercase font-mono-dash">Authority / Corpus Version</span>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="px-1.5 py-0.5 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-400 text-[9px] font-bold">🟢 DailyMed</span>
                              <span className="text-xs text-slate-400 font-mono-dash">v3.2</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
"""

if "DRUG INFORMATION CARD" not in content:
    content = content.replace(
        '{/* Result Content Text */}',
        drug_card + '\n                    {/* Result Content Text */}'
    )

# 6. Clinical Evidence Panel
evidence_panel = """
                    {/* CLINICAL EVIDENCE PANEL */}
                    <div className="mt-6 border-t border-slate-700/50 pt-4">
                      <div className="flex items-center gap-2 mb-3">
                        <ShieldAlert className="h-4 w-4 text-indigo-400" />
                        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono-dash">Clinical Evidence Used</h4>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div className="p-3 rounded-lg border border-slate-800 bg-[#090e17]/50 flex flex-col gap-1">
                          <span className="text-[10px] text-slate-500 font-mono-dash uppercase">Authorities</span>
                          <div className="flex gap-1 flex-wrap mt-1">
                            {Array.from(new Set(activeItem?.a.citations?.map(c => c.source) || [])).map(src => (
                              <Badge key={src as string} className="text-[9px] h-4 bg-emerald-950/40 text-emerald-400 border-emerald-900/50">🟢 {src as string}</Badge>
                            ))}
                          </div>
                        </div>
                        <div className="p-3 rounded-lg border border-slate-800 bg-[#090e17]/50 flex flex-col gap-1">
                          <span className="text-[10px] text-slate-500 font-mono-dash uppercase">Version</span>
                          <span className="text-xs text-slate-300 font-bold">Corpus v3.2</span>
                        </div>
                        <div className="p-3 rounded-lg border border-slate-800 bg-[#090e17]/50 flex flex-col gap-1">
                          <span className="text-[10px] text-slate-500 font-mono-dash uppercase">Chunks Used</span>
                          <span className="text-xs text-slate-300 font-bold">{activeItem?.a.citations?.length || 0}</span>
                        </div>
                        <div className="p-3 rounded-lg border border-slate-800 bg-[#090e17]/50 flex flex-col gap-1">
                          <span className="text-[10px] text-slate-500 font-mono-dash uppercase">Confidence</span>
                          <span className="text-xs text-emerald-400 font-bold">{activeItem?.a.metadata?.confidence || "High"}</span>
                        </div>
                      </div>
                      
                      {/* CLINICAL AUDIT COMPONENT */}
                      <ClinicalAudit audit={activeItem?.a.metadata?.audit} />
                      
                    </div>
"""

if "CLINICAL EVIDENCE PANEL" not in content:
    # Inject right after FormattedText inside the white block
    content = content.replace(
        '<FormattedText text={activeItem.a.answer} citations={activeItem.a.citations} />\n                  </div>',
        '<FormattedText text={activeItem.a.answer} citations={activeItem.a.citations} />\n                  ' + evidence_panel + '\n                  </div>'
    )


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patch complete")
