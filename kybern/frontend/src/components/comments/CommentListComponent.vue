<template>

    <span>

        <form-button-and-modal :item_model="'comment'" :button_text="'+ add comment'" :alt_target="alt_target"
            :supplied_params="{'item_id':item_id, 'item_model':item_model}"></form-button-and-modal>

        <b-button v-if="item_comments.length > 0 && show_comments == false" class="btn-sm show-comments mr-2"
            v-on:click="show_comments = true">
            Show comments</b-button>
        <b-button v-if="item_comments.length > 0 && show_comments == true" class="btn-sm hide-comments mr-2"
            v-on:click="show_comments = false">
            Hide comments</b-button>

        <span v-if="show_comments">
            <comment-component v-for="comment in item_comments" :comment=comment :item_id=item_id :item_model=item_model
                v-bind:key=comment.pk></comment-component>
        </span>

    </span>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import CommentComponent from '../comments/CommentComponent'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: { FormButtonAndModal, CommentComponent },
    props: ['item_id', 'item_model'],
    store,
    data: function() {
        return {
            show_comments: true,
            comment_text: '',
            edit_comment_response: null
        }
    },
    created () {
        this.getComments({ item_id: this.item_id, item_model: this.item_model })
        .catch(error => { console.log("Error getting comment data")  })
    },
    computed: {
        ...Vuex.mapGetters(['getCommentsForItem', 'getUserName']),
        item_comments: function() {
            if (this.item_id && this.item_model) {
                return this.getCommentsForItem(this.item_id + "_" + this.item_model)
            } else {
                return []
            }
        },
        alt_target: function() {
            return this.item_model + "_" + this.item_id
        }
    },
    methods: {
        ...Vuex.mapActions(['getComments']),
        display_date(date) { return Date(date) },
        comment_name(text) {
            if (text.length > 50) {
                return "Comment: " + text.substr(0, 50) + "...'"
            } else {
                return "Comment: '" + text + "'"
            }
        }
    }

}

</script>