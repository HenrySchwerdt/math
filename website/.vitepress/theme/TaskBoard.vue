<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import ledger from '../ledger.json'

const project = ref('all')
const query = ref('')
const selected = ref(null)
const details = ref(null)
const columns = [{ id: 'open', title: 'Open' }, { id: 'active', title: 'In progress' }, { id: 'blocked', title: 'Blocked' }, { id: 'completed', title: 'Completed' }]
const tasks = computed(() => ledger.tasks.filter(t =>
  (project.value === 'all' || t.project === project.value) &&
  `${t.task_key || t.id} ${t.title} ${t.question}`.toLowerCase().includes(query.value.toLowerCase())
))
const recordUrl = id => withBase(`/research/records/${id}`)
const taskKey = task => task.task_key || task.id
const projectName = slug => ledger.projects.find(p => p.slug === slug)?.title || slug
const formatTime = value => value.replace('T', ' ').replace(/\.\d+Z$/, ' UTC').replace(/Z$/, ' UTC')

function syncUrl() {
  const url = new URL(window.location.href)
  if (project.value === 'all') url.searchParams.delete('project')
  else url.searchParams.set('project', project.value)
  if (selected.value) url.searchParams.set('task', taskKey(selected.value))
  else url.searchParams.delete('task')
  window.history.replaceState(window.history.state ?? {}, '', url)
}
function chooseProject(slug) { project.value = slug; syncUrl() }
async function openTask(task) {
  selected.value = task
  await nextTick()
  details.value.showModal()
  syncUrl()
}
function closeTask() { selected.value = null; syncUrl() }
onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (ledger.projects.some(p => p.slug === params.get('project'))) project.value = params.get('project')
  const task = ledger.tasks.find(t => taskKey(t) === params.get('task') || t.id === params.get('task'))
  if (task) openTask(task)
})
</script>

<template>
  <div class="task-workspace">
    <aside class="project-rail" aria-label="Research projects">
      <p class="rail-label">PROJECTS</p>
      <button :class="{ selected: project === 'all' }" @click="chooseProject('all')">All projects <span>{{ ledger.tasks.length }}</span></button>
      <button v-for="p in ledger.projects" :key="p.slug" :class="{ selected: project === p.slug }" @click="chooseProject(p.slug)">{{ p.title }} <span>{{ ledger.tasks.filter(t => t.project === p.slug).length }}</span></button>
      <div class="rail-links"><a :href="withBase('/research/')">Project documentation</a><a :href="withBase('/research/results')">Results & evidence</a><a :href="withBase('/research/activity')">All recorded activity</a></div>
    </aside>
    <main class="board-main">
      <div class="board-header"><div><p class="board-breadcrumb">Math Research / {{ project === 'all' ? 'All projects' : projectName(project) }}</p><h1>Task board</h1></div><a class="board-source" :href="`${ledger.repository}/tree/${ledger.commit}`">{{ ledger.commit.slice(0, 7) }}{{ ledger.dirty ? ' + local changes' : '' }} ↗</a></div>
      <div class="board-toolbar"><label><span class="sr-only">Search tasks</span><input v-model="query" type="search" placeholder="Search by task ID or title" /></label><span>{{ tasks.length }} {{ tasks.length === 1 ? 'task' : 'tasks' }} · Read-only</span></div>
      <div class="task-columns" aria-label="Task status board">
        <section v-for="column in columns" :key="column.id" class="task-column" :aria-labelledby="`column-${column.id}`">
          <h2 :id="`column-${column.id}`"><span class="column-dot" :class="column.id"></span>{{ column.title }} <span class="column-count">{{ tasks.filter(t => t.status === column.id).length }}</span></h2>
          <button v-for="task in tasks.filter(t => t.status === column.id)" :key="task.id" class="task-card" @click="openTask(task)">
            <span class="task-key">{{ taskKey(task) }}</span><h3>{{ task.title }}</h3><p>{{ projectName(task.project) }}</p>
            <div class="task-card-footer"><span>{{ task.activity.filter(e => e.kind === 'command').length }} recorded commands</span><span>{{ task.related.filter(r => r.type === 'REV').length }} reviews</span></div>
            <div v-if="task.outcome && task.status === 'completed'" class="task-card-outcome">Outcome: {{ task.outcome }}</div>
          </button>
          <p v-if="!tasks.some(t => t.status === column.id)" class="empty-column">No tasks</p>
        </section>
      </div>
      <p class="board-caption">Click a task to see its scope, recorded steps, results and next action. Status is updated from the Git ledger after deployment.</p>
    </main>
    <dialog ref="details" class="task-dialog" aria-labelledby="task-heading" @close="closeTask">
      <template v-if="selected">
        <div class="task-dialog-header"><span class="task-key">{{ taskKey(selected) }} <span class="task-status">{{ columns.find(c => c.id === selected.status)?.title }}</span></span><button class="close-dialog" aria-label="Close task details" @click="details.close()">×</button></div>
        <h2 id="task-heading">{{ selected.title }}</h2>
        <p class="task-dialog-project">{{ projectName(selected.project) }} · Created {{ formatTime(selected.created_at) }}</p>
        <div class="task-status-fields"><span>Outcome <strong>{{ selected.outcome || 'pending' }}</strong></span><span>Proof status <strong>{{ selected.proof_status }}</strong></span></div>
        <section><h3>Research question</h3><p>{{ selected.question }}</p></section>
        <section><h3>Completion criteria</h3><ul><li v-for="criterion in selected.success_criteria" :key="criterion">{{ criterion }}</li></ul></section>
        <section class="task-next"><h3>Next action</h3><p>{{ selected.next_action }}</p></section>
        <section><h3>Recorded steps</h3><p v-if="selected.activity.length === 1" class="task-muted">No execution has been recorded for this task yet.</p>
          <ol class="task-timeline"><li v-for="(event, index) in selected.activity" :key="`${event.time}-${index}`"><time :datetime="event.time">{{ formatTime(event.time) }}</time><h4>{{ event.title }}</h4><pre v-if="event.argv"><code>{{ event.argv.join(' ') }}</code></pre><p>{{ event.detail }}</p><ul v-if="event.checks?.length"><li v-for="check in event.checks" :key="check">{{ check }}</li></ul><div class="event-links"><a :href="recordUrl(event.record)">Record ↗</a><a v-if="event.evidence" :href="event.evidence">Command evidence ↗</a></div></li></ol>
        </section>
        <section v-if="selected.related.length"><h3>Linked records</h3><ul class="related-task-records"><li v-for="record in selected.related" :key="record.id"><a :href="recordUrl(record.id)">{{ record.task_key || record.type }} · {{ record.title }}</a><span>{{ record.status }} · {{ record.outcome || 'pending' }} · proof: {{ record.proof_status }}</span></li></ul></section>
        <a class="full-task-link" :href="recordUrl(selected.id)">Full task record, canonical ID & sources →</a>
      </template>
    </dialog>
  </div>
</template>
