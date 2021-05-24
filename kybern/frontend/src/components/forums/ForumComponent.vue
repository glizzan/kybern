<template>

    <div v-if="forum" class="bg-white p-3 rounded">

        <div class="title-and-actions mb-4">

            <span class="h3 font-weight-bold">{{ forum.name }}</span>

            <resource-action-icons class="float-right" v-on:delete="delete_forum" :item_id=item_id
                :item_model="'forum'" :item_name=forum.name :edit_permission="user_permissions.edit_forum"
                :delete_permission="user_permissions.delete_forum && !is_governance_forum" :export_url=json_export_url
                :export_text="'export as json'"></resource-action-icons>

        </div>

        <action-response-component :response=delete_forum_response class="mt-4"></action-response-component>

        <p>{{ forum.description }}</p>

        <hr >

        <form-button-and-modal v-if="user_permissions.add_post" :item_model="'post'"
            :button_text="'+ add post'" :supplied_params="{'forum_id':item_id}"></form-button-and-modal>

        <b-card v-for="{ pk, title, content, author, created } in posts" v-bind:key=pk
                                            class="bg-light text-info mt-3 rounded">
            <router-link :to="{ name: 'post-detail', params: { forum_id: item_id, item_id: pk } }">
                <span class="post-link text-info pb-1">{{ title }} </span>
            </router-link>
            <p class="mb-1 post-content text-dark">  {{ shorten_text(content, 100) }} </p>
            <small class="text-muted">posted by {{ getUserName(author) }} on {{ display_date(created) }}</small>
        </b-card>

        <span v-if="Object.keys(posts).length === 0">There are no posts yet in this forum.</span>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import FormButtonAndModal from '../utils/FormButtonAndModal'
import ActionResponseComponent from '../actions/ActionResponseComponent'
import ResourceActionIcons from '../utils/ResourceActionIcons'


export default {

    props: ['item_id'],
    store,
    components: { FormButtonAndModal, ActionResponseComponent, ResourceActionIcons },
    mixins: [UtilityMixin],
    data: function() {
            return {
                forum: null,
                posts: null,
                delete_forum_response: null,
                base_export_url: ""
            }
        },
    created (){

        this.forum = this.getForumData(this.item_id)
        if (!this.forum) {
            this.getForum({ forum_pk: parseInt(this.item_id) }).then( response => {
                this.forum = this.getForumData(this.item_id)
            })
        }

        this.posts = this.getPostsDataForForum(this.item_id)
        if (!this.posts || this.posts.length == 0) {
            this.getPosts({ forum_pk: parseInt(this.item_id) }).then( response => {
                this.posts = this.getPostsDataForForum(this.item_id)
            })
        }

        var alt_target = "forum_" + this.item_id
        this.checkPermissions({ permissions:
                {edit_forum: {alt_target : alt_target},
                delete_forum: {alt_target : alt_target},
                add_post: {alt_target : alt_target}}
        })

        this.url_lookup('export_as_json').then(response => this.base_export_url = response)
    },
    watch: {
        forums: function(val) { this.forum = this.getForumData(this.item_id) }
    },
    computed: {
        ...Vuex.mapState({
            user_permissions: state => state.permissions.current_user_permissions,
            forums: state => state.forums.forums
        }),
        ...Vuex.mapGetters(['getForumData', 'getPostsDataForForum', 'getUserName', 'url_lookup']),
        is_governance_forum: function() {
            if (this.forum) { return this.forum.special == "Gov" } return undefined
        },
        json_export_url: function() {
            return this.base_export_url + "?item_id=" + this.item_id + "&item_model=forum"
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getForum', 'getPosts', 'deleteForum']),
        display_date(date) { return new Date(date).toUTCString() },
        delete_forum() {
            this.deleteForum({ pk: this.item_id })
            .then(response => {
                if (response.data.action_status == "implemented") { this.$router.push({name: 'home'}) }
                else { this.delete_forum_response = response }
            })
        }
    }

}

</script>

<style scoped>

 .text-info {
     border: none;
 }

 a {
     font-size: 120%;
     font-weight: bold;
 }

 a:hover {
     text-decoration: none;
 }


</style>