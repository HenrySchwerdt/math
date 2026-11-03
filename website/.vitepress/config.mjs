import { defineConfig } from 'vitepress'
import ledger from './ledger.json' with { type: 'json' }

export default defineConfig({
  title: 'Math Research',
  description: 'An open notebook for classical mathematical research: questions, tasks, evidence and exact proof status.',
  base: '/math/',
  lang: 'en-US',
  cleanUrls: true,
  head: [['link', { rel: 'icon', type: 'image/svg+xml', href: '/math/logo.svg' }]],
  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'Math Research',
    nav: [
      { text: 'Research', link: '/research/' },
      { text: 'Tasks', link: '/research/tasks' },
      { text: 'Results', link: '/research/results' },
      { text: 'Activity', link: '/research/activity' },
    ],
    search: { provider: 'local' },
    socialLinks: [{ icon: 'github', link: ledger.repository }],
    sidebar: [
      { text: 'Research notebook', items: [
        { text: 'Overview', link: '/research/' },
        { text: 'Open and completed tasks', link: '/research/tasks' },
        { text: 'Results & evidence', link: '/research/results' },
        { text: 'Activity timeline', link: '/research/activity' },
        { text: 'All records', link: '/research/records/' },
      ] },
      { text: 'Projects', items: ledger.projects.map(p => ({ text: p.title, link: `/research/projects/${p.slug}` })) },
      { text: 'How research works', collapsed: false, items: [
        { text: 'Methodology', link: '/research/guides/methodology' },
        { text: 'Evidence & review', link: '/research/guides/review' },
        { text: 'Lean 4 verification', link: '/research/guides/lean' },
        { text: 'Cross-provider handoff', link: '/research/guides/handoff' },
        { text: 'Start a session', link: '/research/guides/claude' },
        { text: 'Update this website', link: '/research/guides/website' },
      ] },
    ],
    outline: [2, 3],
    footer: {
      message: 'Open questions. Reproducible evidence. No consensus-based proof.',
      copyright: `Snapshot ${ledger.commit.slice(0, 7)} · Built from the shared Git ledger`,
    },
  },
})
