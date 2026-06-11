import React from 'react';
import { motion } from 'framer-motion';
import { Terminal, Shield, Activity, Bug, Github, Linkedin, Globe, Fingerprint, Crosshair, Radio, ScanEye } from 'lucide-react';

const XIcon = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

const iconMap = {
  'Bug': Bug,
  'Shield': Shield,
  'Activity': Activity,
  'Terminal': Terminal,
  'Fingerprint': Fingerprint,
  'Crosshair': Crosshair,
  'Globe': Globe,
  'Radio': Radio,
  'ScanEye': ScanEye
};

/**
 * @param {object} props
 * @param {any[]} [props.members]
 */
const TeamProfiles = (props) => {
  const members = props.members || [];

  return (
    <div className="w-full">
      {/* Grid ajustado com gap um pouco maior (gap-6) */}
      <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-5 gap-6">
        {members.map((member, index) => {
          const IconComponent = iconMap[member.data.icon] || Terminal;
          const isRed = member.data.team === 'Red Team';

          // --- CORES DINÂMICAS ---
          const redStyles = {
            containerHover: 'hover:border-red-500 hover:shadow-[0_0_30px_-5px_rgba(220,38,38,0.3)] hover:bg-red-950/20',
            textHover: 'group-hover:text-red-400',
            borderHover: 'group-hover:border-red-500/50',
            iconBoxHover: 'group-hover:bg-red-500/10 group-hover:border-red-500 group-hover:text-red-400',
            skillHover: 'group-hover:border-red-900 group-hover:text-red-400 group-hover:bg-red-950/30'
          };

          const blueStyles = {
            containerHover: 'hover:border-blue-500 hover:shadow-[0_0_30px_-5px_rgba(59,130,246,0.3)] hover:bg-blue-950/20',
            textHover: 'group-hover:text-blue-400',
            borderHover: 'group-hover:border-blue-500/50',
            iconBoxHover: 'group-hover:bg-blue-500/10 group-hover:border-blue-500 group-hover:text-blue-400',
            skillHover: 'group-hover:border-blue-900 group-hover:text-blue-400 group-hover:bg-blue-950/30'
          };

          const styles = isRed ? redStyles : blueStyles;
          const accentText = isRed ? 'text-red-500' : 'text-blue-400';
          const accentBorderSoft = isRed ? 'border-red-500/30' : 'border-blue-500/30';

          return (
            <motion.div
              key={member.id || member.slug}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`
                group relative flex flex-col h-full 
                p-8  /* AUMENTADO DE p-5 PARA p-8 */
                border border-neutral-800 bg-neutral-900/40 
                transition-all duration-300 ease-out
                ${styles.containerHover}
              `}
            >
              {/* Link esticado: clicar em qualquer área do card abre o perfil */}
              <a
                href={`/team/${member.id}`}
                aria-label={`Open ${member.data.name} profile`}
                className="absolute inset-0 z-10 cursor-pointer"
              ></a>

              {/* HEADER: ID + Status */}
              <div className={`flex justify-between items-center mb-8 border-b border-neutral-800 pb-3 transition-colors ${styles.borderHover}`}>
                <span className={`text-[10px] font-mono text-neutral-600 uppercase tracking-widest transition-colors ${styles.textHover}`}>
                  ID: {member.data.name.substring(0, 3).toUpperCase()}_0{index + 1}
                </span>
                
                <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold text-neutral-500 tracking-widest transition-colors group-hover:text-white`}>
                        {member.data.status}
                    </span>
                    <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse"></span>
                </div>
              </div>

              {/* PERFIL: Ícone + Nome */}
              <div className="flex flex-col items-center text-center gap-5 mb-4 min-h-[140px] justify-center">
                {/* Ícone MAIOR */}
                <div className={`
                    w-16 h-16 border border-neutral-700 bg-neutral-950 flex items-center justify-center 
                    transition-all duration-300 ${styles.iconBoxHover} shrink-0
                `}>
                    <IconComponent className="w-8 h-8 text-neutral-400 transition-colors group-hover:text-inherit" />
                </div>
                
                <div className="w-full">
                    {/* Nome MAIOR */}
                    <h3 className="text-base font-bold text-white font-mono tracking-wider uppercase mb-2 truncate">
                        {member.data.name}
                    </h3>
                    <p className={`text-[10px] font-bold text-neutral-500 uppercase tracking-[0.2em] transition-colors ${styles.textHover} truncate`}>
                        {member.data.role}
                    </p>
                </div>
              </div>

              {/* BADGE: slot de altura fixa em TODOS os cards (vazio sem badge) p/ manter alinhamento */}
              <div className="h-6 flex items-center justify-center mb-4">
                {member.data.badge && (
                  <span className="relative group/badge z-20 inline-flex cursor-help">
                    <Bug className={`w-4 h-4 ${accentText} transition-colors duration-200 group-hover/badge:text-neutral-600`} />
                    <span className={`pointer-events-none absolute bottom-full left-1/2 mb-2 -translate-x-1/2 whitespace-nowrap border ${accentBorderSoft} bg-neutral-950 px-3 py-1.5 text-[10px] uppercase tracking-widest text-neutral-300 opacity-0 shadow-lg shadow-black/50 transition-opacity duration-200 group-hover/badge:opacity-100 z-30`}>
                      {member.data.badge.tooltip}
                    </span>
                  </span>
                )}
              </div>

              {/* LINKS SOCIAIS */}
              <div className="relative z-20 flex justify-center gap-5 h-10 items-center mb-6">
                {member.data.social?.github && (
                    <a href={member.data.social.github} target="_blank" rel="noopener noreferrer" className={`text-neutral-600 transition-colors ${styles.textHover}`}>
                        <Github className="w-5 h-5" />
                    </a>
                )}
                {member.data.social?.linkedin && (
                    <a href={member.data.social.linkedin} target="_blank" rel="noopener noreferrer" className={`text-neutral-600 transition-colors ${styles.textHover}`}>
                        <Linkedin className="w-5 h-5" />
                    </a>
                )}
                {member.data.social?.twitter && (
                    <a href={member.data.social.twitter} target="_blank" rel="noopener noreferrer" className={`text-neutral-600 transition-colors ${styles.textHover}`}>
                        <XIcon className="w-[18px] h-[18px]" />
                    </a>
                )}
                {member.data.social?.website && (
                    <a href={member.data.social.website} target="_blank" rel="noopener noreferrer" className={`text-neutral-600 transition-colors ${styles.textHover}`}>
                        <Globe className="w-5 h-5" />
                    </a>
                )}
              </div>

              {/* SKILLS */}
              <div className="space-y-4">
                <div className={`h-[1px] w-full bg-neutral-800 transition-colors ${styles.borderHover}`}></div>
                <div className="flex flex-wrap justify-center gap-2">
                  {member.data.skills.slice(0, 3).map((skill, i) => (
                    <span key={i} className={`
                        text-[10px] font-mono border border-neutral-800 px-2 py-1 uppercase 
                        text-neutral-500 transition-all duration-300 cursor-default whitespace-nowrap
                        ${styles.skillHover}
                    `}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Crosshair */}
              <div className={`absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${isRed ? 'text-red-500' : 'text-blue-500'}`}>
                <Crosshair className="w-4 h-4" />
              </div>

            </motion.div>
          );
        })}
      </div>

    </div>
  );
};

export default TeamProfiles;