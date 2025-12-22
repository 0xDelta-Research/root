import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders'; // Importante para Astro v5

// 1. Definição da coleção do BLOG
const blog = defineCollection({
  // O 'glob' diz ao Astro: "Vá na pasta blog e pegue todos os arquivos .md"
  loader: glob({ pattern: "**/*.md", base: "./src/content/blog" }),
  
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.date(),
    author: z.string(),
    team: z.enum(['Red Team', 'Blue Team']),
    category: z.enum([
      'Threat Hunting',
      'OSINT',
      'Detection Engineering',
      'Cyber Threat Intelligence',
      'Malware Analysis & Reverse Engineering',
      'Privacy Compliance Officer',
      'Offensive Techniques',
      'Web Security',
      'Network Security',
      'Cloud Security',
      'AD Security',
      'CVEs'
    ]),
    tags: z.array(z.string()).optional(),
    image: z.string().optional(),
    repoLink: z.string().url().optional(),
    risk: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']).optional(),
  })
});

// 2. Definição da coleção do TEAM
const team = defineCollection({
  // O 'glob' diz ao Astro: "Vá na pasta team e pegue todos os arquivos .md"
  loader: glob({ pattern: "**/*.md", base: "./src/content/team" }),
  
  schema: z.object({
    name: z.string(),
    role: z.string(),
    team: z.enum(['Red Team', 'Blue Team']).default('Blue Team'),
    specialty: z.string(),
    
    icon: z.enum([
      'Bug', 
      'Activity', 
      'Shield', 
      'Terminal', 
      'Globe', 
      'Fingerprint', 
      'Crosshair', 
      'Radio', 
      'ScanEye'
    ]), 
    
    status: z.string().default('ONLINE'),
    skills: z.array(z.string()),
    social: z.object({
      github: z.string().url().optional(),
      linkedin: z.string().url().optional(),
      twitter: z.string().url().optional(),
      website: z.string().url().optional(),
    }).optional(),
  })
});

// 3. Exportação ÚNICA
export const collections = {
  blog,
  team,
};