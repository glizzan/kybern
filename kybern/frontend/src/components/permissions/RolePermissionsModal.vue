<template>

    <b-modal id="role_permissions_modal" :title="title_string" size="xl" hide-footer>

        <p class="my-1">People with this role can...</p>

        <simple-permissions-display-component :permissions=role_permissions :role_to_edit=role_to_edit
            :item_id=group_id :item_model="'group'" :item_name="'Role ' + role_to_edit">
        </simple-permissions-display-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import SimplePermissionsDisplayComponent from '../permissions/SimplePermissionsDisplayComponent'


export default {

    props: ['role_to_edit'],
    components: { SimplePermissionsDisplayComponent },
    store,
    data: function() {
        return {
            error_message: ""
        }
    },
    created () {
        this.getPermissionsForItem({ item_id: this.group_id, item_model: 'group' })
        if (this.role_to_edit) {
            this.prepEditRole()
        }
    },
    computed: {
        ...Vuex.mapGetters(['permissionsForRole']),
        ...Vuex.mapState({ group_id: state => state.group_pk }),
        title_string: function () {
            return "Permissions for role '" + this.role_to_edit + "'"
        },
        role_permissions: function () {
            if (this.role_to_edit) {
                return this.permissionsForRole(this.role_to_edit)
            } else {
                return []
            }
        }
    },
    watch: {
        role_to_edit: function() {
            // When role to edit has been set, trigger vuex to load/update permission & condition data related to the role
            this.prepEditRole()
        }
    },
    methods: {
        ...Vuex.mapActions(['refreshRoleData', 'getPermissionsForItem']),
        prepEditRole() {
            this.refreshRoleData({ role: this.role_to_edit }).catch(error => {
                this.error_message = error
            })
        }
    }

}

</script>

