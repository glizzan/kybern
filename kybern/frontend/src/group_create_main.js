import Vue from 'vue'
import GroupCreateApp from './views/GroupCreateApp.vue'
import router from './router'
import store from './store'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

Vue.use(BootstrapVue)  // Make BootstrapVue available throughout your project
Vue.use(IconsPlugin)

Vue.config.productionTip = false


new Vue({
  router,
  store,
  render: h => h(GroupCreateApp)
}).$mount('#kybernApp')
