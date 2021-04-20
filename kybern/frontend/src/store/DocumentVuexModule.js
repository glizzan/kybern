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
            var url = await getters.url_lookup('add_document')
            var params = { name: payload.name, description: payload.description, content: payload.content }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_DOCUMENT', { document_data : response.data.document_data })
                return response.data.document_data
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editDocument({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('edit_document')
            var params = { name: payload.name, document_pk: payload.document_pk, description: payload.description,
                 content: payload.content }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_DOCUMENT', { document_data : response.data.document_data })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteDocument({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('delete_document')
            var params = { document_pk: payload.document_pk }
            console.log("Params: ", params)

            var implementationCallback = (response) => {
                commit('DELETE_DOCUMENT', { deleted_document_pk : response.data.deleted_document_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
    }
}

export default DocumentVuexModule