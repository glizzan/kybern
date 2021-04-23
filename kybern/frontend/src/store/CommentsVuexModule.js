import Vue from 'vue'


const CommentsVuexModule = {

    state: {

        item_comments: {},          // { item_pk + "_" + item_model: [pk, pk, pk] }
        comments: {}                // { int(pk) : { text: x, created_at: x, author: pk, etc}}

    },

    getters: {
        getCommentData: (state, getters) => (comment_pk) => {
            return state.comments[comment_pk]
        },
        getCommentsForItem: (state, getters) => (item_key) => {
            var comments = []
            for (let index in state.item_comments[item_key]) {
                var comment_pk = state.item_comments[item_key][index]
                comments.push(state.comments[comment_pk])
            }
            return comments
        }
    },

    mutations: {

        REPLACE_ITEM_COMMENTS (state, data) {
            var item_key = data.item_id + "_" + data.item_model
            Vue.set(state.item_comments, item_key, data.pks)
        },
        ADD_COMMENT_TO_ITEM (state, data ) {
            var item_key = data.item_id + "_" + data.item_model
            var comment_index = state.item_comments[item_key].indexOf(data.comment_pk)
            if (comment_index == -1) { state.item_comments[item_key].push(parseInt(data.comment_pk)) }
        },
        REMOVE_COMMENT_FROM_ITEM (state, data) {
            var item_key = data.item_id + "_" + data.item_model
            var comment_index = state.item_comments[item_key].indexOf(data.comment_pk)
            if (comment_index > -1) { state.item_comments[item_key].splice(comment_index, 1) }
        },
        ADD_OR_UPDATE_COMMENT (state, data) {
            Vue.set(state.comments, data.pk, data.data)
        },
        DELETE_COMMENT (state, data) {
            Vue.delete(state.comments, data.pk);
        }

    },

    actions: {

        async getComments({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_comment_data')
            var params = { item_id: payload.item_id, item_model: payload.item_model }
            var implementationCallback = (response) => {
                for (let comment_pk in response.data.comments) {
                    commit('ADD_OR_UPDATE_COMMENT', { pk: comment_pk, data: response.data.comments[comment_pk] })
                }
                commit('REPLACE_ITEM_COMMENTS', { item_id: response.data.item_id, item_model: response.data.item_model,
                    pks: response.data.comment_pks })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addComment({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('add_comment')
            var params = { item_id: payload.item_id, item_model: payload.item_model, text: payload.text }
            var implementationCallback = (response) => {
                var pk = Object.keys(response.data.comment)[0]
                var data = response.data.comment[pk]
                commit('ADD_OR_UPDATE_COMMENT', { pk: pk, data: data })
                commit('ADD_COMMENT_TO_ITEM', { comment_pk: pk, item_id: payload.item_id, item_model: payload.item_model })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editComment({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('edit_comment')
            var params = { text: payload.text, comment_pk: payload.pk }
            var implementationCallback = (response) => {
                var pk = Object.keys(response.data.comment)[0]
                var data = response.data.comment[pk]
                commit('ADD_OR_UPDATE_COMMENT', { pk: pk, data: data })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteComment({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('delete_comment')
            var params = { comment_pk: payload.comment_pk }
            var implementationCallback = (response) => {
                commit('REMOVE_COMMENT_FROM_ITEM', { item_id: payload.item_id, item_model: payload.item_model,
                    comment_pk:response.data.deleted_comment_pk })
                commit('DELETE_COMMENT', { pk: response.data.deleted_comment_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }

        }
}

export default CommentsVuexModule
