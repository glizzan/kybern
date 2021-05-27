<template>

    <span>

        <!-- If the user has the permission, sees the button to take the default action, but also the
        drop down button to alternate action *and* the button to add a note to the selectec action.
        This enables them to just click the button. -->

        <!-- Otherwise, they just see the button with the options, and clicking it brings up the note modal. -->

        <!-- Button displayed inline -->
        <b-dropdown split text=":show_text" class="m-2">
            <b-dropdown-item href="#">{{ alt_text }}</b-dropdown-item>
        </b-dropdown>



        <b-modal :id="verb + '_action_modal'" title="Take Action">

            <b-form-group id="comment_text_group">
                <b-form-textarea id="text" name="text" v-model="comment_text" placeholder="Write your comment here">
                </b-form-textarea>
            </b-form-group>

            <action-response-component :response=edit_comment_response></action-response-component>

            <b-button variant="outline-secondary" class="btn-sm" id="add_comment_default_button"  @click="add_comment">submit</b-button>

        </b-modal>


    </span>

</template>

<script>

// What about inline editing of list? That's not showing the button, so...?
// Have a version of the modal where you've got to decide between take & propose, that this incorporates.
//
//

module.exports = {

    props: ['verb', 'has_permission', 'has_condition', 'button-variant'],
    data: function() {
        return {
            unique_identifier: null,
            showAlert: false
        }
    },
    computed: {
        ...Vuex.mapState({group_pk: state => state.group_pk}),
        show_text: function() {
            if (this.has_permission && !this.has_condition) { return this.verb } else { return "propose " + this.verb }
        },
        alt_text: function() {
            if (this.has_permission && !this.has_condition) { return "propose " + this.verb } else { return this.verb }
        }
    }

}

</script>