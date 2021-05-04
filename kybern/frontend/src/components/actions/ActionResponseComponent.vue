<template>

    <div v-if="response">

        <b-alert :show=showAlert :variant=variant dismissible @dismissed="showAlert = false">
            <span v-if="status == 'waiting' || status == 'implemented'" v-html=processed_message></span>
            <span v-else>{{ processed_message }}</span>
        </b-alert>

    </div>

</template>

<script>

module.exports = {

    props: ['response'],
    data: function() {
        return {
            unique_identifier: null,
            showAlert: false
        }
    },
    watch: {
        response: function(val) { if (val) { this.showAlert = true } }
    },
    computed: {
        ...Vuex.mapState({group_pk: state => state.group_pk}),
        status: function() {
            if (this.response && this.response.data.action_status) {
                return this.response.data.action_status
            } else {
                return null
            }
        },
        variant: function() {
            if (this.status == "waiting") { return "warning"}  // yellow
            if (this.status == "invalid") { return "danger" }  // red
            if (this.status == "rejected") { return "outline-danger" }   // blue
            if (this.status == "implemented") { return "success" }  // green
            if (this.status) {
                console.log("WARNING: unexpected status: ", this.status )
            }
        },
        processed_message: function() {
            if (this.status) {

                var link = "/groups/" + this.group_pk + "/#/actions/detail/" + this.response.data.action_pk
                if (this.status == "implemented") {
                    return "You have successfully " + this.response.data.action_description + ". " +
                        "If you want to provide context for this action, you can do so " +
                        "<a id='history_link' href='" + link + "'>here</a>."
                }
                if (this.status == "waiting") {
                    return "<span>There is a <a id='condition_link' href='" + link + "'>condition</a> " +
                        "on your action which must be resolved before your action can be implemented.</span>"
                }
                if (this.status == "invalid") {
                    return this.response.data.user_message
                }
                if (this.status == "rejected") {
                    if (this.response.data.user_message) {
                        return "This action cannot be taken because: " + this.response.data.user_message
                    } else {
                        return "You do not have permission to take this action."
                    }
                }
            }
        }
    }

}

</script>