import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// Componente isolado para o Glitch do "3" vira "E"
const GlitchDigit = () => {
  const [char, setChar] = useState('3');
  const [isGlitching, setIsGlitching] = useState(false);

 useEffect(() => {
    const triggerGlitch = () => {
      // Começa o efeito
      setIsGlitching(true);
      
      // Primeira fase: troca rápida inicial (3 -> E -> 3 -> E)
      let count = 0;
      const initialFlickers = 3;
      
      const interval = setInterval(() => {
        setChar(prev => prev === '3' ? 'E' : '3');
        count++;
        
        if (count >= initialFlickers) {
          clearInterval(interval);
          setChar('E'); // Fixa no E
          
          // Segunda fase: E fica visível por mais tempo
          setTimeout(() => {
            // Terceira fase: pisca de volta para 3
            let backCount = 0;
            const backFlickers = 3;
            
            const backInterval = setInterval(() => {
              setChar(prev => prev === 'E' ? '3' : 'E');
              backCount++;
              
              if (backCount >= backFlickers) {
                clearInterval(backInterval);
                setChar('3'); // Garante que volta para 3
                setIsGlitching(false);
                
                // Agenda o próximo glitch
                setTimeout(triggerGlitch, Math.random() * 4000 + 2000);
              }
            }, 120); // Mais devagar na volta
          }, 800); // E fica visível por 800ms
        }
      }, 120); // Velocidade mais devagar (era 50ms)
    };

    // Inicia o primeiro glitch
    const timer = setTimeout(triggerGlitch, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <span className={`inline-block ${isGlitching ? 'opacity-70 text-neutral-400' : ''}`}>
      {char}
    </span>
  );
};

const Header = () => {
  return (
    <motion.header 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="border-b border-neutral-800 bg-[#050505]/90 backdrop-blur-md sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* LOGO */}
          <a href="/" className="flex items-center gap-3 group cursor-pointer decoration-0">
            <motion.div 
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
            >
              <img src="/delta-favicon.png" alt="0xD3LTA" className="h-10 w-auto opacity-90 group-hover:opacity-100 transition-opacity" />
            </motion.div>
            
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-white font-mono tracking-wider group-hover:text-neutral-300 transition-colors flex">
                {/* 0xD + GLITCH + LTA */}
                <span>0xD</span>
                <GlitchDigit />
                <span>LTA</span>
              </h1>
              <p className="text-[10px] text-neutral-500 font-mono tracking-widest uppercase">
                [ RESEARCH_UNIT ]
              </p>
            </div>
          </a>
          
          {/* MENU DE NAVEGAÇÃO */}
          <nav className="hidden md:flex items-center gap-8">
            <a href="/" className="text-neutral-400 hover:text-white transition-colors text-xs uppercase tracking-widest font-bold">
              Home
            </a>
            <a href="/blog" className="text-neutral-400 hover:text-white transition-colors text-xs uppercase tracking-widest font-bold">
              Research
            </a>
            <a href="/#team" className="text-neutral-400 hover:text-white transition-colors text-xs uppercase tracking-widest font-bold">
              Operators
            </a>
            <a href="/contact" className="text-neutral-400 hover:text-white transition-colors text-xs uppercase tracking-widest font-bold">
              Contact
            </a>
          </nav>
          
          {/* STATUS */}
          <div className="flex items-center gap-2">
            <div className="hidden sm:block text-[10px] text-neutral-500 font-mono border border-neutral-800 px-3 py-1 rounded bg-neutral-900/50">
              <span className="animate-pulse text-green-500 inline-block mr-2">●</span> 
              SYSTEM_ONLINE
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;