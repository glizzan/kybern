import Vue from 'vue'

const ForumsVuexModule = {
    state: {
        forums: {pk:1, name:'fake', description: 'also fake'},      // [ { pk: pk, name: name, description: description }],
        posts: []                       // [ { pk: pk, forum_pk: forum_pk, title: title, content: content, author: author, etc } ] }
    },
    getters: {
        getForumData: (state) => (forum_pk) => {
            return state.forums.find(forum => forum.pk == forum_pk)
        },
        getPostsDataForForum: (state) => (forum_pk) => {
            return state.posts.filter(post => post.forum_pk == forum_pk)
        },
        getPostData: (state) => (post_pk) => {
            return state.posts.find(post => post.pk == post_pk)
        }
    },
    mutations: {

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
        getForum({ commit, dispatch}, payload) {
            const url = "{% url 'get_forum' target=object.pk %}"
            const params = { forum_pk: payload.forum_pk }
            const implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_FORUM', { forum_data : response.data.forum_data })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        addForum({ commit, dispatch}, payload) {
            const url = "{% url 'add_forum' target=object.pk %}"
            const params = { name: payload.name, description: payload.description }
            const implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_FORUM', { forum_data : response.data.forum_data })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        editForum({ commit, dispatch}, payload) {
            const url = "{% url 'edit_forum' target=object.pk %}"
            const params = { pk: payload.pk, name: payload.name, description: payload.description }
            const implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_FORUM', { forum_data : response.data.forum_data })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        deleteForum({ commit, dispatch}, payload) {
            const url = "{% url 'delete_forum' target=object.pk %}"
            const params = { pk: payload.pk }
            const implementationCallback = (response) => {
                commit('DELETE_FORUM', { pk : response.data.deleted_forum_pk })
                // TODO: need to delete permissions set on forum in state.permissions plus key-value in item_permissions
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        getPosts({ commit, dispatch}, payload) {
            const url = "{% url 'get_posts_for_forum' target=object.pk %}"
            const params = { forum_pk: payload.forum_pk }
            const implementationCallback = (response) => {
                for (let index in response.data.posts) {
                    commit('ADD_POST', { post_data: response.data.posts[index] })
                }
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        getPost({ commit, dispatch}, payload) {
            const url = "{% url 'get_post' target=object.pk %}"
            const params = { post_pk: payload.post_pk }
            const implementationCallback = (response) => {
                commit('ADD_POST', { post_data: response.data.post })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        addPost ({ commit, dispatch }, payload) {
            const url = "{% url 'add_post' target=object.pk %}"
            const params = { forum_pk: payload.forum_pk, title: payload.title, content: payload.content  }
            const implementationCallback = (response) => {
                commit('ADD_POST', { post_data: response.data.post_data})
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        editPost ({ commit, dispatch }, payload) {
            const url = "{% url 'edit_post' target=object.pk %}"
            const params = { pk: payload.pk, title: payload.title, content: payload.content  }
            const implementationCallback = (response) => {
                commit('EDIT_POST', { post_data: response.data.post_data})
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        deletePost ({ commit, dispatch }, payload) {
            const url = "{% url 'delete_post' target=object.pk %}"
            const params = { pk: payload.pk, forum_pk: payload.forum_pk }
            const implementationCallback = (response) => {
                commit('DELETE_POST', { pk: response.data.deleted_post_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
     }
}

export default ForumsVuexModule