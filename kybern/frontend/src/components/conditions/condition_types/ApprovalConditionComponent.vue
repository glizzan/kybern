<template>
    <span>

        <!-- If action is waiting -->
        <span v-if="condition_status == 'waiting' && !user_has_taken_action" class="my-5">

            <!-- If user can approve -->
            <span v-if="can_approve">
                <!-- BUG: we're letting people reject here as well without handling it functionally -->
                <p class="mb-3"><b>Please approve or reject this action.</b></p>
                <b-form-radio-group id="btn-radios-1" v-model="button_selected" :options="button_options"
                    buttons name="radios-btn-default" button-variant="outline-primary">
                </b-form-radio-group>
                <b-button @click="update_conditional" id="save_approve_choice">Save</b-button>
            </span>

            <span v-else>
                <p class="mb-3"><b>You do not have permission to approve or reject this action.</b></p>
            </span>

        </span>

        <!-- If user has just approved or rejected condition.-->
        <span v-if="user_has_taken_action">
            <span v-if="condition_status == 'approved' || condition_status == 'rejected'" class="my-5">
                You have {{ condition_status }} {{ action_details.actor }}'s action.
                Nothing further is needed from you.
            </span>
        </span>

        <!-- If condition was already closed before the user opened this modal, so they haven't taken action. -->
        <span v-if="!user_has_taken_action">
            <span v-if="condition_status == 'approved' || condition_status == 'rejected'" class="my-5">
                {{ action_details.actor }}'s action has been {{ condition_status }}.
            </span>
        </span>

        <span v-if="error_message" class="text-danger mt-3">{{ error_message }}</span>

</span>
</template>


<script>

import Vuex from 'vuex'
import store from '../../../store'
import axios from '../../../store/axios_instance'


export default {

    props: ['condition_type', 'condition_pk', 'action_details'],
    store,
    data: function() {
        return {
            user_has_taken_action: false,
            button_options: ["approve", "reject"],
            button_selected: null,
            error_message: null,
            permission_details: null,
            condition_details: null
        }
    },
    created () {
        this.get_conditional_data()
    },
    computed: {
        ...Vuex.mapGetters(['url_lookup']),
        can_approve: function() {

            // Every condition has permissions set on it (generated by the system from the condition template)
            // To see whether a user can approve an action, we need to check the permissions

            if (this.permission_details["concord.conditionals.state_changes.ApproveStateChange"][0] == true) {

                // Is self-approval allowed?
                var self_approval_allowed = null
                this.condition_details.fields.forEach((field) => {
                    if (field.field_name == "self_approval_allowed") {
                        self_approval_allowed = field.field_value }
                })
                if (self_approval_allowed == true) { return true }

                // Or, if it's not allowed, is the action-taker not the approver?

                if (store.state.user_name != this.action_details.actor ) { return true }
            }
            return false
        },
        condition_status: function() {
            if (this.condition_details) {
                return this.condition_details.status
            } else {
                return null
            }
        }
    },
    methods: {
        ...Vuex.mapActions(['addOrUpdateAction']),
        async get_conditional_data() {
            var url = await this.url_lookup('get_conditional_data')
            var params ={ condition_pk: this.condition_pk, condition_type: this.condition_type }
            return axios.post(url, params).then(response => {
                this.permission_details = response.data.permission_details
                this.condition_details = response.data.condition_details
            }).catch(error => {  console.log(error)  })
        },
        async update_conditional() {

            // For now, we don't store individual conditional data in vuex in part to make this more
            // extensible, although presumably there *is* a way to make vuex handle this extensibly,
            // but that's a bit above my paygrade for now.

            var url = await this.url_lookup('update_approval_condition')
            var params ={ condition_pk: this.condition_pk, action_to_take: this.button_selected }
            axios.post(url, params).then(response => {

                var new_action_pk = response.data.action_pk

                // update condition data
                this.user_has_taken_action = true
                this.get_conditional_data().then(response => {

                    if (this.condition_status == "waiting") {
                        // In a limited set of circumstances, there may be a condition on a conditional action
                        // (for instance, if someone is using a governing or owning authority to act)
                        this.error_message = "Before your decision to " + this.button_selected + " can be implemented, a condition must be satisfied."
                    } else {
                        // refresh action
                        this.addOrUpdateAction({ action_pk: this.action_details["action_pk"] })
                        // also call vuex to record this as an action (need to do this for all actions)
                        this.addOrUpdateAction({ action_pk: new_action_pk })
                    }

                }).catch(error => {  console.log("Error refreshing condition data:", error); this.error_message = error })

            }).catch(error => {  console.log("Error updating condition: ", error); this.error_message = error })

        }
    }
}

</script>