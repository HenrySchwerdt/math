import DefaultTheme from 'vitepress/theme'
import ResearchOverview from './ResearchOverview.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ResearchOverview', ResearchOverview)
  },
}
