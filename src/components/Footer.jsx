import React from 'react';
import { Github, Linkedin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="border-t border-neutral-900 bg-neutral-950 py-16 mt-auto">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            
            {/* Lado Esquerdo: Identidade Técnica */}
            <div className="text-center md:text-left">
                <h3 className="text-white font-bold tracking-[0.2em] mb-2 uppercase text-sm">
                    0xD3LTA Research
                </h3>
                <div className="flex flex-col gap-1">
                    <p className="text-[10px] text-neutral-600 font-mono tracking-widest uppercase">
                        [ ADAPTIVE_THREAT_HUNTING ]
                    </p>
                </div>
            </div>

            {/* Lado Direito: Social Icons (Minimalistas e Quadrados) */}
            <div className="flex items-center gap-4">
                {/* GitHub */}
                <a 
                  href="https://github.com/SEU_GITHUB_AQUI" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="p-3 border border-neutral-800 bg-neutral-900 text-neutral-500 hover:text-black hover:bg-white hover:border-white transition-all duration-200"
                  aria-label="GitHub"
                >
                    <Github className="w-5 h-5" />
                </a>

                {/* LinkedIn */}
                <a 
                  href="https://linkedin.com/company/SEU_LINKEDIN_AQUI" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="p-3 border border-neutral-800 bg-neutral-900 text-neutral-500 hover:text-black hover:bg-white hover:border-white transition-all duration-200"
                  aria-label="LinkedIn"
                >
                    <Linkedin className="w-5 h-5" />
                </a>
            </div>
        </div>

        {/* Rodapé: Copyright Técnico */}
        <div className="mt-16 text-center border-t border-neutral-900 pt-8 flex flex-col gap-2">
            <p className="text-[10px] text-neutral-600 font-mono uppercase tracking-widest">
                © {new Date().getFullYear()} 0xD3LTA_RESEARCH // ALL_RIGHTS_RESERVED
            </p>
            <p className="text-[10px] text-neutral-700 font-mono uppercase tracking-widest">
                [ UNAUTHORIZED_ACCESS_IS_PROHIBITED ]
            </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;