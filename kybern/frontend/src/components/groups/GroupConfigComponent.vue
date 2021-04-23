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

            <action-response-component :response=group_response></action-response-component>

            <b-button v-if="user_permissions.join_group && !user_in_group" id="join_group_button" class="py-0"
                variant="link" @click="join_group()">join</b-button>

            <b-button v-if="user_permissions.leave_group && user_in_group" id="leave_group_button" class="py-0"
                variant="link" @click="leave_group()">leave</b-button>

            <span v-if="user_permissions.change_name || user_permissions.change_description">
                <router-link :to="{ name: 'edit-group'}" id="edit_group_button">
                    <b-button variant="link" class="py-0">edit</b-button>
                </router-link>
            </span>

        </span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    components: { ActionResponseComponent },
    store,
    data: function() {
        return {
            group_response: null
        }
    },
    created () {
        this.checkPermissions({
            permissions:
                {add_members_to_community: {member_pk_list: [store.state.user_pk]},
                 remove_members_from_community: {member_pk_list: [store.state.user_pk]},
                 change_name_of_community: null, change_group_description: null},
            aliases:
                {add_members_to_community: "join_group", remove_members_from_community: "leave_group",
                change_name_of_community: "change_name", change_group_description: "change_description"} })
    },
    computed: {
        ...Vuex.mapState({
            group_name: state => state.group_name,
            group_description: state => state.group_description,
            group_pk: state => state.group_pk,
            user_pk: state => state.user_pk,
            user_permissions: state => state.permissions.current_user_permissions
        }),
        ...Vuex.mapGetters(['userInGroup']),
        user_in_group: function() {
            return this.userInGroup(this.user_pk)
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'addMembers', 'removeMembers']),
        join_group() {
            this.addMembers({ user_pks: [store.state.user_pk] })
                .then(response => {
                    if (response.data.action_status == "implemented") { window.location.reload() }
                    else { this.group_response = response }
                })
        },
        leave_group() {
            this.removeMembers({ user_pks: [store.state.user_pk] })
            .then(response => {
                if (response.data.action_status == "implemented") { window.location.reload() }
                else { this.group_response = response }
            })
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