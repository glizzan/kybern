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

                <simple-permissions-display-component :permissions=addmember_permissions :item_id=item_id
                    :item_model=item_model :item_name="'Adding Members'"
                    :default_selection=add_member_state_change :modal_id="'addmember'">
                </simple-permissions-display-component>

            </span>

            <span id="remove_member_permissions">

                <p class="pt-4 pb-1 font-weight-bold">Permissions for Removing Members</p>

                <simple-permissions-display-component :permissions=removemember_permissions :item_id=item_id
                    :item_model=item_model :item_name="'Removing Members'"
                    :default_selection=remove_member_state_change :modal_id="'removemember'">
                </simple-permissions-display-component>

            </span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import SimplePermissionsDisplayComponent from '../permissions/SimplePermissionsDisplayComponent'


export default {

    store,
    components: { ErrorComponent, SimplePermissionsDisplayComponent },
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