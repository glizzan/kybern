import Vue from 'vue'
import GroupDetailApp from './views/GroupDetailApp'
import router from './router'
import store from './store'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

Vue.use(BootstrapVue)  // Make BootstrapVue available throughout your project
Vue.use(IconsPlugin)

Vue.config.productionTip = false


new Vue({
  router,
  store,
  render: h => h(GroupDetailApp)
}).$mount('#kybernApp')
