import Vue from 'vue'
import Vuex from 'vuex'

import ForumsVuexModule from './ForumsVuexModule.js'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        // concord_actions: ActionsVuexModule,  // use 'concord_actions' so as not to conflict with vuex actions
        forums: ForumsVuexModule
        // permissions: PermissionsVuexModule,
        // governance: GovernanceVuexModule,
        // comments: CommentVuexModule,
        // templates: TemplateVuexModule,
        // simplelists: SimplelistVuexModule
    },
    state: {
    },
    mutations: {
    },
    actions: {
    }
})
