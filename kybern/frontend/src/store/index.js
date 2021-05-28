import Vue from 'vue'
import Vuex from 'vuex'

import axios from '../store/axios_instance'

import ActionsVuexModule from './ActionsVuexModule'
import CommentsVuexModule from './CommentsVuexModule'
import DocumentVuexModule from './DocumentVuexModule'
import ForumsVuexModule from './ForumsVuexModule'
import GovernanceVuexModule from './GovernanceVuexModule'
import PermissionsVuexModule from './PermissionsVuexModule'
import SimplelistVuexModule from './SimplelistVuexModule'
import TemplatesVuexModule from './TemplatesVuexModule'


Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        concord_actions: ActionsVuexModule,  // use 'concord_actions' so as not to conflict with vuex actions
        documents: DocumentVuexModule,
        forums: ForumsVuexModule,
        permissions: PermissionsVuexModule,
        governance: GovernanceVuexModule,
        comments: CommentsVuexModule,
        templates: TemplatesVuexModule,
        simplelists: SimplelistVuexModule
    },
    state: {
        group_pk: null,
        group_name: "",
        group_description: "",
        user_pk: null,
        user_name: "",
        urls: {},
    },
    getters: {
        url_lookup: (state, getters) => (url_name) => {

            console.log("Looking for ", url_name)
            console.log("In ", state.urls)

            return new Promise((resolve, reject) => {

                var url_lookup_interval = setInterval(function() {
                    if (Object.keys(state.urls).length == 0) return;
                    clearInterval(url_lookup_interval);
                    resolve("/" + state.urls[url_name])
                }, 1000);

            })
        }
    },
    mutations: {
        UPDATE_GROUP_PK (state, data) { state.group_pk = data.group_pk },
        UPDATE_GROUP_NAME (state, data) { state.group_name = data.group_name },
        UPDATE_GROUP_DESCRIPTION (state, data) { state.group_description = data.group_description },
        SET_URL_MAP(state, data) { state.urls = data.urls },
        UPDATE_USER_PK (state, data) { state.user_pk = data.user_pk },
        UPDATE_USER_NAME (state, data) { state.user_name = data.user_name }
    },
    actions: {

        // Initialization actions

        initialize_url_data({ commit, state, dispatch }, payload) {
            commit('SET_URL_MAP', { urls : payload.urls })
        },

        initialize_group_data({ commit, state, dispatch }, payload) {
            commit('SET_URL_MAP', { urls : payload.urls })
            commit('UPDATE_GROUP_NAME', { group_name : payload.group_name })
            commit('UPDATE_GROUP_DESCRIPTION', { group_description : payload.group_description })
            commit('UPDATE_GROUP_PK', { group_pk : payload.group_pk })
            commit('UPDATE_USER_PK', { user_pk: payload.user_pk })
            commit('UPDATE_USER_NAME', { user_name: payload.user_name })
        },

        get_url_data({ commit, state, dispatch }, payload) {
            // possibly delete this since we're getting urls another way
            var url = "/groups/api/get_urls/" + state.group_pk + "/"
            return axios.post(url).then(response => {
                commit('SET_URL_MAP', { urls : payload.urls })
            })
            .catch(error => { console.log(error); throw error })
        },

        // Group info actions

        async changeGroupName({ commit, getters, state, dispatch }, payload) {
            var url = await getters.url_lookup('change_group_name')
            var params = { group_pk : payload.group_pk, new_name : payload.new_name }
            var implementationCallback = (response) => {
                commit('UPDATE_GROUP_NAME', { group_name : response.data.group_name })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        async changeGroupDescription({ commit, getters, state, dispatch }, payload) {
            var url = await getters.url_lookup('change_group_description')
            var params = { group_pk : payload.group_pk, group_description : payload.group_description }
            var implementationCallback = (response) => {
                commit('UPDATE_GROUP_DESCRIPTION', { group_description : response.data.group_description })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        actionAPIcall({ commit, state, dispatch }, payload) {

            var url = payload.url
            var params = payload.params
            var implementationCallback = payload.implementationCallback

            return axios.post(url, params).then(response => {

                if (response.data.action_status != "invalid") {
                    dispatch('updateActions', { response: response })
                }
                if (response.data.action_status == "implemented") {
                    implementationCallback(response)
                }
                return response

            }).catch(error => {console.log("Error: ", error); throw error })

        },

        getAPIcall({ commit, state, dispatch }, payload) {
        // we might not need this method, since view should be an action, but let's keep it for now

            var url = payload.url
            var params = payload.params
            var implementationCallback = payload.implementationCallback

            return axios.post(url, params).then(response => { implementationCallback(response) })
            .catch(error => { console.log(error); throw error })
        }
    }
})
