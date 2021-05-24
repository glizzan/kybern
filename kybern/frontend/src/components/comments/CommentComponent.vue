<template>

    <span>

        <b-card class="my-3 rounded">

            <b-card-text>{{ comment.text }}</b-card-text>

            <template v-slot:footer>

                <action-response-component :response=delete_comment_response></action-response-component>

                <small class="text-muted">posted by <span class="user-link">{{ getUserName(comment.commenter_pk) }}</span>
                    on {{ display_date(comment.created_at) }}</small>

                <resource-action-icons class="float-right" v-on:delete="delete_comment(comment.pk)"
                    :item_id=comment.pk :item_name="comment_name(comment.text)" :item_model="'comment'"
                    :id_add="'comment' + comment.pk" :edit_permission="user_permissions.edit_comment"
                    :delete_permission="user_permissions.delete_comment"></resource-action-icons>

            </template>

        </b-card>

    </span>

</template>


<script>


import Vuex from 'vuex'
import store from '../../store'
import ActionResponseComponent from '../actions/ActionResponseComponent'
import ResourceActionIcons from '../utils/ResourceActionIcons'


export default {

    components: { ActionResponseComponent, ResourceActionIcons },
    props: ['item_id', 'item_model', 'comment'],
    store,
    data: function() {
        return {
            comment_text: '',
            error_message: '',
            edit_comment_response: null,
            delete_comment_response: null
        }
    },
    created () {
        var alt_target = "comment_" + this.comment.pk
        this.checkPermissions({permissions: {"edit_comment": {alt_target: alt_target},
            "delete_comment": {alt_target: alt_target}}})
            .catch(error => {  this.error_message = error; console.log(error) })
        this.comment_text = this.comment.text
    },
    computed: {
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        ...Vuex.mapGetters(['getUserName']),
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'deleteComment']),
        display_date(date) { return  new Date(date).toUTCString() },
        comment_name(text) {
            if (text.length > 50) {
                return "Comment: " + text.substr(0, 50) + "...'"
            } else {
                return "Comment: '" + text + "'"
            }
        },
        delete_comment(pk) {
            this.deleteComment({ item_id: this.item_id, item_model: this.item_model, comment_pk: pk })
            .then( response => {
                if (!response.data.action_status == "implemented") {
                    this.delete_comment_response = response
                }})
        }
    }
}

</script>

<style scoped>
    .card-text {
        color: #404040
    }

    .user-link {
        color: #17a2b8;
        font-weight: bold;
    }

</style>