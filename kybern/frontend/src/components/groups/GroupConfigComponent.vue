<template>

    <span class="d-flex my-3">

        <!-- left aligned nav -->
        <span class="flex-grow-1">

            <span class="font-weight-bold"><b-icon-people-fill class="mr-2"></b-icon-people-fill>{{group_name}}</span>

            <router-link id="resources_button" :to="{ name: 'home'}" :exact-active-class="'selected-link'">
                <b-icon-grid class="ml-3 mr-1"></b-icon-grid>Resources
            </router-link>

            <router-link id="group_history_button" :to="{ name: 'action-history', params: { item_id: group_pk,
            item_model: 'group', item_name: group_name }}" :exact-active-class="'selected-link'">
                <b-icon-clock-history class="ml-3 mr-1"></b-icon-clock-history>History
            </router-link>

            <router-link id="governance_button" :to="{ name: 'governance'}" :exact-active-class="'selected-link'">
                <b-icon-person-lines-fill class="ml-3 mr-1"></b-icon-person-lines-fill>Group Roles
            </router-link>

            <router-link id="group_permissions_button" :exact-active-class="'selected-link'"
                :to="{ name: 'group-permissions', params: { group_pk: group_pk}}">
                <b-icon-shield-lock-fill class="ml-3 mr-1"></b-icon-shield-lock-fill>Permissions
            </router-link>

        </span>


        <!-- right aligned nav -->
        <span>

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


export default {

    store,
    data: function() {
        return {
            error_message: null
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
            this.addMembers({ user_pks: [store.state.user_pk] }).then(response => window.location.reload())
            .catch(error => {  this.error_message = error; console.log(error) })
        },
        leave_group() {
            this.removeMembers({ user_pks: [store.state.user_pk] }).then(response => window.location.reload())
            .catch(error => {  this.error_message = error; console.log(error) })
        }
    }

}

</script>

<style scoped>

a, a button {
color: black
}

.selected-link {
    font-weight: bold;
    color: #17a2b8;   /* info */
}

</style>