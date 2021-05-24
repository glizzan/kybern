<template>

    <b-row>
        <b-col cols=3>
            <resource-sidebar-component :highlight_model="'forum'" :highlight_pk=forum_id>
            </resource-sidebar-component>
        </b-col>
        <b-col cols=9>

            <div class="bg-white p-3 rounded" v-if="post">

                <div class="title-and-actions mb-4">

                    <span class="h3 font-weight-bold">{{ post.title }}</span>

                    <resource-action-icons class="float-right" v-on:delete="delete_post" :item_id=item_id
                        :item_model="'post'" :item_name=post.title :edit_permission="user_permissions.edit_post"
                        :delete_permission="user_permissions.delete_post"></resource-action-icons>

                    <div id="author" class="mt-2"> by <span class="user-link">{{ getUserName(post.author) }}</span></div>
                    <div id="post-info" class="mt-2 small">
                        posted in {{ forum_name }} on {{ display_date(post.created) }}</div>

                </div>

                <action-response-component :response=delete_post_response></action-response-component>

                <!-- Content -->
                <p class="mb-4 post-text">  {{ post.content }}  </p>
                <CommentListComponent :item_id=item_id :item_model="'post'" class="mt-3"></CommentListComponent>

            </div>

        </b-col>
    </b-row>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import CommentListComponent from '../comments/CommentListComponent'
import ResourceSidebarComponent from '../groups/ResourceSidebarComponent'
import ActionResponseComponent from '../actions/ActionResponseComponent'
import ResourceActionIcons from '../utils/ResourceActionIcons'


export default {

    props: ['forum_id', 'item_id'],
    store,
    components: { CommentListComponent, ResourceSidebarComponent, ActionResponseComponent, ResourceActionIcons },
    mixins: [UtilityMixin],
    data: function() {
            return {
                post: null,
                forum: null,
                delete_post_response: null
            }
        },
    created (){
        this.getGovernanceData().then(response => {
            this.post = this.getPostData(this.item_id)
            if (!this.post){
                this.getPost({ post_pk: this.item_id}).then(response => {
                this.post = this.getPostData(this.item_id) })
            }
        })
        this.forum = this.getForumData(this.forum_id)
        if (!this.forum) {
            this.getForum({forum_pk: parseInt(this.forum_id)}).then(response => {
            this.forum = this.getForumData(this.forum_id)})
        }
        // Check permissions
        var alt_target = "post_" + this.item_id
        this.checkPermissions({ permissions: {edit_post: {alt_target:alt_target},
            delete_post: {alt_target:alt_target}}
        }).catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({user_permissions: state => state.permissions.current_user_permissions}),
        ...Vuex.mapGetters(['getUserName', 'getPostData', 'getForumData']),
        forum_name: function() { if (this.forum) { return this.forum.name } else { return "" } }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'deletePost', 'getPost', 'getForum', 'getGovernanceData']),
        display_date(date) {
            return new Date(date).toUTCString()
        },
        delete_post(pk) {
            this.deletePost({ pk : pk, forum_pk: this.forum_id })
            .then(response => {
                if (response.data.action_status == "implemented") {
                    this.$router.push({name: 'forum-detail', params: {forum_id: this.forum_id}})
                }
                else { this.delete_post_response = response }
            })
        }
    }

}

</script>

<style scoped>

    .post-text {
        font-size: 120%;
    }

    .user-link {
        color: #17a2b8;
        font-weight: bold;
    }

</style>