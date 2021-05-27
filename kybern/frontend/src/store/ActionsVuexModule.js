import Vue from 'vue'
import axios from '../store/axios_instance'


const ActionsVuexModule = {

    state: {
        actions: {}                // { 'group_1' : [ { action_dict }, { action_dict } ] }
    },
    getters: {
        getActionData: (state, getters) => (action_pk) => {
            for (let action_group in state.actions) {
                var match = state.actions[action_group].find(action => action.action_pk == action_pk)
                if (match) { return match }
            }
        }
    },
    mutations: {
        REPLACE_ACTIONS_FOR_ITEM (state, data) {
                Vue.set(state.actions, data.item_key.toLowerCase(), data.action_data)
            },
        ADD_OR_UPDATE_ACTION (state, data) {
            // Takes in action data and the item_key for the item the action targets

            var item_key = data.item_key.toLowerCase()

            if (!state.actions[item_key]) {
                Vue.set(state.actions, item_key, [])
            }

            for (let index in state.actions[item_key]) {
                if (state.actions[item_key][index].action_pk == data.action_data.action_pk) {
                    state.actions[item_key].splice(index, 1, data.action_data)
                    return
                }
            }

            state.actions[item_key].push(data.action_data)  // If we get here, we're adding the action
        }
    },
    actions: {
        updateActions ({ state, commit, rootState, dispatch }, payload) {
            // Given a single action or multiple actions, calls addOrUpdateAction with those pks,
            // triggering updates of their data

            var data =  payload.response.data

            if (data.multiple_actions) {
                for (let index in data.actions) {
                    dispatch('addOrUpdateAction', { action_pk: data.actions[index].action_pk })
                }
            } else {
                dispatch('addOrUpdateAction', { action_pk: data.action_pk })
            }

        },
        async loadActions({ state, commit, rootState, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_action_data_for_target')
            var item_model = payload.item_model == "list" ? "simplelist" : payload.item_model
            var params = { item_id: payload.item_id, item_model: item_model }
            var implementationCallback = (response) => {
                var item_key = payload.item_id + "_" + payload.item_model
                commit('REPLACE_ACTIONS_FOR_ITEM', { action_data : response.data.action_data, item_key : item_key })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})

        },
        async addOrUpdateAction ({ state, commit, rootState, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_action_data')
            var params = { action_pk : payload.action_pk }

            axios.post(url, params).then(response => {
                var action_data = response.data.action_data
                var item_key = action_data.action_target_pk + "_" + action_data.action_target_model
                commit('ADD_OR_UPDATE_ACTION', { action_data : action_data, item_key : item_key })
            })
            .catch(error => {  console.log(error); throw error })

        },

        async addNoteToAction ({ state, commit, rootState, dispatch, getters }, payload) {
            var url = await getters.url_lookup('add_note_to_action')
            var params = { action_pk : payload.action_pk, note : payload.note }
            var implementationCallback = (response) => {
                dispatch('addOrUpdateAction', { action_pk: payload.action_pk })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
    }
}

export default ActionsVuexModule