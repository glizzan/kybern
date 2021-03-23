<template>

    <div class="mt-3">

        <b-button v-if="user_permissions.add_members_to_community || user_permissions.remove_members_from_community"
            class="btn-sm btn-info mr-3 mb-3" v-b-modal.group_membership_display id="group_membership_display_button">
            change members</b-button>

        <edit-membership-modal></edit-membership-modal>

        <b-button class="btn-sm btn-info mb-3" v-b-modal.group_membership_settings_display
            id="group_membership_settings_button">
            change membership settings</b-button>

        <membership-settings-modal></membership-settings-modal>

        <div id="current_member_list" class="bg-white p-3">
            <b-table small :items="members_and_roles" :fields="fields">

                <template #cell(member)="data">
                    <router-link :to="{ name: 'user-permissions', params: { 'user_pk': data.item.pk } }" class="text-info">
                        {{ data.item.member }}
                    </router-link>
                </template>

                <template #cell()="data">
                    <span v-if="data.value != undefined && data.value == true">
                        <b-icon-check-circle-fill variant="success">
                        </b-icon-check-circle-fill>
                    </span>
                    <span v-else>
                        <b-icon-x variant="danger"></b-icon-x>
                    </span>
                </template>

            </b-table>
        </div>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import EditMembershipModal from '../governance/EditMembershipModal'
import MembershipSettingsModal from '../governance/MembershipSettingsModal'


export default {

    components: { EditMembershipModal, MembershipSettingsModal },
    store,
    created () {
        this.checkPermissions({permissions: {"add_members_to_community": null, "remove_members_from_community": null }})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        ...Vuex.mapGetters(['groupMembersAsOptions', 'allRoleNames', 'rolesForMember']),
        members_and_roles: function() {
            var vue_data = this
            var items = []
            this.groupMembersAsOptions.forEach(member => {
                var row = {member: member.name, pk: member.pk}
                var roles_user_is_in = this.rolesForMember(member.pk)
                vue_data.fields.forEach(field => {
                    if (roles_user_is_in.includes(field)) { row[field] = true }
                })
                items.push(row)
            })
            return items
        },
        fields: function() {
            var role_names = []
            this.allRoleNames.forEach(name => {
                if (name != "members") { role_names.push(name) }
            })
            return ["member"].concat(role_names)
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions'])
    }

}

</script>
