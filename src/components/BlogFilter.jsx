import React, { useState } from 'react';
import { Terminal, Filter, X, ChevronDown, ChevronUp, Shield, Bug, Trash2, RotateCcw, AlertTriangle } from 'lucide-react';
import LatestResearch from './LatestResearch';

const BlogFilter = ({ allPosts }) => {
  const [activeTeam, setActiveTeam] = useState('ALL'); 
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('');
  const [activeRisk, setActiveRisk] = useState('');
  
  const [showCategoryMenu, setShowCategoryMenu] = useState(false);
  const [showRiskMenu, setShowRiskMenu] = useState(false);

  // Listas
  const allBlueCategories = [ 'Threat Hunting', 'OSINT', 'Detection Engineering', 'Cyber Threat Intelligence', 'Malware Analysis & Reverse Engineering', 'Privacy Compliance Officer' ];
  const allRedCategories = [ 'Offensive Techniques', 'Web Security', 'Network Security', 'Cloud Security', 'AD Security', 'CVEs' ];
  const riskLevels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];

  // Métricas
  const totalRed = allPosts.filter(p => p.data.team === 'Red Team').length;
  const totalBlue = allPosts.filter(p => p.data.team === 'Blue Team').length;
  const authors = [...new Set(allPosts.map(p => p.data.author))].length;

  // Filtros
  const filteredPosts = allPosts.filter(post => {
    const matchTeam = activeTeam === 'ALL' ? true : post.data.team === activeTeam;
    const query = searchQuery.toLowerCase();
    const matchSearch = post.data.title.toLowerCase().includes(query) || 
                        post.data.description.toLowerCase().includes(query);
    const matchCategory = activeCategory === '' ? true : post.data.category === activeCategory;
    const matchRisk = activeRisk === '' ? true : post.data.risk === activeRisk;

    return matchTeam && matchSearch && matchCategory && matchRisk;
  });

  const clearFilters = () => {
    setActiveTeam('ALL');
    setSearchQuery('');
    setActiveCategory('');
    setActiveRisk('');
    setShowCategoryMenu(false);
    setShowRiskMenu(false);
  };

  const handleCategoryClick = (cat) => {
    setActiveCategory(activeCategory === cat ? '' : cat);
    setShowCategoryMenu(false);
  };

  const handleRiskClick = (risk) => {
    setActiveRisk(activeRisk === risk ? '' : risk);
    setShowRiskMenu(false);
  };

  const hasPosts = (cat) => allPosts.some(p => p.data.category === cat);
  const hasRisk = (r) => allPosts.some(p => p.data.risk === r);
  const isFilterActive = activeTeam !== 'ALL' || searchQuery !== '' || activeCategory !== '' || activeRisk !== '';

  // Helper de cores para o botão de risco (no dropdown)
  const getRiskColorInfo = (risk) => {
      const base = "border-neutral-900 text-neutral-600";
      switch(risk) {
          case 'CRITICAL': return `${base} hover:border-red-500 hover:text-red-500`;
          case 'HIGH': return `${base} hover:border-orange-500 hover:text-orange-500`;
          case 'MEDIUM': return `${base} hover:border-yellow-500 hover:text-yellow-500`;
          case 'LOW': return `${base} hover:border-blue-400 hover:text-blue-400`;
          case 'INFO': return `${base} hover:border-green-500 hover:text-green-500`;
          default: return base;
      }
  };

  return (
    <div className="space-y-8">
      
      {/* Dashboard */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-0 border-t border-l border-neutral-800">
         <div className="bg-neutral-950 border-r border-b border-neutral-800 p-6">
            <div className="text-[9px] text-neutral-600 uppercase tracking-widest mb-1">Total_Files</div>
            <div className="text-3xl font-bold text-white font-mono">{allPosts.length}</div>
         </div>
         <div className="bg-neutral-950 border-r border-b border-neutral-800 p-6">
            <div className="text-[9px] text-neutral-600 uppercase tracking-widest mb-1">Offensive</div>
            <div className="text-2xl font-bold text-neutral-400 font-mono">{totalRed}</div>
         </div>
         <div className="bg-neutral-950 border-r border-b border-neutral-800 p-6">
            <div className="text-[9px] text-neutral-600 uppercase tracking-widest mb-1">Defensive</div>
            <div className="text-2xl font-bold text-neutral-400 font-mono">{totalBlue}</div>
         </div>
         <div className="bg-neutral-950 border-r border-b border-neutral-800 p-6">
            <div className="text-[9px] text-neutral-600 uppercase tracking-widest mb-1">Operatives</div>
            <div className="text-2xl font-bold text-neutral-400 font-mono">{authors}</div>
         </div>
      </div>

      {/* Barra de Controle */}
      <div className="bg-neutral-900/50 border border-neutral-800 p-6 sticky top-24 z-30 shadow-2xl shadow-black backdrop-blur-md">
        
        <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
          
          <div className="flex flex-wrap gap-3 w-full md:w-auto items-center">
              
              {/* Botões de Time (AGORA COM CORES) */}
              <div className="flex gap-2">
                {['ALL', 'Blue Team', 'Red Team'].map((team) => {
                    let activeClass = 'bg-white text-black border-white'; // Default

                    // Lógica de Cor Ativa
                    if (team === 'Blue Team') activeClass = 'bg-blue-900/20 text-blue-400 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.2)]';
                    if (team === 'Red Team') activeClass = 'bg-red-900/20 text-red-500 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.2)]';

                    // Lógica de Hover (Quando não está ativo)
                    const hoverClass = team === 'Blue Team' ? 'hover:text-blue-400 hover:border-blue-500' 
                                     : team === 'Red Team' ? 'hover:text-red-500 hover:border-red-500' 
                                     : 'hover:text-white hover:border-white';

                    return (
                      <button
                        key={team}
                        onClick={() => { setActiveTeam(team); setActiveCategory(''); setActiveRisk(''); }}
                        className={`px-4 py-2 text-[9px] font-bold uppercase tracking-widest border transition-all duration-300 ${
                          activeTeam === team
                            ? activeClass
                            : `bg-transparent text-neutral-600 border-neutral-800 ${hoverClass}`
                        }`}
                      >
                        {team === 'ALL' ? 'ALL' : team.replace(' Team', '')}
                      </button>
                    )
                })}
              </div>

              <div className="h-6 w-[1px] bg-neutral-800 mx-1 hidden md:block"></div>

              {/* Botão de Categoria */}
              <button 
                onClick={() => { setShowCategoryMenu(!showCategoryMenu); setShowRiskMenu(false); }}
                className={`flex items-center gap-2 px-4 py-2 border text-[9px] font-bold uppercase tracking-widest transition-all ${
                    showCategoryMenu || activeCategory
                    ? 'bg-neutral-800 text-white border-white'
                    : 'bg-transparent text-neutral-600 border-neutral-800 hover:border-neutral-500 hover:text-white'
                }`}
              >
                <Filter className="w-3 h-3" />
                <span className="truncate max-w-[120px]">
                    {activeCategory || 'CATEGORY'}
                </span>
                {activeCategory ? (
                    <div role="button" onClick={(e) => { e.stopPropagation(); setActiveCategory(''); }}>
                        <X className="w-3 h-3" />
                    </div>
                ) : (
                    <ChevronDown className="w-3 h-3" />
                )}
              </button>

              {/* Botão de Risco */}
              <button 
                onClick={() => { setShowRiskMenu(!showRiskMenu); setShowCategoryMenu(false); }}
                className={`flex items-center gap-2 px-4 py-2 border text-[9px] font-bold uppercase tracking-widest transition-all ${
                    showRiskMenu || activeRisk
                    ? 'bg-neutral-800 text-white border-white'
                    : 'bg-transparent text-neutral-600 border-neutral-800 hover:border-neutral-500 hover:text-white'
                }`}
              >
                <AlertTriangle className="w-3 h-3" />
                <span>{activeRisk || 'RISK'}</span>
                {activeRisk ? (
                    <div role="button" onClick={(e) => { e.stopPropagation(); setActiveRisk(''); }}>
                        <X className="w-3 h-3" />
                    </div>
                ) : (
                    <ChevronDown className="w-3 h-3" />
                )}
              </button>

              {/* RESET */}
              {isFilterActive && (
                  <button 
                    onClick={clearFilters}
                    className="flex items-center gap-2 px-4 py-2 text-[9px] font-bold text-neutral-500 border border-neutral-800 hover:border-white hover:text-white transition-all uppercase tracking-widest animate-in fade-in zoom-in duration-300"
                  >
                    <RotateCcw className="w-3 h-3" /> RESET
                  </button>
              )}
          </div>

          {/* Busca */}
          <div className="relative w-full md:w-auto flex-grow md:max-w-xs">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Terminal className="h-4 w-4 text-neutral-600" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="grep 'search_query'..."
              className="block w-full pl-10 pr-3 py-2 bg-neutral-950 border border-neutral-800 text-white placeholder-neutral-600 text-xs font-mono focus:outline-none focus:border-neutral-500 transition-all focus:bg-black"
            />
          </div>
        </div>

        {/* Dropdown de Categorias */}
        {showCategoryMenu && (
            <div className="mt-6 pt-6 border-t border-neutral-800 grid grid-cols-1 md:grid-cols-2 gap-8 animate-in fade-in slide-in-from-top-2">
                
                {/* Blue Categories (AZUL) */}
                <div className="space-y-3">
                    <div className="flex items-center gap-2 text-blue-500 border-b border-blue-900/30 pb-2">
                        <Shield className="w-3 h-3" />
                        <span className="text-[9px] font-bold tracking-widest">DEFENSIVE_OPS</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {allBlueCategories.map(cat => {
                            const exists = hasPosts(cat);
                            const isActive = activeCategory === cat;
                            return (
                                <button 
                                    key={cat} 
                                    onClick={() => handleCategoryClick(cat)}
                                    className={`text-[9px] uppercase border px-3 py-1.5 transition-all ${
                                        isActive 
                                        ? 'bg-blue-900/20 text-blue-400 border-blue-500 font-bold' // Azul Ativo
                                        : exists 
                                            ? 'border-neutral-800 text-neutral-500 hover:border-blue-500 hover:text-blue-400' // Azul Hover
                                            : 'border-neutral-900 text-neutral-800 cursor-not-allowed'
                                    }`}
                                    disabled={!exists}
                                >
                                    {cat}
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* Red Categories (VERMELHO) */}
                <div className="space-y-3">
                    <div className="flex items-center gap-2 text-red-500 border-b border-red-900/30 pb-2">
                        <Bug className="w-3 h-3" />
                        <span className="text-[9px] font-bold tracking-widest">OFFENSIVE_OPS</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {allRedCategories.map(cat => {
                            const exists = hasPosts(cat);
                            const isActive = activeCategory === cat;
                            return (
                                <button 
                                    key={cat} 
                                    onClick={() => handleCategoryClick(cat)}
                                    className={`text-[9px] uppercase border px-3 py-1.5 transition-all ${
                                        isActive 
                                        ? 'bg-red-900/20 text-red-500 border-red-500 font-bold' // Vermelho Ativo
                                        : exists
                                            ? 'border-neutral-800 text-neutral-500 hover:border-red-500 hover:text-red-500' // Vermelho Hover
                                            : 'border-neutral-900 text-neutral-800 cursor-not-allowed'
                                    }`}
                                    disabled={!exists}
                                >
                                    {cat}
                                </button>
                            )
                        })}
                    </div>
                </div>
            </div>
        )}

        {/* Dropdown de Risco */}
        {showRiskMenu && (
             <div className="mt-6 pt-6 border-t border-neutral-800 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center gap-2 text-neutral-500 mb-4">
                    <AlertTriangle className="w-3 h-3" />
                    <span className="text-[9px] font-bold tracking-widest uppercase">Select Threat Level</span>
                </div>
                <div className="flex flex-wrap gap-3">
                    {riskLevels.map(risk => {
                        const exists = hasRisk(risk);
                        const isActive = activeRisk === risk;
                        return (
                            <button
                                key={risk}
                                onClick={() => handleRiskClick(risk)}
                                disabled={!exists}
                                className={`text-[9px] font-bold uppercase tracking-widest border px-4 py-2 transition-all ${
                                    isActive 
                                    ? 'bg-neutral-800 text-white border-white'
                                    : exists 
                                        ? getRiskColorInfo(risk) 
                                        : 'border-neutral-900 text-neutral-800 cursor-not-allowed'
                                }`}
                            >
                                {risk}
                            </button>
                        )
                    })}
                </div>
             </div>
        )}

      </div>

      {/* Resultados */}
      <div className="flex items-center justify-between text-[9px] text-neutral-600 border-b border-neutral-800 pb-2 uppercase tracking-widest mt-8">
         <span>
            RESULTS_FOUND: <span className="text-white font-bold">{filteredPosts.length}</span>
         </span>
         {(activeTeam !== 'ALL' || searchQuery || activeCategory) && (
            <button onClick={clearFilters} className="flex items-center gap-1 hover:text-white transition-colors">
                <X className="w-3 h-3" /> CLEAR_FILTERS
            </button>
         )}
      </div>

      {/* Grid */}
      {filteredPosts.length > 0 ? (
  // Mudei para 'stealth' (ou você pode simplesmente apagar a prop variant, pois stealth é o padrão)
  <LatestResearch posts={filteredPosts} variant="stealth" />
) : (
        <div className="py-32 text-center border border-neutral-800 bg-neutral-900/50">
            <Terminal className="w-12 h-12 text-neutral-800 mx-auto mb-4" />
            <p className="text-neutral-600 text-xs font-mono uppercase">DATABASE_EMPTY // NO_RECORDS</p>
            <button onClick={clearFilters} className="mt-4 text-[10px] text-neutral-500 hover:text-white underline">
                Clear search criteria
            </button>
        </div>
      )}
    </div>
  );
};

export default BlogFilter;