<template>

    <div v-if="forum_name" class="bg-white p-3">

        <h3 class="mt-3">{{ forum_name }}</h3>
        <p>{{ forum_description }}</p>

        <router-link :to="{ name: 'edit-forum', params: { forum_id: forum_id } }" v-if="user_permissions.edit_forum">
            <b-button variant="outline-secondary" class="btn-sm" id="edit_forum_button">
                edit forum info</b-button>
        </router-link>

        <b-button v-if="user_permissions.delete_forum && !is_governance_forum" variant="outline-secondary"
            class="btn-sm" id="delete_forum_button" @click="delete_forum(forum_id)">delete forum</b-button>

        <router-link :to="{ name: 'action-history', params: {item_id: forum_id, item_model: 'forum', item_name: forum_name }}">
            <b-button variant="outline-secondary" class="btn-sm" id="forum_history_button">forum history</b-button>
        </router-link>

        <b-button variant="outline-secondary" id="forum_permissions_button" v-b-modal.item_permissions_modal
            class="btn-sm">list permissions</b-button>
        <item-permissions-modal :item_id=forum_id :item_model="'forum'" :item_name=forum_name>
        </item-permissions-modal>

        <b-button :href=json_export_url variant="outline-secondary" class="btn-sm" download>
            export as json</b-button>

        <error-component :message="delete_error_message"></error-component>

        <hr >

            <router-link :to="{ name: 'add-new-post'}" v-if="user_permissions.add_post">
                <b-button variant="outline-secondary" class="btn-sm mr-3 mb-3" id="add_post_button">
                    + add post</b-button>
            </router-link>

            <error-component :message="list_post_error_message"></error-component>

            <b-card v-for="{ pk, title, content, author, created } in posts" v-bind:key=pk
                                                class="bg-light text-info border-secondary mb-3">
                <router-link :to="{ name: 'post-detail', params: { forum_id: forum_id, post_id: pk } }">
                    <b-card-title class="post-link">{{ title }}</b-card-title></router-link>
                <p class="mb-1 text-secondary post-content">  {{ shorten_text(content, 100) }} </p>
                <small class="text-muted">Posted by {{ author }} on {{ display_date(created) }}</small>
            </b-card>

            <span v-if="Object.keys(posts).length === 0">There are no posts yet in this forum.</span>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ErrorComponent from '../utils/ErrorComponent'
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'


export default {

    props: ['forum_id'],
    store,
    components: { ErrorComponent, ItemPermissionsModal },
    mixins: [UtilityMixin],
    data: function() {
            return {
                delete_error_message: null,
                add_post_error_message: null,
                list_post_error_message: null,
                base_export_url: ""
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
        this.url_lookup('export_as_json').then(response => this.base_export_url = response)
    },
    computed: {
        ...Vuex.mapState({user_permissions: state => state.permissions.current_user_permissions}),
        ...Vuex.mapGetters(['getForumData', 'getPostsDataForForum', 'getUserName', 'url_lookup']),
        posts: function() {
            var forum = this.get_forum()
            if (forum) { return this.getPostsDataForForum(this.forum_id) } return undefined
        },
        forum_name: function() {
            var forum = this.get_forum()
            if (forum) { return forum.name } return undefined
        },
        forum_description: function() {
            var forum = this.get_forum()
            if (forum) { return forum.description } return undefined
        },
        is_governance_forum: function() {
            var forum = this.get_forum()
            if (forum) { return forum.special == "Gov" } return undefined
        },
        json_export_url: function() {
            return this.base_export_url + "?item_id=" + this.forum_id + "&item_model=forum"
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getPosts', 'addPost', 'deleteForum']),
        display_date(date) { return Date(date) },
        get_forum() {
            if (this.forum_id) {
                var forum = this.getForumData(this.forum_id)
                if (forum) { return forum }
            }
            return undefined
        },
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