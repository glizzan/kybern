<template>

    <span id="edit_role_section">

        <h3>{{ title_string }}</h3>

        <p class="my-1">People with this role can...</p>

        <simple-permissions-display-component :permissions=role_permissions :role_to_edit=role_to_edit
            :item_id=group_id :item_model="'group'" :item_name="'Role ' + role_to_edit">
        </simple-permissions-display-component>

    </span>

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
    created () { if (this.role_to_edit) { this.prepEditRole() } },
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
        ...Vuex.mapActions(['refreshRoleData']),
        prepEditRole() {
            this.refreshRoleData({ role: this.role_to_edit }).catch(error => {
                this.error_message = error
            })
        }
    }

}

</script>

