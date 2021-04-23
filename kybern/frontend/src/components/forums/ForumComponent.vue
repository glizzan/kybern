<template>

    <div v-if="forum" class="bg-white p-3">

        <h3 class="mt-3">{{ forum.name }}</h3>
        <p>{{ forum.description }}</p>

        <form-button-and-modal v-if="user_permissions.edit_forum" :id_add="'main'" :item_id=item_id
            :item_model="'forum'" :button_text="'edit metadata'"></form-button-and-modal>

        <action-response-component :response=delete_forum_response></action-response-component>
        <b-button v-if="user_permissions.delete_forum && !is_governance_forum" variant="outline-secondary"
            class="btn-sm mr-2" id="delete_forum_button" @click="delete_forum">delete forum</b-button>

        <router-link :to="{ name: 'action-history', params: {item_id: item_id, item_model: 'forum', item_name: forum.name }}">
            <b-button variant="outline-secondary" class="btn-sm mr-2" id="forum_history_button">forum history</b-button>
        </router-link>

        <b-button variant="outline-secondary" id="forum_permissions_button" v-b-modal.item_permissions_modal
            class="btn-sm mr-2">forum permissions</b-button>
        <item-permissions-modal :item_id=item_id :item_model="'forum'" :item_name=forum.name>
        </item-permissions-modal>

        <b-button :href=json_export_url variant="outline-secondary" class="btn-sm" download>
            export as json</b-button>

        <hr >

        <form-button-and-modal v-if="user_permissions.add_post" :item_model="'post'"
            :button_text="'+ add post'" :supplied_params="{'forum_id':item_id}"></form-button-and-modal>

        <b-card v-for="{ pk, title, content, author, created } in posts" v-bind:key=pk
                                            class="bg-light text-info border-secondary mt-3">
            <router-link :to="{ name: 'post-detail', params: { forum_id: item_id, item_id: pk } }">
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
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'
import FormButtonAndModal from '../utils/FormButtonAndModal'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    props: ['item_id'],
    store,
    components: { ItemPermissionsModal, FormButtonAndModal, ActionResponseComponent },
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
        display_date(date) { return Date(date) },
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