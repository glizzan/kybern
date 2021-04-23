<template>

    <span>

        <b-card class="my-3">

            <b-card-text>{{ comment.text }}</b-card-text>

            <template v-slot:footer>

                <form-button-and-modal v-if="user_permissions.edit_comment" :id_add="'comment' + comment.pk"
                    :item_id=comment.pk :item_model="'comment'" :button_text="'edit'"></form-button-and-modal>

                <b-button v-if="user_permissions.delete_comment" variant="outline-secondary" class="btn-sm mr-2"
                    @click="delete_comment(comment.pk)">delete</b-button>
                <action-response-component :response=delete_comment_response></action-response-component>

                <router-link :to="{ name: 'action-history', params: {item_id: comment.pk, item_model: 'comment',
                        item_name: comment_name(comment.text) }}">
                    <b-button variant="outline-secondary" class="btn-sm mr-2">comment history</b-button>
                </router-link>

                <b-button variant="outline-secondary" id="comment_permissions" v-b-modal.item_permissions_modal
                    class="btn-sm mr-2">comment permissions</b-button>
                <item-permissions-modal :item_id=comment.pk :item_model="'comment'"
                    :item_name="comment_name(comment.text)"></item-permissions-modal>

                <br />

                <small class="text-muted">Posted {{ display_date(comment.created_at) }}
                    by {{ getUserName(comment.commentor_pk) }}</small>

            </template>

        </b-card>

    </span>

</template>


<script>


import Vuex from 'vuex'
import store from '../../store'
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'
import ActionResponseComponent from '../actions/ActionResponseComponent'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: {ItemPermissionsModal, ActionResponseComponent, FormButtonAndModal },
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
        display_date(date) { return Date(date) },
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