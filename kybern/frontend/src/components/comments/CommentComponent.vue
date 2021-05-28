<template>

    <span>

        <b-card class="my-3 rounded">

            <b-card-text>{{ comment.text }}</b-card-text>

            <template v-slot:footer>

                <small class="text-muted">posted by <span class="user-link">{{ getUserName(comment.commenter_pk) }}</span>
                    on {{ display_date(comment.created_at) }}</small>

                <resource-action-icons class="float-right" v-on:delete="delete_comment(comment.pk)"
                    :item_id=comment.pk :item_name="comment_name(comment.text)" :item_model="'comment'"
                    :id_add="'comment' + comment.pk" :response=response></resource-action-icons>

            </template>

        </b-card>

    </span>

</template>


<script>


import Vuex from 'vuex'
import store from '../../store'
import ResourceActionIcons from '../utils/ResourceActionIcons'


export default {

    components: { ResourceActionIcons },
    props: ['item_id', 'item_model', 'comment'],
    store,
    data: function() {
        return {
            comment_text: '',
            error_message: '',
            response: null
        }
    },
    created () {
        this.comment_text = this.comment.text
    },
    computed: {
        ...Vuex.mapGetters(['getUserName']),
    },
    methods: {
        ...Vuex.mapActions(['deleteComment']),
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
            .then( response => { this.response = response })
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