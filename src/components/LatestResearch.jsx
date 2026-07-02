import React from 'react';
import { ArrowRight, Bug, Shield, User, Users, AlertTriangle } from 'lucide-react';

/**
 * AQUI ESTÁ A CORREÇÃO DO ERRO:
 * O JSDoc abaixo avisa ao sistema que 'posts' aceita qualquer lista de dados.
 * 
 * @param {object} props
 * @param {any[]} [props.posts]
 * @param {'stealth' | 'explicit'} [props.variant]
 */
const LatestResearch = ({ posts = [], variant = 'stealth' }) => {
  if (!posts || posts.length === 0) return null;

  // Helper para cor do Risco (Só ativa no Hover)
  const getRiskHoverClass = (risk) => {
    switch (risk) {
      case 'CRITICAL': return 'group-hover:text-red-500 group-hover:border-red-500 group-hover:bg-red-500/10';
      case 'HIGH': return 'group-hover:text-orange-500 group-hover:border-orange-500 group-hover:bg-orange-500/10';
      case 'MEDIUM': return 'group-hover:text-yellow-500 group-hover:border-yellow-500 group-hover:bg-yellow-500/10';
      case 'INFO': return 'group-hover:text-green-500 group-hover:border-green-500 group-hover:bg-green-500/10';
      default: return 'group-hover:text-blue-400 group-hover:border-blue-400';
    }
  };

  return (
    // Grid com GAP-6 para espaçamento entre cards
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {posts.map((post) => {
        const isRed = post.data.team === 'Red Team';
        const risk = post.data.risk;

        // Cores do Time (Red/Blue) que só aparecem no Hover
        const teamHoverBorder = isRed ? 'hover:border-red-500/50' : 'hover:border-blue-500/50';
        const teamHoverShadow = isRed ? 'hover:shadow-[0_0_20px_rgba(220,38,38,0.15)]' : 'hover:shadow-[0_0_20px_rgba(59,130,246,0.15)]';
        const teamTextHover = isRed ? 'group-hover:text-red-500' : 'group-hover:text-blue-400';
        const teamBgHover = isRed ? 'hover:bg-red-950/10' : 'hover:bg-blue-950/10';

        return (
          <a
            key={post.id || post.slug}
            href={`/blog/${post.slug || post.id}`}
            className={`
                group relative flex flex-col h-full p-6
                border border-neutral-800 bg-neutral-900/40 backdrop-blur-sm
                transition-all duration-300 ease-out cursor-pointer
                ${teamHoverBorder} ${teamHoverShadow} ${teamBgHover}
            `}
          >

            {/* Linha decorativa no topo */}
            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-neutral-800 to-transparent group-hover:via-white/20 transition-all"></div>

            {/* Cabeçalho */}
            <div className="flex justify-between items-start mb-6 relative z-10">
               
               {/* Lógica do Badge: Cinza por padrão -> Cor do Risco no Hover */}
               <div className="flex flex-col gap-2">
                  {risk ? (
                     <div className={`
                        flex items-center gap-2 px-2 py-1 border text-[9px] font-bold uppercase tracking-widest w-fit transition-all duration-300
                        border-neutral-800 text-neutral-600
                        ${getRiskHoverClass(risk)}
                     `}>
                        <AlertTriangle className="w-3 h-3" /> {risk}
                     </div>
                  ) : null}

                  {/* Categoria */}
                  <span className={`
                    text-[9px] uppercase tracking-widest border border-neutral-800 px-2 py-1 rounded w-fit
                    text-neutral-600 transition-colors duration-300
                    ${isRed ? 'group-hover:border-red-900 group-hover:text-red-500' : 'group-hover:border-blue-900 group-hover:text-blue-400'}
                  `}>
                      {post.data.category}
                  </span>
               </div>
              
               <span className="text-[10px] font-mono text-neutral-700 group-hover:text-neutral-500 transition-colors">
                  {new Date(post.data.pubDate).toISOString().split('T')[0]}
               </span>
            </div>

            {/* Conteúdo */}
            <div className="mb-6 flex-grow relative z-10">
               <h3 className="text-xl font-bold text-neutral-200 group-hover:text-white transition-colors leading-tight mb-3">
                 {post.data.title}
               </h3>
               
               <p className="text-sm text-neutral-500 group-hover:text-neutral-400 transition-colors line-clamp-3 leading-relaxed">
                 {post.data.description}
               </p>
            </div>

            {/* Rodapé Detalhado */}
            <div className="flex items-center justify-between mt-auto pt-4 border-t border-neutral-800 group-hover:border-neutral-700 transition-colors relative z-10">
                
                {/* Autor com Ícone e Box */}
                <div className="flex items-center gap-2">
                    <div className={`
                        w-8 h-8 rounded border flex items-center justify-center transition-colors duration-300
                        bg-neutral-950 border-neutral-800
                        ${isRed ? 'group-hover:border-red-900 group-hover:bg-red-950/20' : 'group-hover:border-blue-900 group-hover:bg-blue-950/20'}
                    `}>
                        <User className={`w-3 h-3 text-neutral-600 ${teamTextHover}`} />
                    </div>
                    <span className={`text-xs font-mono font-bold text-neutral-600 ${teamTextHover}`}>
                        {post.data.author}
                    </span>

                    {/* Badge de Colaboração */}
                    {post.data.collaborators?.length > 0 && (
                        <span
                            title={`Collaboration with ${post.data.collaborators.join(', ')}`}
                            className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider border border-neutral-700 text-neutral-500 bg-neutral-950 group-hover:text-neutral-300 group-hover:border-neutral-600 transition-colors"
                        >
                            <Users className="w-2.5 h-2.5" />
                            Collab{post.data.collaborators.length > 1 ? ` +${post.data.collaborators.length}` : ''}
                        </span>
                    )}
                </div>

                <ArrowRight className={`w-4 h-4 transition-all group-hover:translate-x-1 text-neutral-700 ${teamTextHover}`} />
            </div>
          </a>
        );
      })}
    </div>
  );
};

export default LatestResearch;