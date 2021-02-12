<template>

    <span>

        <b-card no-body class="my-3">

            <b-card-header>

                <span class="float-left">Roles</span>

                <span class="float-right">
                    <b-button v-if="user_permissions.add_role_to_community" class="btn-sm"
                        v-b-modal.add_role_modal id="add_role_button">add a role</b-button>

                    <router-link v-if="user_permissions.apply_template"
                        :to="{ name: 'item-templates', params: {scope: 'role', target_id: group_pk, target_model: 'group'} }">
                        <b-button class="btn-sm" id="apply_role_templates">role templates</b-button>
                    </router-link>
                </span>

            </b-card-header>

            <b-card-text class="p-3">

                <p>Each group has a variety of roles which different people can be assigned to. Each
                    role has different rights and responsibilities within the community.</p>

                <error-component :message=error_message></error-component>

                <b-list-group>

                        <b-list-group-item class="d-flex justify-content-between align-items-center"
                            :id="'members_role'">
                            <span class="role_info">
                                <span class="role_name_display">members</span>
                                <small class="ml-2" :id="'members_member_count'"> {{ group_members.length }} people </small>
                            </span>
                            <div class="role_interactions">
                                <router-link :to="{ name: 'role-permissions', params: { role_to_edit: 'members' }}">
                                    <b-button variant="info" pill id="members_editrole">permissions</b-button>
                                </router-link>
                            </div>
                        </b-list-group-item>

                        <b-list-group-item v-for="role in roles" v-bind:key="role.id"
                            class="d-flex justify-content-between align-items-center" :id="role.name + '_role'">
                                <span class="role_info">
                                        <span class="role_name_display">{{ role.name }}</span>
                                        <small class="ml-2" :id="role.name + '_member_count'">
                                        {{role.current_members.length }} people </small>
                                </span>
                                <div class="role_interactions">
                                    <b-button variant="secondary" pill v-b-modal.role_membership_modal
                                        v-on:click="role_to_change_membership = role.name" :id="role.name + '_changemembers'">
                                        change members</b-button>
                                    <router-link :to="{ name: 'role-permissions', params: { role_to_edit: role.name }}">
                                        <b-button variant="info" pill :id="role.name + '_editrole'">
                                            permissions</b-button>
                                    </router-link>
                                    <b-button variant="danger" pill v-on:click="remove_role(role.name)">
                                        remove</b-button>
                                </div>
                        </b-list-group-item>

                </b-list-group>

            </b-card-text>

        </b-card>

        <add-role-component></add-role-component>
        <role-membership-component :role_selected=role_to_change_membership></role-membership-component>


    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import AddRoleComponent from '../governance/AddRoleComponent'
import RoleMembershipComponent from '../governance/RoleMembershipComponent'


export default {

    store,
    components: { ErrorComponent, AddRoleComponent, RoleMembershipComponent },
    data: function() {
        return {
            role_to_change_membership: '',               // prop for add-people-to-role-modal
            error_message: null,
        }
    },
    created () {
        this.checkPermissions({permissions: {"add_role_to_community": null, "apply_template": null}})
        .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({
            roles: state => state.governance.roles,
            group_members: state => state.governance.members,
            user_permissions: state => state.permissions.current_user_permissions,
            group_pk: state => state.group_pk
        })
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'removeRole']),
        remove_role(role_name) {
            this.removeRole({role_name: role_name})
            .catch(error => {  this.error_message = error  })
        }
    }

}

</script>