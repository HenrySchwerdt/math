import DefaultTheme from 'vitepress/theme'
import TaskBoard from './TaskBoard.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('TaskBoard', TaskBoard)
  },
}
