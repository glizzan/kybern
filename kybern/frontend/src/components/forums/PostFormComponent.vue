<template>

    <b-modal id="post_modal" :title=title_string size="md" :visible=true hide-footer @hide="$router.go(-1)">

        <b-form-group id="title" label="Post title:" label-for="post_title">
            <b-form-input id="post_title" name="post_title" v-model="title" required placeholder="Add a title">
            </b-form-input>
        </b-form-group>

        <b-form-group id="content" label="Post content:" label-for="post_content">
            <b-form-textarea id="post_content" name="post_content" v-model="content" placeholder="Add some content">
            </b-form-textarea>
        </b-form-group>

        <b-button v-if=!post_id variant="outline-secondary" class="btn-sm" id="add_post_save_button"
            @click="add_post">submit</b-button>
        <b-button v-if=post_id variant="outline-secondary" class="btn-sm"  id="edit_post_save_button"
            @click="edit_post">submit</b-button>

        <error-component :message=error_message></error-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['forum_id', 'post_id'],
    store,
    components: { ErrorComponent },
    data: function() {
        return {
            title: null,
            content: null,
            error_message: null
        }
    },
    created () {
        if (this.post_id) {
            post = this.getPostData(this.post_id)
            this.title = post.title
            this.content = post.content
        }
    },
    computed: {
        ...Vuex.mapGetters(['getPostData']),
        title_string: function() {
            if (this.post_id) {  return "Edit post '" + this.title + "'" }
            else { return "Add a new post" }
        }
    },
    methods: {
        ...Vuex.mapActions(['addPost', 'editPost']),
        add_post() {
            this.addPost({ forum_pk: this.forum_id, title: this.title, content: this.content })
                .then(response => { this.$router.go(-1) })


                .catch(error => { this.error_message = error })
        },
        edit_post() {
            this.editPost({ pk: this.post_id, title: this.title, content: this.content })
                .then(response => { this.$router.go(-1) })
                .catch(error => {  this.error_message = error })
        }
    }

}

</script>