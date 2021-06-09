<template>

    <span class="d-flex my-3">

        <!-- left aligned nav -->
        <span class="flex-grow-1">

            <span class="font-weight-bold"><b-icon-people-fill class="mr-2"></b-icon-people-fill>{{group_name}}</span>

            <router-link id="resources_button" :to="{ name: 'home'}" :class="is_active('resources')">
                <b-icon-grid-fill v-if="is_active('resources') == 'tab-active'" class="ml-3 mr-1"></b-icon-grid-fill>
                <b-icon-grid v-else class="ml-3 mr-1"></b-icon-grid>
                Resources
            </router-link>

            <router-link id="group_history_button" :to="{ name: 'action-history', params: { item_id: group_pk,
            item_model: 'group', item_name: group_name }}" :class="is_active('history')">
                <b-icon-clock-fill v-if="is_active('history') == 'tab-active'" class="ml-3 mr-1">
                </b-icon-clock-fill>
                <b-icon-clock-history v-else class="ml-3 mr-1"></b-icon-clock-history>
                History
            </router-link>

            <router-link id="governance_button" :to="{ name: 'governance'}" :class="is_active('governance')">
                <b-icon-person-check-fill v-if="is_active('governance') == 'tab-active'" class="ml-3 mr-1">
                </b-icon-person-check-fill>
                <b-icon-person-check v-else class="ml-3 mr-1"></b-icon-person-check>
                Group Roles
            </router-link>

            <router-link id="group_permissions_button" :class="is_active('permissions')"
                :to="{ name: 'group-permissions', params: { group_pk: group_pk}}">
                <b-icon-shield-lock-fill v-if="is_active('permissions') == 'tab-active'" class="ml-3 mr-1">
                </b-icon-shield-lock-fill>
                <b-icon-shield-lock v-else class="ml-3 mr-1"></b-icon-shield-lock>
                Permissions
            </router-link>

        </span>


        <!-- right aligned nav -->
        <span>

            <take-action-component v-if="!user_in_group" v-on:take-action="join_group" :response=response
                :verb="'join group'" :action_name="'add_members_to_community'" :check_permissions_params=check_params
                v-on:close-modal="modal_closed">
                <b-button id="join_group_button" class="py-0" variant="link">join</b-button>
            </take-action-component>

            <take-action-component v-else v-on:take-action="leave_group" :response=response :verb="'leave group'"
                 :action_name="'remove_members_from_community'" :check_permissions_params=check_params
                v-on:close-modal="modal_closed">
                <b-button id="leave_group_button" class="py-0" variant="link">leave</b-button>
            </take-action-component>

            <form-button-and-modal :item_model="'group'" :item_id=group_pk :button_text="'edit'"
                :supplied_classes="'btn-link border-0 py-0'"></form-button-and-modal>

        </span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import TakeActionComponent from '../actions/TakeActionComponent'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: { TakeActionComponent, FormButtonAndModal },
    store,
    data: function() {
        return {
            response: null
        }
    },
    computed: {
        ...Vuex.mapState({
            group_name: state => state.group_name,
            group_description: state => state.group_description,
            group_pk: state => state.group_pk,
            user_pk: state => state.user_pk
        }),
        ...Vuex.mapGetters(['userInGroup']),
        user_in_group: function() {
            return this.userInGroup(this.user_pk)
        },
        check_params: function() {
            return {member_pk_list: [store.state.user_pk]}
        }
    },
    methods: {
        ...Vuex.mapActions(['addMembers', 'removeMembers']),
        modal_closed() {
            // on modal close, if user has joined or left group, reloads to get fresh data
            if (this.response && this.response.data.action_status == "implemented") { window.location.reload() }
        },
        join_group(extra_data) {
            this.addMembers({ member_pk_list: [store.state.user_pk], extra_data : extra_data })
                .then(response => { this.response = response })
        },
        leave_group(extra_data) {
            this.removeMembers({ member_pk_list: [store.state.user_pk], extra_data : extra_data })
                .then(response => { this.response = response })
        },
        is_active(tab_name) {
            if (this.$route.meta.tab == tab_name) { return "tab-active" } else { return "tab-inactive" }
        }
    }

}

</script>

<style scoped>

a, a button {
color: black
}

.tab-active {
    font-weight: bold;
    color: #17a2b8;   /* info */
}

</style>