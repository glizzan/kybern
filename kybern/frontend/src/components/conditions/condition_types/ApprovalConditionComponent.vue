<template>
    <span>

        <div v-if="condition_status == 'waiting'" class="my-2">
            <b>Please approve or reject this action.</b>
        </div>

        <div v-if="condition_status == 'approved' || condition_status == 'rejected'" class="my-2">
            {{ action_details.actor }}'s action has been {{ condition_status }}.
        </div>

        <span v-if="condition_status == 'waiting' || approve_response">
            <take-action-component v-if="hide != 'approve'" :response=approve_response :verb="'approve'"
                :inline="true" class="mr-3" :alt_target=alt_target
                v-on:take-action="update_conditional('approve', $event)"
                v-on:open-extra="hide = 'reject'" v-on:close-extra="hide = null">
            </take-action-component>
        </span>

        <span v-if="condition_status == 'waiting' || reject_response">
            <take-action-component v-if="hide != 'reject'" :response=reject_response :verb="'reject'"
                :inline="true" :alt_target=alt_target v-on:take-action="update_conditional('reject', $event)"
                v-on:open-extra="hide = 'approve'" v-on:close-extra="hide = null">
            </take-action-component>
        </span>

    </span>
</template>


<script>

import Vuex from 'vuex'
import store from '../../../store'
import axios from '../../../store/axios_instance'
import TakeActionComponent from '../../actions/TakeActionComponent'


export default {

    components: { TakeActionComponent },
    props: ['condition_type', 'condition_pk', 'action_details'],
    store,
    data: function() {
        return {
            error_message: null,
            permission_details: null,
            condition_details: null,
            approve_response: null,
            reject_response: null,
            hide: null
        }
    },
    created () {
        this.get_conditional_data()
    },
    computed: {
        ...Vuex.mapGetters(['url_lookup']),
        alt_target: function() { return "approvalcondition_" + this.condition_pk },
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
        async update_conditional(action_taken, extra_data) {

            // For now, we don't store individual conditional data in vuex in part to make this more
            // extensible, although presumably there *is* a way to make vuex handle this extensibly.

            var url = await this.url_lookup('take_action')
            var params = { action_name: action_taken, extra_data: extra_data,
                alt_target: "approvalcondition_" + this.condition_pk }
            axios.post(url, params).then(response => {

                var new_action_pk = response.data.action_pk
                var response_str = action_taken + "_response"
                this[response_str] = response

                // update condition data
                this.get_conditional_data().then(response => {
                        // refresh action
                        this.addOrUpdateAction({ action_pk: this.action_details["action_pk"] })
                        // also call vuex to record this as an action (need to do this for all actions)
                        this.addOrUpdateAction({ action_pk: new_action_pk })
                })

            })
        }
    }
}

</script>
