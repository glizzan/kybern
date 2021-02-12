<template>

    <span>

        <h3 class="mt-3">{{ forum_name }}</h3>
        <p>{{ forum_description }}</p>

        <router-link :to="{ name: 'edit-forum', params: { forum_id: forum_id } }" v-if="user_permissions.edit_forum">
            <b-button variant="outline-secondary" class="btn-sm" id="edit_forum_button">
                edit forum info</b-button>
        </router-link>

        <b-button variant="outline-secondary" class="btn-sm" id="delete_forum_button" v-if="user_permissions.delete_forum"
            @click="delete_forum(forum_id)">delete forum</b-button>

        <router-link :to="{ name: 'action-history', params: {item_id: forum_id, item_model: 'forum', item_name: forum_name }}">
            <b-button variant="outline-secondary" class="btn-sm" id="forum_history_button">forum history</b-button>
        </router-link>

        <router-link :to="{ name: 'item-permissions', params: { item_id: forum_id, item_model: 'forum', item_name: forum_name }}">
            <b-button variant="outline-secondary" id="forum_permissions_button" class="btn-sm">forum permissions</b-button>
        </router-link>

        <error-component :message="delete_error_message"></error-component>

        <hr >

            <router-link :to="{ name: 'add-new-post'}" v-if="user_permissions.add_post">
                <b-button variant="outline-secondary" class="btn-sm mr-3 mb-3" id="add_post_button">
                    + add post</b-button>
            </router-link>

            <error-component :message="list_post_error_message"></error-component>

            <router-link v-for="{ pk, title, content } in posts" v-bind:key=pk
                                :to="{ name: 'post-detail', params: { forum_id: forum_id, post_id: pk } }">
                <b-card :title=title v-bind:key=pk class="bg-light text-info border-secondary mb-3">
                    <p class="mb-1 text-secondary post-content">  {{ shorten_text(content, 100) }} </p>
                </b-card>
            </router-link>

            <span v-if="Object.keys(posts).length === 0">There are no posts yet in this forum.</span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['forum_id'],
    store,
    components: { ErrorComponent },
    mixins: [UtilityMixin],
    data: function() {
            return {
                delete_error_message: null,
                add_post_error_message: null,
                list_post_error_message: null
            }
        },
    created (){
        this.getPosts({ forum_pk: parseInt(this.forum_id) })
        .catch(error => { this.list_post_error_message = "Error getting post data from server " })
        var alt_target = "forum_" + this.forum_id
        this.checkPermissions({
            permissions:
                {edit_forum: {alt_target : alt_target},
                delete_forum: {alt_target : alt_target},
                add_post: {alt_target : alt_target}}
        }).catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({user_permissions: state => state.permissions.current_user_permissions}),
        ...Vuex.mapGetters(['getForumData', 'getPostsDataForForum', 'getUserName']),
        posts: function() {
            if (this.forum_id) { return this.getPostsDataForForum(this.forum_id) } return undefined
        },
        forum_name: function() {
            if (this.forum_id) { return this.getForumData(this.forum_id).name } return undefined
        },
        forum_description: function() {
            if (this.forum_id) { return this.getForumData(this.forum_id).description } return undefined
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getPosts', 'addPost', 'deleteForum']),
        display_date(date) { return Date(date) },
        delete_forum(forum_pk) {
            this.deleteForum({ pk: forum_pk })
            .then(response => { console.log(response); this.$router.push({name: 'home'}) })
            .catch(error => {  this.delete_error_message = error })
        },
        add_post() {
            this.addPost({ forum_pk: this.forum_id, title: this.post_title, content: this.post_content })
                .catch(error => {  this.add_post_error_message = error })
        }
    }

}

</script>