<template>

    <b-row>
        <b-col cols=3>
            <resource-sidebar-component :highlight_model="'forum'" :highlight_pk=forum_id>
            </resource-sidebar-component>
        </b-col>
        <b-col cols=9>

            <div class="bg-white p-3" v-if="post">

                <h3>{{ post.title }}</h3>
                <small class="text-muted">Posted in {{ forum_name }} on {{ display_date(post.created) }}
                    by {{ getUserName(post.author) }}</small>

                <!-- Nav links -->

                <div class="my-3">

                    <form-button-and-modal v-if="user_permissions.edit_post" :item_id=item_id
                        :item_model="'post'" :button_text="'edit post'" :id_add="'main'"></form-button-and-modal>

                    <action-response-component :response=delete_post_response></action-response-component>
                    <b-button v-if="user_permissions.delete_post" variant="outline-secondary" class="btn-sm mr-2"
                        id="delete_post_button" @click="delete_post(item_id)">delete post</b-button>

                    <router-link :to="{ name: 'action-history', params: {item_id: item_id, item_model: 'post', item_name: post.title }}">
                        <b-button variant="outline-secondary" id="post_history_button" class="btn-sm mr-2">post history</b-button>
                    </router-link>

                    <b-button variant="outline-secondary" id="post_permissions" v-b-modal.item_permissions_modal
                        class="btn-sm mr-2">post permissions</b-button>
                    <item-permissions-modal :item_id=item_id :item_model="'post'" :item_name=post.title>
                    </item-permissions-modal>

                </div>

                <!-- Content -->
                <p class="mb-3 text-secondary">  {{ post.content }}  </p>
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
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'
import FormButtonAndModal from '../utils/FormButtonAndModal'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    props: ['forum_id', 'item_id'],
    store,
    components: { CommentListComponent, ResourceSidebarComponent, ItemPermissionsModal, FormButtonAndModal, ActionResponseComponent },
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
        display_date(date) { return Date(date) },
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