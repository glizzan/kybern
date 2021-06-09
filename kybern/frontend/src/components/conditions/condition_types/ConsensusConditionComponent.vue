<template>

    <span>

        <!-- Information about the discussion. -->

        <b-card bg-variant="white" class="mb-3">
            <div class="mb-2 font-weight-bold">Discussion Status</div>

            <span v-if="is_resolved">The condition was resolved with resolution {{ condition_resolution_status}}.
                <span v-if="response_selected">Your response was <b>{{response_selected}}</b>.</span>
            </span>
            <span v-else>
                <span v-if="can_be_resolved">The minimum duration of {{ minimum_duration }} has passed. If the discussion
                    was resolved right now, the result would be: {{ current_result }}.
                    <b-button v-if="can_resolve" class="btn-sm d-block mt-2" variant="outline-info" id="resolve_button"
                        @click="resolve_condition()">Resolve this discussion?</b-button>
                </span>
                <span v-else>The discussion cannot be resolved until the minimum duration of {{ minimum_duration}} has passed.
                    This will happen in {{ time_remaining }}.
                </span>
            </span>
        </b-card>

        <b-container class="bg-white light-border my-2 py-2 px-4" id="consensus_responses">
            <b-row><b-col class="text-center my-2 font-weight-bold">Current Responses</b-col></b-row>
            <b-row class="font-weight-bold text-secondary mb-3">
                <b-col>Support</b-col><b-col cols="3">Support With Reservations</b-col><b-col>Stand Aside</b-col><b-col>Block</b-col>
                <b-col>No Response</b-col>
            </b-row>
            <b-row>
                <b-col id="support_names">{{get_names(response_data.support)}}</b-col>
                <b-col cols="3" id="reservatiions_names">{{get_names(response_data.support_with_reservations)}}</b-col>
                <b-col id="stand_aside_names">{{get_names(response_data.stand_aside)}}</b-col>
                <b-col id="block_names">{{get_names(response_data.block)}}</b-col>
                <b-col id="no_response_names">{{get_names(response_data.no_response)}}</b-col>
            </b-row>
        </b-container>

        <!-- Interface for changes -->

        <b-card bg-variant="white" class="mb-3">
            <div v-if="!is_resolved" class="my-3">
                <span v-if="can_respond">
                    <b-form-group>
                        <b-form-radio-group id="user_response_radio_buttons" v-model="response_selected" :options="response_options"
                            button-variant="outline-info" buttons name="user_response_radio_buttons"></b-form-radio-group>
                    </b-form-group>
                    <b-button class="btn-sm" id="submit_response" @click="submit_response()">Submit Your Response</b-button>
                </span>
                <span v-else>You are not a participant in this consensus decision.</span>
            </div>

            <span v-if="error_message" class="text-danger">{{ error_message }}</span>

        </b-card>


    </span>
</template>


<script>

import Vue from 'vue'
import Vuex from 'vuex'
import store from '../../../store'
import axios from '../../../store/axios_instance'


export default {

    props: ['condition_type', 'condition_pk', 'action_details'],
    store,
    data: function() {
        return {
            error_message: null,
            permission_details: null,
            condition_details: null,
            // select data
            response_selected: null,
            // fields that will be automatically filled by getConditionData
            minimum_duration: null,
            time_remaining: null,
            can_be_resolved: null,
            responses: null,
            response_options: null,
            current_result: null
        }
    },
    computed: {
        ...Vuex.mapGetters(['getUserName', 'url_lookup']),
        can_respond: function() {
            if (this.permission_details) {
                return this.permission_details["concord.conditionals.state_changes.RespondConsensusStateChange"][0]
            }
            return undefined
        },
        can_resolve: function() {
            if (this.permission_details) {
                return this.permission_details["concord.conditionals.state_changes.ResolveConsensusStateChange"][0]
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
        },
        response_data: function() {
            var response_dict = {}
            if (this.response_options) {
                this.response_options.forEach(response_option => response_dict[response_option.replace(/\s/g, "_")] = [])
                for (let user in this.responses) {
                    response_dict[this.responses[user].replace(/\s/g, "_")].push(user)
                }
            }
            return response_dict
        },
        condition_resolution_status: function() {
            if (this.condition_details) { return this.condition_details.status }
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
                this.permission_details = response.data.permission_details
                this.condition_details = response.data.condition_details
                for (let field in this.condition_details.fields) {
                    var name = this.condition_details.fields[field]["field_name"]
                    var value = this.condition_details.fields[field]["field_value"]
                    Vue.set(this, name, value)
                }
                this.set_user_response()
            }).catch(error => {  console.log(error)  })
        },
        get_names(pk_list) {
            if (pk_list) {
                var name_list = []
                pk_list.forEach(pk => name_list.push(this.getUserName(parseInt(pk))))
                return name_list.join(", ")
            } else { return "" }

        },
        set_user_response() {
            for (let user in this.responses) {
                if (user == store.state.user_pk) { this.response_selected = this.responses[user] }
            }
        },
        update_action(new_action_pk) {
            // update action this was a condition on
            this.addOrUpdateAction({ action_pk: this.action_details["action_pk"] })
            // also call vuex to record this as an action (need to do this for all actions)
            this.addOrUpdateAction({ action_pk: new_action_pk })
        },
        async submit_response() {
            if (!this.response_selected) { this.error_message = "Please select a response" }
            if (this.response_selected == this.user_response) { this.error_message = "Your response has not changed"; return }
            var url = await this.url_lookup('update_consensus_condition')
            var params ={ condition_pk: this.condition_pk, action_to_take: "respond", response: this.response_selected }
            axios.post(url, params).then(response => {
                if (["implemented", "waiting"].indexOf(response.data.action_status) > -1) {
                    this.update_action(response.data.action_pk)
                    this.get_conditional_data().catch(error => { this.error_message = error })
                } else {
                    this.error_message = response.data.user_message
                }
            }).catch(error => {  console.log("Error updating condition: ", error); this.error_message = error })
        },
        async resolve_condition() {
            var url = await this.url_lookup('update_consensus_condition')
            var params ={ condition_pk: this.condition_pk, action_to_take: "resolve" }
            axios.post(url, params).then(response => {
                if (["implemented", "waiting"].indexOf(response.data.action_status) > -1) {
                    this.update_action(response.data.action_pk)
                    this.get_conditional_data().catch(error => { this.error_message = error })
                } else {
                    this.error_message = response.data.user_message
                }
            }).catch(error => {  console.log("Error updating condition: ", error); this.error_message = error })
        }
    }
}

</script>

<style scoped>

    .light-border {
        border: 1px solid rgba(0,0,0,.125);
    }

</style>