import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
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
    collaborators: z.array(z.string()).optional(),
    image: z.string().optional(),
    repoLink: z.url().optional(),
    risk: z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']).optional(),
  })
});

// 2. Definição da coleção do TEAM
const team = defineCollection({
  // O 'glob' diz ao Astro: "Vá na pasta team e pegue todos os arquivos .md"
  loader: glob({ pattern: "**/*.md", base: "./src/content/team" }),
  
  schema: z.object({
    name: z.string(),
    code: z.string().optional(),
    role: z.string(),
    team: z.enum(['Red Team', 'Blue Team', 'Purple Team']).default('Blue Team'),
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
    bio: z.string().optional(),
    skills: z.array(z.string()),
    badge: z.object({
      label: z.string(),
      tooltip: z.string(),
    }).optional(),
    social: z.object({
      github: z.url().optional(),
      linkedin: z.url().optional(),
      twitter: z.url().optional(),
      website: z.url().optional(),
    }).optional(),

    // Perfis em plataformas de bug bounty. Lista aberta: uma plataforma nova
    // entra só pelo frontmatter, sem mexer em código.
    bugBounty: z.array(z.object({
      platform: z.string(),
      url: z.url(),
    })).optional(),
  })
});

// 3. Exportação ÚNICA
export const collections = {
  blog,
  team,
};