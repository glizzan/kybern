import Vue from 'vue'


const TemplatesVuexModule = {

    state: {
        templates: {}               // dict of list, with dict keys as scopes
    },

    getters: {
        scopeTemplates: (state, getters) => (scope) => {
            return state.templates[scope]
        }
    },

    mutations: {
        REPLACE_SCOPE_TEMPLATES (state, data) {
            Vue.set(state.templates, data.scope, data.templates)
        }
    },

    actions: {
        async getTemplatesForScope({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_templates_for_scope')
            var params = { scope: payload.scope }
            var implementationCallback = (response) => {
                commit('REPLACE_SCOPE_TEMPLATES', { scope: response.data.scope,
                    templates: response.data.templates })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async applyTemplate({ commit, state, dispatch, getters, rootState}, payload) {
            var target_model = null
            var target_pk = null
            if (payload.target_model && payload.target_pk) {
                target_model = payload.target_model; target_pk = payload.target_pk;
            } else {
                target_model = 'group'; target_pk = rootState.group_pk;
            }
            var url = await getters.url_lookup('apply_template')
            var params = { supplied_fields: payload.supplied_fields, target_pk: target_pk, target_model: target_model,
                       template_model_pk : payload.template_model_pk }
            var implementationCallback = (response) => { }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
    }
}

export default TemplatesVuexModule