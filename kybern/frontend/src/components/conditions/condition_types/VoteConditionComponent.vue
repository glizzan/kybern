<template>

    <span>

        <!-- Information about the vote. -->
        <span v-if="is_resolved">
            This vote ended on {{ voting_deadline_display }}.
            The results were {{ vote_results }}, which means the action was {{ condition_details.status }}.
            It required a {{ majority_or_plurality }} vote and abstentions were
            <span v-if="!allow_abstain">not</span> allowed.
        </span>

        <span v-else>
            This vote will end on {{ voting_deadline_display }}.
            The results so far are {{ vote_results }}.
            It requires a {{ majority_or_plurality }} vote and abstentions are
            <span v-if="!allow_abstain">not</span> allowed.
        </span>


        <!-- If action is waiting, and user has not taken action -->
        <span v-if="!is_resolved && !user_has_taken_action" class="my-5">

            <!-- If user can vote -->
            <span v-if="can_vote && not_yet_voted">

                    <p class="mb-3"><b>Please cast your vote</b></p>
                    <b-form-radio-group id="btn-radios-1" v-model="button_selected" :options="button_options"
                        buttons name="radios-btn-default" button-variant="outline-primary">
                    </b-form-radio-group>
                    <b-button @click="update_condition" id="save_vote_choice">Submit</b-button>

            </span>

            <span v-else-if="can_vote && !not_yet_voted">
                <p class="mb-3"><b>You have already voted.</b></p>
            </span>

            <span v-else>
                <p class="mb-3"><b>You are not eligible to vote.</b></p>
            </span>

        </span>

        <!-- If user has just voted.-->
        <span v-if="user_has_taken_action">
            Thank you for voting!  No further action from you is needed.
        </span>

        <span v-if="error_message" class="text-danger">{{ error_message }}</span>

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
            button_selected: null,
            error_message: null,
            permission_details: null,
            condition_details: null,
            allow_abstain: null,
            require_majority: null,
            voting_deadline: null
        }
    },
    computed: {
        ...Vuex.mapGetters(['url_lookup']),
        voting_deadline_display: function() {
            if (this.voting_deadline) {
                return Date(this.voting_deadline)
            }
            return undefined
        },
        button_options: function() {
            if (this.allow_abstain) {
                if (this.allow_abstain == true) { return ["yea", "nay", "abstain"] }
                else { return ["yea", "nay"] }
            } else { return [] }
        },
        majority_or_plurality: function() {
            if (this.require_majority == true ) {
                return "majority (as opposed to plurality)"
            } else if ( this.require_majority == false ) {
                return "plurality (as opposed to majority)"
            }
            return undefined
        },
        vote_results: function() {
            if (this.condition_details) {
                var vote_results = this.current_yeas + " yeas and " + this.current_nays + " nays"
                if (this.allow_abstain) { vote_results += " with " + this.current_abstains  + "  abstentions" }
                return vote_results
            }
            return undefined
        },
        can_vote: function() {
            if (this.permission_details) {
                return this.permission_details["concord.conditionals.state_changes.AddVoteStateChange"][0]
            }
            return undefined
        },
        not_yet_voted: function() {
            if (this.permission_details) {
                return this.permission_details["user_condition_status"][0]
            }
            return undefined
        },
        is_resolved: function() {
            if (this.condition_details) {
                if (["approved", "rejected", "implemented"].includes(this.condition_details.status)) {
                    return true
                } else { return false }
            }
            return undefined
        }
    },
    created () {
        this.get_conditional_data()
    },
    methods: {
        ...Vuex.mapActions(['addOrUpdateAction']),
        async get_conditional_data() {
            var url = await this.url_lookup('get_conditional_data')
            var params ={ condition_pk: this.condition_pk, condition_type: this.condition_type }
            return axios.post(url, params).then(response => {
                this.condition_details = response.data.condition_details
                this.permission_details = response.data.permission_details
                for (let field in this.condition_details.fields) {
                    var name = this.condition_details.fields[field]["field_name"]
                    var value = this.condition_details.fields[field]["field_value"]
                    this[name] = value
                }
            }).catch(error => {  console.log("Error calling get_conditional_data in vote condition: ", error)  })
        },
        async update_condition() {

            // For now, we don't store individual conditional data in vuex in part to make this more
            // extensible, although presumably there *is* a way to make vuex handle this extensibly,
            // but that's a bit above my paygrade for now.

            var url = await this.url_lookup('update_vote_condition')
            var params ={ condition_pk: this.condition_pk, action_to_take: this.button_selected }
            axios.post(url, params).then(response => {

                var new_action_pk = response.data.action_pk

                // update condition data
                this.user_has_taken_action = true
                this.get_conditional_data().then(response => {

                    if (this.condition_details.status == "waiting") {

                        // In a vote, *usually* the condition is still waiting after a person's taken action,
                        // because the condition is only resolved after the voting period ends.  So we'll need
                        // a separate way to let people know if their vote isn't cast due to a condition.

                    } else {

                        // update action this was a condition on
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

