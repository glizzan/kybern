<template>

    <b-form :id=edit_leadership_id>

        <div class="mb-3">
            <b-input-group prepend="Roles" class="mb-2 mr-sm-2 mb-sm-0 flex-nowrap">
                <vue-multiselect v-model="roles_selected" :options="rolesAsOptions" :multiple="true"
                :close-on-select="true" :clear-on-select="false" placeholder="No roles selected"
                :disabled="!has_permission" label="name" track-by="name">
                </vue-multiselect>
            </b-input-group>
        </div>

        <div class="mb-3">
            <b-input-group prepend="Individuals" class="mb-2 mr-sm-2 mb-sm-0 flex-nowrap">
                <vue-multiselect v-model="actors_selected" :options="groupMembersAsOptions" :multiple="true"
                :close-on-select="true" :clear-on-select="true" placeholder="No individuals selected"
                :disabled="!has_permission" label="name" track-by="pk" prepend="Individuals">
                </vue-multiselect>
            </b-input-group>
        </div>

        <div class="mb-3">
            <b-button v-if="has_permission" variant="outline-secondary" @click="update_leadership()">
                Update {{this.leadership_type}}s</b-button>
         </div>

        <error-component :message=error_message></error-component>

    </b-form>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['leadership_type'],
    components: { "vue-multiselect": Multiselect, ErrorComponent },
    store,
    data: function() {
        return {
            error_message: null,
            actors_selected: [],
            roles_selected: []
        }
    },
    created (){
        this.checkPermissions({permissions: {
            "add_owner_to_community": null, "remove_owner_from_community": null,
            "add_owner_role_to_community": null, "remove_owner_role_from_community": null,
            "add_governor_to_community": null, "remove_governor_from_community": null,
            "add_governor_role_to_community": null, "remove_governor_role_from_community": null
        }}).catch(error => {this.error_message = error})
        this.get_existing_roles_and_actors()
    },
    computed: {
        ...Vuex.mapState({user_permissions: state => state.permissions.current_user_permissions}),
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions', 'leadershipAsOptions']),
        edit_leadership_id: function() { return this.leadership_type + "_actors_and_roles" },
        has_permission: function() {
            if (this.leadership_type == "owner" && this.user_permissions) { return this.permission_to_update_owners() }
            if (this.leadership_type == "governor" && this.user_permissions) { return this.permission_to_update_governors() }
            return false
        }
    },
    watch: {  leadershipAsOptions: function (val) { this.get_existing_roles_and_actors() } },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'updateOwners', 'updateGovernors']),
        permission_to_update_owners: function() {
            return this.user_permissions.add_owner_to_community || this.user_permissions.remove_owner_from_community ||
                   this.user_permissions.add_owner_role_to_community || this.user_permissions.remove_owner_role_from_community
        },
        permission_to_update_governors: function() {
            return this.user_permissions.add_governor_to_community || this.user_permissions.remove_governor_from_community ||
                    this.user_permissions.add_governor_role_to_community || this.user_permissions.remove_governor_role_from_community
        },
        get_existing_roles_and_actors() {
            if (this.leadership_type == "owner") {
                this.roles_selected = this.leadershipAsOptions.owner_role_options
                this.actors_selected = this.leadershipAsOptions.owner_actor_options
            } else if (this.leadership_type == "governor") {
                this.roles_selected = this.leadershipAsOptions.governor_role_options
                this.actors_selected = this.leadershipAsOptions.governor_actor_options
            }
        },
        update_leadership(leadership_type) {
            var roles = this.roles_selected.map(role => role.name)
            var actors = this.actors_selected.map(actor => actor.pk)
            if (this.leadership_type == "owner") {
                this.updateOwners({roles: roles, actors:actors}).catch(error => { this.error_message = error.message })
            } else if (this.leadership_type == "governor") {
                this.updateGovernors({ roles: roles, actors: actors}).catch(error => { this.error_message = error.message })
            }
        }
    }

}

</script>