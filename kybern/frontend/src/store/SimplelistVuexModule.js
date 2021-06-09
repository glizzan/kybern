import Vue from 'vue'

const SimplelistVuexModule = {
    state: {
        lists: []           // {'pk': x, 'name': y, 'description': z,
                            // 'rows': {unique_id: {col_name: value, col_name: value}}
                            //  'columns': { col_name: {}}
    },
    getters: {
        getListData: (state, getters) => (list_pk) => {
            return state.lists.find(list => list.pk == list_pk)
        }
    },
    mutations: {
        ADD_OR_UPDATE_LIST (state, data) {
            // Maybe want to only update name & description here?
            // Otherwise we may replace 10,000 rows when we're just editing the name
            for (let index in state.lists) {
                if (state.lists[index].pk == data.list_data.pk) {
                    state.lists.splice(index, 1, data.list_data)
                    return
                }
            }
            state.lists.push(data.list_data)
        },
        DELETE_LIST (state, data) {
            for (let index in state.lists) {
                if (state.lists[index].pk == data.deleted_list_pk) {
                    state.lists.splice(index, 1)
                }
            }
        },
        ADD_OR_EDIT_ROW (state, data) {
            var list_to_edit = state.lists.find(list => list.pk == data.list_pk)
            Vue.set(list_to_edit.rows, data.unique_id, data.row_content)
        },
        DELETE_ROW (state, data) {
            var list_to_edit = state.lists.find(list => list.pk == data.list_pk)
            Vue.delete(list_to_edit.rows, data.unique_id)
        }
    },
    actions: {
        async getLists({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_lists')
            var params = {}
            var implementationCallback = (response) => {
                for (let list in response.data.lists) {
                    commit('ADD_OR_UPDATE_LIST', { list_data : response.data.lists[list] })
                }
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async getList({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_list')
            var params = { list_pk: payload.list_pk }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_LIST', { list_data : response.data.list })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addList({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "add_list", data_to_return: "created_instance", extra_data: payload.extra_data,
                name: payload.name, description: payload.description }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_LIST', { list_data : response.data.created_instance })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editList({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "edit_list", data_to_return: "edited_instance", extra_data: payload.extra_data,
                alt_target: "simplelist_" + payload.pk, name: payload.name, description: payload.description }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_LIST', { list_data : response.data.edited_instance })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteList({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "delete_list", data_to_return: "deleted_item_pk", extra_data: payload.extra_data,
                alt_target: "simplelist_" + payload.pk }
            var implementationCallback = (response) => {
                commit('DELETE_LIST', { deleted_list_pk : response.data.deleted_item_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addColumn({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "add_column_to_list", extra_data: payload.extra_data, alt_target: payload.alt_target,
                data_to_return: "target_pk", column_name: payload.column_name, required: payload.required,
                default_value: payload.default_value }
            var implementationCallback = (response) => {
                // not very performant, but for now just refresh the list so we don't need to apply logic to the rows
                dispatch('getList', { list_pk: response.data.target_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editColumn({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "edit_column_in_list", extra_data: payload.extra_data, alt_target: payload.alt_target,
                data_to_return: "target_pk", column_name: payload.column_name, required: payload.required,
                default_value: payload.default_value, new_name: payload.new_name }
            var implementationCallback = (response) => {
                // not very performant, but for now just refresh the list so we don't need to apply logic to the rows
                dispatch('getList', { list_pk: response.data.target_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteColumn({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "delete_column_from_list", extra_data: payload.extra_data, alt_target: payload.alt_target,
                data_to_return: "target_pk", column_name: payload.column_name}
            var implementationCallback = (response) => {
                // not very performant, but for now just refresh the list so we don't need to apply logic to the rows
                dispatch('getList', { list_pk: response.data.target_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addRow({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "add_row_to_list", extra_data: payload.extra_data,
                alt_target: "simplelist_" + payload.list_pk, data_to_return: "unique_id", row_content: payload.row_content,
                list_pk: payload.list_pk }
            var implementationCallback = (response) => {
                commit('ADD_OR_EDIT_ROW', { list_pk : payload.list_pk, row_content: payload.row_content,
                                            unique_id: response.data.unique_id })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editRow({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "edit_row_in_list", extra_data: payload.extra_data,
                row_content: payload.row_content, unique_id: payload.unique_id, list_pk: payload.list_pk,
                alt_target: "simplelist_" + payload.list_pk }
            var implementationCallback = (response) => {
                commit('ADD_OR_EDIT_ROW', { list_pk : payload.list_pk, row_content: payload.row_content,
                                            unique_id: payload.unique_id })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteRow({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "delete_row_in_list", extra_data: payload.extra_data, list_pk: payload.list_pk,
                alt_target: "simplelist_" + payload.list_pk, unique_id: payload.unique_id }
            var implementationCallback = (response) => {
                commit('DELETE_ROW', { list_pk: payload.list_pk, unique_id: payload.unique_id })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
    }
}

export default SimplelistVuexModule