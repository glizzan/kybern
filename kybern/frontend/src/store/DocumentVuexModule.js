const DocumentVuexModule = {
    state: {
        documents: []           // {'pk': int, 'name': 'str', 'description': 'str', 'content': 'str'}
    },
    getters: {
        getDocumentData: (state, getters) => (document_pk) => {
            return state.documents.find(document => document.pk == document_pk)
        }
    },
    mutations: {
        ADD_OR_UPDATE_DOCUMENT (state, data) {
            // Maybe want to only update name & description here?
            // Otherwise we may replace lots of content when we're just editing the name
            for (let index in state.documents) {
                if (state.documents[index].pk == data.document_data.pk) {
                    state.documents.splice(index, 1, data.document_data)
                    return
                }
            }
            state.documents.push(data.document_data)
        },
        DELETE_DOCUMENT (state, data) {
            for (let index in state.documents) {
                if (state.documents[index].pk == data.deleted_document_pk) {
                    state.documents.splice(index, 1)
                }
            }
        }
    },
    actions: {
        async getDocuments({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_documents')
            var params = {}
            var implementationCallback = (response) => {
                for (let index in response.data.documents) {
                    commit('ADD_OR_UPDATE_DOCUMENT', { document_data : response.data.documents[index] })
                }
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addDocument({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "add_document", extra_data: payload.extra_data, data_to_return: "created_instance",
                name: payload.name, description: payload.description, content: payload.content }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_DOCUMENT', { document_data : response.data.created_instance })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editDocument({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "edit_document", extra_data: payload.extra_data, data_to_return: "edited_instance",
                alt_target: "document_" + payload.pk, name: payload.name, description: payload.description,
                content: payload.content }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_DOCUMENT', { document_data : response.data.edited_instance })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteDocument({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "delete_document", extra_data: payload.extra_data, data_to_return: "deleted_item_pk",
                alt_target: "document_" + payload.pk }
            var implementationCallback = (response) => {
                commit('DELETE_DOCUMENT', { deleted_document_pk : response.data.deleted_item_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
    }
}

export default DocumentVuexModule