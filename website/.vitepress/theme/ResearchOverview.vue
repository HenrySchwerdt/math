<script setup>
import { computed, ref } from 'vue'
import { withBase } from 'vitepress'
import ledger from '../ledger.json'

const query = ref('')
const project = ref('all')
const status = ref('all')
const kind = ref('all')
const types = { TSK: 'Task', HYP: 'Hypothesis', RUN: 'Run', EXP: 'Experiment', ALG: 'Algorithm', PRF: 'Proof', REV: 'Review', DEC: 'Decision', PAP: 'Paper' }
const openTasks = ledger.records.filter(r => r.type === 'TSK' && r.status !== 'completed').length
const proofs = ledger.records.filter(r => ['HYP', 'PRF'].includes(r.type) && r.proof_status === 'formally-verified').length
const records = computed(() => ledger.records.filter(r =>
  (project.value === 'all' || r.project === project.value) &&
  (status.value === 'all' || r.status === status.value) &&
  (kind.value === 'all' || r.type === kind.value) &&
  `${r.title} ${r.id} ${r.question} ${r.project} ${r.next_action}`.toLowerCase().includes(query.value.toLowerCase())
))
const href = r => withBase(`/research/records/${r.id}`)
</script>

<template>
  <section class="research-overview" aria-labelledby="notebook-title">
    <div class="notebook-heading">
      <div><p class="eyebrow">THE SHARED NOTEBOOK</p><h2 id="notebook-title">Follow the work, not the hype.</h2></div>
      <a class="source-snapshot" :href="`${ledger.repository}/tree/${ledger.commit}`">Source {{ ledger.commit.slice(0, 7) }}{{ ledger.dirty ? ' + local changes' : '' }} ↗</a>
    </div>
    <div class="research-stats" aria-label="Research summary">
      <div><strong>{{ ledger.projects.length }}</strong><span>Research projects & infrastructure</span></div>
      <div><strong>{{ openTasks }}</strong><span>Open, active or blocked tasks</span></div>
      <div><strong>{{ proofs }}</strong><span>Formally verified research records</span></div>
    </div>
    <p class="evidence-note">The universal ECDLP and integer-factorization targets remain open and unproved. Successful infrastructure checks are shown as run outcomes, never as mathematical discoveries.</p>
    <div class="project-links">
      <a v-for="p in ledger.projects" :key="p.slug" :href="withBase(`/research/projects/${p.slug}`)">
        <span class="project-label">{{ p.slug === 'platform' ? 'INFRASTRUCTURE' : 'RESEARCH PROJECT' }}</span>
        <strong>{{ p.title }} <span aria-hidden="true">↗</span></strong>
        <span>{{ p.hypotheses }} {{ p.hypotheses === 1 ? 'hypothesis' : 'hypotheses' }} · {{ p.open_tasks }} {{ p.open_tasks === 1 ? 'task' : 'tasks' }} remaining</span>
      </a>
    </div>
    <div class="notebook-heading records-heading"><h2 id="records-title">The research ledger</h2><a :href="withBase('/research/tasks')">Browse tasks →</a></div>
    <div class="ledger-filters" role="search" aria-label="Filter research records">
      <label class="search-label"><span>Search the ledger</span><input v-model="query" type="search" placeholder="Question, task, concept or ID…" /></label>
      <label><span>Project</span><select v-model="project"><option value="all">All projects</option><option v-for="p in ledger.projects" :key="p.slug" :value="p.slug">{{ p.title }}</option></select></label>
      <label><span>Record type</span><select v-model="kind"><option value="all">All types</option><option v-for="(label, code) in types" :key="code" :value="code">{{ label }}</option></select></label>
      <label><span>Status</span><select v-model="status"><option value="all">All statuses</option><option>open</option><option>active</option><option>blocked</option><option>completed</option></select></label>
    </div>
    <p class="result-count" aria-live="polite">{{ records.length }} {{ records.length === 1 ? 'record' : 'records' }} · UTC timestamps · Updated on deployment</p>
    <div class="ledger-list" aria-labelledby="records-title">
      <article v-for="r in records" :key="r.id" class="ledger-record">
        <div class="record-meta"><span>{{ types[r.type] }}</span><span>{{ r.project }}</span><time :datetime="r.updated_at">{{ r.updated_at.slice(0, 10) }}</time></div>
        <h3><a :href="href(r)">{{ r.title }}</a></h3>
        <p>{{ r.question }}</p>
        <div class="record-states"><span class="state-badge" :class="`state-${r.status}`">{{ r.status }}</span><span>Outcome: <strong>{{ r.outcome || 'pending' }}</strong></span><span>Proof: <strong>{{ r.proof_status }}</strong></span></div>
        <a class="record-detail" :href="href(r)">Read task, result & evidence →</a>
      </article>
      <p v-if="records.length === 0" class="empty-ledger">No records match these filters. Try another term or project.</p>
    </div>
  </section>
</template>
