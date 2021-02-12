<template>

    <span>

        <h3>Group Membership Settings</h3>

            <router-link v-if="user_permissions.apply_template" :to="{ name: 'templates', params: {scope: 'membership'}}">
                <b-card title="Membership Templates" class="bg-light text-info border-secondary my-4">
                    <p id="membership_templates_link" class="mb-1 text-secondary">Browse pre-existing membership setups and
                        apply them to your community.</p></b-card>
            </router-link>

            <error-component :message=error_message></error-component>

            <span id="add_member_permissions">
                <p class="pb-1 font-weight-bold">Permissions for Adding Members</p>
                <edit-permission-component v-for="permission in addmember_permissions" v-bind:key="permission.pk"
                    :permission=permission :item_id=item_id :item_model=item_model> </edit-permission-component>
                <p v-if="!addmember_permissions.length">No permissions for adding members have been
                    set yet. This means only people with foundational or governing permission can
                    add members.</p>
                <add-permission-component :default_selection=add_member_state_change :item_id=item_id
                    :item_model=item_model> </add-permission-component>
            </span>

            <span id="remove_member_permissions">
                <p class="pt-4 pb-1 font-weight-bold">Permissions for Removing Members</p>
                <edit-permission-component v-for="permission in removemember_permissions" v-bind:key="permission.pk"
                    :permission=permission :item_id=item_id :item_model=item_model> </edit-permission-component>
                <p v-if="!removemember_permissions.length">No permissions for removing members have
                    been set yet. This means only people with foundational or governing permission can
                    remove members.</p>
                <add-permission-component :default_selection=remove_member_state_change :item_id=item_id
                    :item_model=item_model></add-permission-component>
            </span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import AddPermissionComponent from '../permissions/AddPermissionComponent'
import EditPermissionComponent from '../permissions/EditPermissionComponent'


export default {

    store,
    components: { ErrorComponent, AddPermissionComponent, EditPermissionComponent },
    data: function() {
        return {
            item_model: 'group',  // group model
            add_member_state_change: 'concord.communities.state_changes.AddMembersStateChange',
            remove_member_state_change: 'concord.communities.state_changes.RemoveMembersStateChange',
            error_message: null
        }
    },
    created () {
        this.checkPermissions({permissions: {"apply_template": null}})
            .catch(error => {  this.error_message = error; console.log(error) })
        this.getPermissionsForItem({ item_id: this.item_id, item_model: this.item_model })
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({
            permissions: state => state.permissions.permissions,
            user_permissions: state => state.permissions.current_user_permissions,
            item_id: state => state.group_pk
        }),
        addmember_permissions: function() {
            return Object.values(this.permissions).filter(permission =>
                permission.change_type == this.add_member_state_change)
        },
        removemember_permissions: function() {
            return Object.values(this.permissions).filter(permission =>
                permission.change_type == this.remove_member_state_change)
        }
    },
    methods: {
        ...Vuex.mapActions(['getPermissionsForItem', 'checkPermissions']),
    }

}

</script>