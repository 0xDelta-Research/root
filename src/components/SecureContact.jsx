import React, { useState } from 'react';
import { Mail, Key, Copy, Check, ShieldAlert, Globe } from 'lucide-react';

const SecureContact = () => {
  const [copied, setCopied] = useState(false);

  const pgpKey = `-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.2.32 (MingW32)

mQENBGFuGqwBCAC9... (CONTEÚDO DA CHAVE) ...
...F8q4W5l/5e8=
=Y5d+
-----END PGP PUBLIC KEY BLOCK-----`;

  const handleCopy = () => {
    navigator.clipboard.writeText(pgpKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full max-w-6xl mx-auto">
      
      <div className="mb-12 text-center">
        <h2 className="text-3xl font-bold text-white uppercase tracking-widest flex items-center justify-center gap-3">
          Secure Uplink
        </h2>
        <div className="h-1 w-12 bg-neutral-800 mx-auto mt-4"></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-0 border border-neutral-800">
        
        {/* LADO ESQUERDO: E-MAIL E REGRAS */}
        <div className="bg-neutral-900/30 p-10 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-neutral-800">
            
            <div className="text-center mb-8">
                <div className="inline-flex p-3 border border-neutral-800 bg-neutral-950 mb-6 rounded-full">
                    <Mail className="w-6 h-6 text-neutral-400" />
                </div>
                
                <p className="text-[10px] text-neutral-500 uppercase tracking-[0.3em] mb-2">
                    Primary Frequency
                </p>
                
                <a 
                    href="mailto:root@0xd3lta.org" 
                    className="text-2xl md:text-3xl font-bold text-white font-mono hover:text-neutral-300 transition-colors tracking-tighter"
                >
                    root@0xd3lta.org
                </a>
            </div>

            {/* PROTOCOLOS DE COMUNICAÇÃO (AQUI ESTÁ A MUDANÇA) */}
            <div className="bg-neutral-950 border border-neutral-800 p-6 rounded-sm">
                <p className="text-[10px] text-neutral-500 font-bold uppercase tracking-widest mb-4 border-b border-neutral-800 pb-2">
                    // Communication_Protocols
                </p>
                
                <div className="space-y-4">
                    {/* Caso 1: Business */}
                    <div className="flex gap-3 items-start">
                        <Globe className="w-4 h-4 text-neutral-600 mt-0.5 shrink-0" />
                        <div>
                            <p className="text-xs font-bold text-white uppercase">General / Business</p>
                            <p className="text-[10px] text-neutral-500 leading-relaxed">
                                Standard cleartext email allowed. Response time: &lt;24h.
                            </p>
                        </div>
                    </div>

                    {/* Caso 2: Whistleblower/Intel */}
                    <div className="flex gap-3 items-start">
                        <ShieldAlert className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                        <div>
                            <p className="text-xs font-bold text-red-500 uppercase">Sensitive Intel / Leaks</p>
                            <p className="text-[10px] text-neutral-500 leading-relaxed">
                                <span className="text-white font-bold">PGP ENCRYPTION MANDATORY.</span><br/>
                                Do not send raw data without encryption.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        {/* LADO DIREITO: CHAVE PGP */}
        <div className="bg-neutral-950 p-8 lg:p-10 relative group flex flex-col h-full">
            <div className="flex justify-between items-center mb-6 border-b border-neutral-800 pb-4">
                <div className="flex items-center gap-2 text-neutral-400">
                    <Key className="w-4 h-4" />
                    <span className="text-[10px] font-bold uppercase tracking-widest">PGP_PUBLIC_KEY</span>
                </div>
                <button 
                    onClick={handleCopy}
                    className="flex items-center gap-2 text-[10px] uppercase font-bold text-neutral-500 hover:text-white transition-colors border border-transparent hover:border-neutral-700 px-2 py-1 rounded"
                >
                    {copied ? <span className="text-white">KEY_COPIED</span> : <span>COPY_KEY</span>}
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                </button>
            </div>
            
            <div className="font-mono text-[10px] text-neutral-500 break-all leading-relaxed opacity-60 flex-grow overflow-hidden relative selection:bg-white selection:text-black min-h-[200px]">
                {pgpKey}
                {/* Gradiente para esconder o texto longo */}
                <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-neutral-950 to-transparent"></div>
            </div>
            
            <div className="mt-6 text-center border-t border-neutral-900 pt-4">
                <p className="text-[9px] text-neutral-700 font-mono">
                    // FINGERPRINT: 8F32 19A0 4C5D 92B1 ...
                </p>
            </div>
        </div>

      </div>

    </div>
  );
};

export default SecureContact;