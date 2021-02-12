const SimplelistVuexModule = {
    state: {
        lists: []           // {'pk': x, 'name': y, 'description': z, 'rows': ['str', 'str']}
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
        ADD_ROW (state, data) {
            var list_to_edit = state.lists.find(list => list.pk == data.list_pk)
            if (data.index || data.index == 0) {
                list_to_edit.rows.splice(data.index, 0, data.row_content)
            } else {
                list_to_edit.rows.push(data.row_content)
            }
        },
        EDIT_ROW (state, data) {
            var list_to_edit = state.lists.find(list => list.pk == data.list_pk)
            list_to_edit.rows.splice(data.index, 1, data.row_content)
        },
        MOVE_ROW (state, data) {
            var list_to_edit = state.lists.find(list => list.pk == data.list_pk)
            var row_to_move = list_to_edit.rows.splice(data.old_index, 1)
            list_to_edit.rows.splice(data.new_index, 0, row_to_move[0])
        },
        DELETE_ROW (state, data) {
            var list_to_edit = state.lists.find(list => list.pk == data.list_pk)
            list_to_edit.rows.splice(data.index, 1)
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
        async addList({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('add_list')
            var params = { name: payload.name, description: payload.description,
                configuration: payload.configuration }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_LIST', { list_data : response.data.list_data })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editList({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('edit_list')
            var params = { name: payload.name, description: payload.description,
                list_pk: payload.list_pk, configuration: payload.configuration }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_LIST', { list_data : response.data.list_data })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteList({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('delete_list')
            var params = { list_pk: payload.list_pk }
            var implementationCallback = (response) => {
                commit('DELETE_LIST', { deleted_list_pk : response.data.deleted_list_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addRow({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('add_row')
            var params = { list_pk: payload.list_pk, row_content: payload.row_content,
                index: payload.index }
            var implementationCallback = (response) => {
                commit('ADD_ROW', { list_pk : payload.list_pk, row_content: payload.row_content,
                    index: payload.index })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editRow({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('edit_row')
            var params = { list_pk: payload.list_pk, row_content: payload.row_content,
                index: payload.index }
            var implementationCallback = (response) => {
                commit('EDIT_ROW', { list_pk : payload.list_pk, row_content: payload.row_content,
                    index: payload.index })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async moveRow({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('move_row')
            var params = { list_pk: payload.list_pk, old_index: payload.old_index, new_index: payload.new_index,
                index: payload.index }
            var implementationCallback = (response) => {
                commit('MOVE_ROW', { list_pk : payload.list_pk, old_index: payload.old_index, new_index: payload.new_index })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteRow({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('delete_row')
            var params = { list_pk: payload.list_pk, index: payload.index }
            var implementationCallback = (response) => {
                commit('DELETE_ROW', { list_pk: payload.list_pk, index: payload.index })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
    }
}

export default SimplelistVuexModule