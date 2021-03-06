import Vue from 'vue'
import TemplatesApp from './views/TemplatesApp'
import router from './router'
import store from './store'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

Vue.use(BootstrapVue)  // Make BootstrapVue available throughout your project
Vue.use(IconsPlugin)

Vue.config.productionTip = false


new Vue({
  router,
  store,
  render: h => h(TemplatesApp)
}).$mount('#templateApp')
