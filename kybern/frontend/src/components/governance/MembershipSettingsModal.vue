<template>

    <b-modal id="group_membership_settings_display" title="Membership Settings" class="modalfade" size="xl" hide-footer>

            <p v-if="user_permissions.apply_template" class="mb-4" >
                Not sure what to pick?
                <span class="text-info" id="membership_templates_link" v-b-modal.apply_template_modal_membership>
                    Browse pre-existing membership templates and apply them to your community.</span>
            </p>

            <template-modal :scope="'membership'"></template-modal>

            <error-component :message=error_message></error-component>

            <span id="add_member_permissions">

                <p class="pb-1 font-weight-bold">Permissions for Adding Members</p>

                <simple-permissions-display-component :permissions=addmember_permissions :item_id=item_id
                    :item_model=item_model :item_name="'Adding Members'"
                    :default_selection="'add members to community'">
                </simple-permissions-display-component>

            </span>

            <span id="remove_member_permissions">

                <p class="pt-4 pb-1 font-weight-bold">Permissions for Removing Members</p>

                <simple-permissions-display-component :permissions=removemember_permissions :item_id=item_id
                    :item_model=item_model :item_name="'Removing Members'"
                    :default_selection="'remove members from community'">
                </simple-permissions-display-component>

            </span>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import SimplePermissionsDisplayComponent from '../permissions/SimplePermissionsDisplayComponent'
import TemplateModal from '../templates/TemplateModal'


export default {

    store,
    components: { ErrorComponent, SimplePermissionsDisplayComponent, TemplateModal },
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