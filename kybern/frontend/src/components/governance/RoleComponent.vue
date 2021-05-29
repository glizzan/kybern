<template>

    <div class="bg-white p-3">

            <p>In addition to the required "members" role, groups can add custom roles which different people can
            be assigned to. Each role has different rights and responsibilities within the community.</p>

            <b-button class="btn-sm mr-3 mb-3" variant="info" v-b-modal.add_role_modal
                id="add_role_button">add a role</b-button>

            <b-button v-if="user_permissions.apply_template" class="btn-sm mb-3" variant="info"
                v-b-modal.apply_template_modal_role id="apply_role_templates">apply role templates</b-button>

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
                                 v-on:click="role_selected = role.name; mode = 'add'" :id="role.name + '_remove_members'">
                                <b-icon-person-plus v-b-tooltip.hover title="add members">
                                </b-icon-person-plus>
                            </div>

                            <div v-if="role.name != 'members'" class="ml-3 d-inline-block" v-b-modal.role_membership_modal
                                 v-on:click="role_selected = role.name; mode = 'remove'" :id="role.name + '_add_members'" :mode="'remove'">
                                <b-icon-person-dash v-b-tooltip.hover title="remove members">
                                </b-icon-person-dash>
                            </div>

                            <div class="ml-3 d-inline-block" v-b-modal.role_permissions_modal :id="role.name + '_editrole'"
                                v-on:click="role_selected = role.name">
                                <b-icon-shield-lock v-b-tooltip.hover title="change permissions">
                                </b-icon-shield-lock>
                            </div>

                            <take-action-component v-if="role.name != 'members'" v-on:take-action="remove_role(role.name, $event)"
                                :response=response :verb="'remove role ' + role.name" :action_name="'remove_role_from_community'">
                                <b-icon-trash v-b-tooltip.hover title="delete" class="ml-3 d-inline-block"></b-icon-trash>
                            </take-action-component>

                        </div>
                </b-list-group-item>

            </b-list-group>

        <add-role-modal></add-role-modal>
        <role-membership-component :role_selected=role_selected :mode=mode></role-membership-component>
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
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    store,
    components: { AddRoleModal, RolePermissionsModal, RoleMembershipComponent, TemplateModal, TakeActionComponent },
    data: function() {
        return {
            role_selected: '',
            mode: null,
            response: null,
        }
    },
    created () {
        this.checkPermissions({permissions: {"apply_template": null}})
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
        remove_role(role_name, extra_data) {
            this.removeRole({role_name: role_name, extra_data: extra_data})
                .then(response => { this.response = response })
        }
    }

}

</script>