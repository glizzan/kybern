<template>

    <b-form :id=edit_leadership_id>

        <div class="mb-3">
            <b-input-group prepend="Roles" class="mb-2 mr-sm-2 mb-sm-0 flex-nowrap">
                <vue-multiselect v-model="roles_selected" :options="rolesAsOptions" :multiple="true"
                :close-on-select="true" :clear-on-select="false" placeholder="No roles selected"
                label="name" track-by="name">
                </vue-multiselect>
            </b-input-group>
        </div>

        <div class="mb-3">
            <b-input-group prepend="Individuals" class="mb-2 mr-sm-2 mb-sm-0 flex-nowrap">
                <vue-multiselect v-model="actors_selected" :options="groupMembersAsOptions" :multiple="true"
                :close-on-select="true" :clear-on-select="true" placeholder="No individuals selected"
                label="name" track-by="pk" prepend="Individuals">
                </vue-multiselect>
            </b-input-group>
        </div>

        <div class="mb-3">
            <take-action-component v-on:take-action=update_leadership :response=response :verb="'change ' + leadership_type + 's'"
                :action_name="'change_' + leadership_type + 's_of_community'"></take-action-component>
         </div>

    </b-form>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    props: ['leadership_type'],
    components: { "vue-multiselect": Multiselect, TakeActionComponent },
    store,
    data: function() {
        return {
            response: null,
            initial_actors: [],
            initial_roles: [],
            actors_selected: [],
            roles_selected: []
        }
    },
    created (){
        this.get_existing_roles_and_actors()
    },
    computed: {
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions', 'leadershipAsOptions']),
        edit_leadership_id: function() { return this.leadership_type + "_actors_and_roles" },
    },
    watch: {  leadershipAsOptions: function (val) { this.get_existing_roles_and_actors() } },
    methods: {
        ...Vuex.mapActions(['updateOwners', 'updateGovernors']),
        get_existing_roles_and_actors() {
            if (this.leadership_type == "owner") {
                this.roles_selected = this.leadershipAsOptions.owner_role_options
                this.initial_roles = this.leadershipAsOptions.owner_role_options
                this.actors_selected = this.leadershipAsOptions.owner_actor_options
                this.initial_actors = this.leadershipAsOptions.owner_actor_options
            } else if (this.leadership_type == "governor") {
                this.roles_selected = this.leadershipAsOptions.governor_role_options
                this.initial_roles = this.leadershipAsOptions.governor_role_options
                this.actors_selected = this.leadershipAsOptions.governor_actor_options
                this.initial_actors = this.leadershipAsOptions.governor_actor_options
            }
        },
        update_leadership(extra_data) {

            var roles_to_add = this.roles_selected.filter(x => !this.initial_roles.includes(x)).map(role => role.name)
            var actors_to_add = this.actors_selected.filter(x => !this.initial_actors.includes(x)).map(actor => actor.pk)
            var roles_to_remove = this.initial_roles.filter(x => !this.roles_selected.includes(x)).map(role => role.name)
            var actors_to_remove = this.initial_actors.filter(x => !this.actors_selected.includes(x)).map(actor => actor.pk)

            var params = { roles_to_add: roles_to_add, actors_to_add: actors_to_add, roles_to_remove: roles_to_remove,
                actors_to_remove: actors_to_remove, extra_data: extra_data }

            if (this.leadership_type == "owner") {
                this.updateOwners(params).then(response => this.response = response)
            } else if (this.leadership_type == "governor") {
                this.updateGovernors(params).then(response => this.response = response)
            }
        }
    }

}

</script>