import Vue from 'vue'


const ForumsVuexModule = {
    state: {
        forums: [],                     // [ { pk: pk, name: name, description: description }],
        posts: []                       // [ { pk: pk, forum_pk: forum_pk, title: title, content: content, author: author, etc } ] }
    },
    getters: {
        getForumData: (state, getters) => (forum_pk) => {
            return state.forums.find(forum => forum.pk == parseInt(forum_pk))
        },
        getPostsDataForForum: (state, getters) => (forum_pk) => {
            return state.posts.filter(post => post.forum_pk == forum_pk)
        },
        getPostData: (state, getters) => (post_pk) => {
            return state.posts.find(post => post.pk == post_pk)
        }
    },
    mutations: {

        SET_FORUMS (state, data) {
            Vue.set(state, "forums", data.forums)
        },

        ADD_OR_UPDATE_FORUM (state, data) {
            for (let index in state.forums) {
                if (state.forums[index].pk == data.forum_data.pk) {
                    state.forums.splice(index, 1, data.forum_data)
                    return
                }
            }
            state.forums.push(data.forum_data)
        },
        DELETE_FORUM (state, data) {
            for (let index in state.forums) {
                if (state.forums[index].pk == data.pk) {
                    state.forums.splice(index, 1)
                }
            }
        },
        ADD_POST (state, data) {
            for (let index in state.posts) {
                if (state.posts[index].pk == data.post_data.pk) {
                    return   // if it already exists, don't add it
                }
            }
            state.posts.push(data.post_data)
        },
        EDIT_POST (state, data) {
            for (let index in state.posts) {
                if (state.posts[index].pk == data.post_data.pk) {
                    Vue.set(state.posts, index, data.post_data)
                }
            }
        },
        DELETE_POST (state, data) {
            for (let index in state.posts) {
                if (state.posts[index].pk == data.pk) {
                    state.posts.splice(index, 1)
                }
            }
        }
    },
    actions: {
        async getForums({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('get_forum_data')
            var implementationCallback = (response) => {
                commit('SET_FORUMS', { forums: response.data.forums })
            }
            return dispatch('getAPIcall', { url: url, implementationCallback: implementationCallback})
        },
        async getForum({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_forum')
            var params = { forum_pk: payload.forum_pk }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_FORUM', { forum_data : response.data.forum_data })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addForum({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "add_forum", data_to_return: "created_instance", extra_data: payload.extra_data,
                name: payload.name, description: payload.description }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_FORUM', { forum_data : response.data.created_instance })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editForum({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "edit_forum", data_to_return: "edited_instance", extra_data: payload.extra_data,
                alt_target: "forum_" + payload.pk, name: payload.name, description: payload.description }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_FORUM', { forum_data : response.data.edited_instance })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deleteForum({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "delete_forum", data_to_return: "deleted_item_pk", alt_target: "forum_" + payload.pk,
                    extra_data: payload.extra_data }
            var implementationCallback = (response) => {
                commit('DELETE_FORUM', { pk : response.data.deleted_item_pk })
                // TODO: need to delete permissions set on forum in state.permissions plus key-value in item_permissions
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async getPosts({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_posts_for_forum')
            var params = { forum_pk: payload.forum_pk }
            var implementationCallback = (response) => {
                for (let index in response.data.posts) {
                    commit('ADD_POST', { post_data: response.data.posts[index] })
                }
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async getPost({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_post')
            var params = { post_pk: payload.post_pk }
            var implementationCallback = (response) => {
                commit('ADD_POST', { post_data: response.data.post })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async  addPost ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "add_post", data_to_return: "created_instance", extra_data: payload.extra_data,
                alt_target: "forum_" + payload.forum_id, title: payload.title, content: payload.content }
                var implementationCallback = (response) => {
                commit('ADD_POST', { post_data: response.data.created_instance})
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async editPost ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "edit_post", data_to_return: "edited_instance", extra_data: payload.extra_data,
                alt_target: "post_" + payload.pk, title: payload.title, content: payload.content  }
            var implementationCallback = (response) => {
                commit('EDIT_POST', { post_data: response.data.edited_instance})
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async deletePost ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "delete_post", data_to_return: "deleted_item_pk", alt_target: "post_" + payload.pk,
                extra_data: payload.extra_data}
            var implementationCallback = (response) => {
                commit('DELETE_POST', { pk: response.data.deleted_item_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
     }
}

export default ForumsVuexModule
