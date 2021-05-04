<template>

    <div class="bg-white p-3">

            <p>In addition to the required "members" role, groups can add custom roles which different people can
            be assigned to. Each role has different rights and responsibilities within the community.</p>

            <b-button v-if="user_permissions.add_role_to_community" class="btn-sm mr-3 mb-3" variant="info"
                v-b-modal.add_role_modal id="add_role_button">add a role</b-button>

            <b-button v-if="user_permissions.apply_template" class="btn-sm mb-3" variant="info"
                v-b-modal.apply_template_modal_role id="apply_role_templates">apply role templates</b-button>

            <action-response-component :response=remove_role_response></action-response-component>

            <b-list-group>

                <b-list-group-item v-for="role in combined_roles" v-bind:key="role.id"
                    class="d-flex justify-content-between align-items-center" :id="role.name + '_role'">

                        <span class="role_info">
                            <span class="role_name_display mr-2">{{ role.name }}</span>
                            <small class="d-inline-block" :id="role.name + '_member_count'">
                            {{role.current_members.length }} people </small>
                        </span>

                        <div class="role_interactions text-right">

                            <div v-if="role.name != 'members'" class="d-inline-block" v-b-modal.role_membership_modal
                                 v-on:click="role_selected = role.name" :id="role.name + '_changemembers'">
                                <b-icon-people v-b-tooltip.hover title="change members">
                                </b-icon-people>
                            </div>

                            <div class="ml-3 d-inline-block" v-b-modal.role_permissions_modal :id="role.name + '_editrole'"
                                v-on:click="role_selected = role.name">
                                <b-icon-shield-lock v-b-tooltip.hover title="change permissions">
                                </b-icon-shield-lock>
                            </div>

                            <div v-if="role.name != 'members'" class="ml-3 d-inline-block" v-on:click="remove_role(role.name)">
                                <b-icon-trash v-b-tooltip.hover title="delete">
                                </b-icon-trash>
                            </div>

                        </div>
                </b-list-group-item>

            </b-list-group>

        <add-role-modal></add-role-modal>
        <role-membership-component :role_selected=role_selected></role-membership-component>
        <role-permissions-modal :role_to_edit=role_selected></role-permissions-modal>
        <template-modal :scope="'role'"></template-modal>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import AddRoleModal from '../governance/AddRoleModal'
import RoleMembershipComponent from '../governance/RoleMembershipComponent'
import RolePermissionsModal from '../permissions/RolePermissionsModal'
import TemplateModal from '../templates/TemplateModal'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    store,
    components: { AddRoleModal, RolePermissionsModal, RoleMembershipComponent, TemplateModal, ActionResponseComponent },
    data: function() {
        return {
            role_selected: '',
            remove_role_response: null,
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
        }),
        combined_roles: function() {
            var combined_roles = [{name: "members", current_members: this.group_members}]
            return combined_roles.concat(this.roles)
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'removeRole']),
        remove_role(role_name) {
            this.removeRole({role_name: role_name})
                .then(response => { this.remove_role_response = response })
        }
    }

}

</script>