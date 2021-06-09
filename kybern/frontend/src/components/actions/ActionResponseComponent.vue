<template>

<span>

    <div v-if="response_list">

        <b-alert v-for="resp in response_list" v-bind:key=resp.data.action_pk :show=get_show_alert(resp)
            :variant=get_variant(resp) @dismissed="dismiss_alert(resp)" dismissible>
            <span v-if="get_status(resp) == 'invalid'" >{{ process_message(resp) }}</span>
            <span v-else v-html=process_message(resp)></span>
        </b-alert>

    </div>

</span>

</template>

<script>

module.exports = {

    props: ['response'],
    data: function() {
        return {
            unique_identifier: null,
            suppress_alert: false,
            dismissed: {}
        }
    },
    computed: {
        ...Vuex.mapState({group_pk: state => state.group_pk}),
        response_list: function() {
            if (Array.isArray(this.response)) { return this.response }
            if (this.response) { return [this.response] }
            return []
        },
        showAlert: function() {
            if (this.response && !this.suppress_alert) { return true }
            return false
        },

    },
    methods: {
        get_status(response) {
            if (response && response.data.action_status) {
                return response.data.action_status
            } else {
                return null
            }
        },
        get_variant(response) {
            var status = this.get_status(response)
            if (["waiting", "propose-req", "propose-vol"].includes(status)) { return "warning"}  // yellow
            if (status == "invalid") { return "danger" }  // red
            if (status == "rejected") { return "info" }   // blue
            if (status == "implemented") { return "success" }  // green
            if (status) {
                console.log("WARNING: unexpected status: ", this.status )
            }
        },
        dismiss_alert(response) {
            this.dismissed[response.data.action_pk] = true
        },
        get_show_alert(response) {
            if (response) {
                if (this.dismissed[response.data.action_pk]) { return false}
                return true
            } else {
                return false
            }
        },
        process_message(response) {

            var status = this.get_status(response)
            var link = "/groups/" + this.group_pk + "/#/actions/detail/" + response.data.action_pk

            if (status == "implemented") {
                return "You have successfully " + response.data.action_description + ". " +
                    "If you want to provide context for this action, you can do so " +
                    "<a id='history_link' href='" + link + "'>here</a>."
            }
            if (status == "waiting") {
                return "<span>There is a <a id='condition_link' href='" + link + "'>condition</a> " +
                    "on your action which must be resolved before your action can be implemented.</span>"
            }
            if (status == "invalid") {
                return response.data.user_message
            }
            if (status == "rejected") {
                return "Your action has been rejected because you do not have permission to take it. " +
                    "You can discuss the issue further <a id='history_link' href='" + link + "'>here</a>."
            }
            if (status == "propose-vol") {
                return "Your action has been proposed. Visit <a id='history_link' href='" + link + "'>this link</a>" +
                    " to discuss further or to go ahead and take your action."
            }
            if (status == "propose-req") {
                return "Your action has been proposed. Visit <a id='history_link' href='" + link + "'>this link</a>" +
                    " for further discussion."
            }
            console.log("Warning, no response given for status ", status)
        }
    }

}

</script>

<style scoped>

    a, a:hover {
        font-weight: bold;
        text-decoration: none;
    }

</style>