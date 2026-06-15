import React from 'react';
import { Github, Linkedin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="border-t border-neutral-900 bg-neutral-950 py-8 mt-auto">
      <div className="container mx-auto px-4">

        <div className="flex flex-row justify-between items-center">

          {/* Identidade */}
          <div>
            <h3 className="text-white font-bold tracking-[0.2em] uppercase text-sm">
              0xD3LTA Research
            </h3>
            <p className="text-[10px] text-neutral-600 font-mono tracking-widest uppercase">
              [ ADAPTIVE_THREAT_HUNTING ]
            </p>
          </div>

          {/* Social Icons */}
          <div className="flex items-start gap-3">
            <a
              href="https://github.com/0xDelta-Research"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 border border-neutral-800 bg-neutral-900 text-neutral-500 hover:text-white hover:border-white hover:bg-white/10 transition-all duration-200"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>

            <a
              href="https://www.linkedin.com/company/0xdeltaresearch/"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 border border-neutral-800 bg-neutral-900 text-neutral-500 hover:text-[#0A66C2] hover:border-[#0A66C2] hover:bg-[#0A66C2]/10 transition-all duration-200"
              aria-label="LinkedIn"
            >
              <Linkedin className="w-5 h-5" />
            </a>
          </div>
        </div>

        {/* Rodapé: Copyright */}
      </div>
    </footer>
  );
};

export default Footer;
