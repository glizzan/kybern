<template>

    <b-modal id="role_membership_modal" :title="title_string" hide-footer @hide="refresh">

        <span id="add_membership_multiselect">
            <vue-multiselect v-model="people_selected" :options="people_to_choose_from" :multiple="true"
            :close-on-select="true" :clear-on-select="false" placeholder="No one selected"
            label="name" track-by="pk" class="my-3">
            </vue-multiselect>
        </span>

        <div v-if="no_valid_action">{{ no_valid_action }}</div>

        <take-action-component v-else v-on:take-action=updateMembers :response=response :inline="true"
            :verb=verb :action_name=action_name :check_permissions_params=check_permissions_params>
        </take-action-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    props: ['role_selected', 'mode'],
    store,
    components: { "vue-multiselect": Multiselect, TakeActionComponent },
    data: function() {
        return {
            response: null,
            people_selected: [],
            no_valid_action: null
        }
    },
    created () {
        if (this.mode == "remove" && this.people_in_role.length == 0) {
            this.no_valid_action = "There is no one in this role who can be removed."
        }
        if (this.mode == "add" && this.people_to_choose_from.length == this.people_in_role.length) {
            this.no_valid_action = "All members are already in this role."
        }
    },
    computed: {
        ...Vuex.mapGetters(['membersAsOptions']),
        people_to_choose_from: function() {
            return this.membersAsOptions("members")
        },
        people_in_role: function() {
            if (this.role_selected) { return this.membersAsOptions(this.role_selected) }
            else { return [] }
        },
        title_string: function() {
            if (this.mode == "add") { return "Add people to role " + this.role_selected }
            else { return "Remove people from role " + this.role_selected }
        },
        action_name: function() {
            if (this.mode == "add") { return "add_people_to_role" } else { return "remove_people_from_role"}
        },
        verb: function() {
            if (this.mode == "add") { return "add people to role '" + this.role_selected + "'"}
            else { return "remove people from role '" + this.role_selected + "'"}
        },
        check_permissions_params: function() { return {role_name: this.role_selected } }
    },
    watch: {
        role_selected: function() {
            this.people_selected = this.people_in_role  // populate with current data initially
        }
    },
    methods: {
        ...Vuex.mapActions(['addUsersToRole', 'removeUsersFromRole']),
        refresh() {
            this.response = null
            this.people_selected = []
            this.no_valid_action = null
        },
        updateMembers(extra_data) {

            var old_array = this.people_in_role.map(person => person.pk)
            var new_array  =this.people_selected.map(person => person.pk)

            if (this.mode == "add") {

                var to_add = new_array.filter(x => !old_array.includes(x))
                if (to_add.length > 0) {
                    this.addUsersToRole({ role_name: this.role_selected, people_to_add: to_add, extra_data: extra_data })
                        .then(response => { this.response = response })
                }

            } else {

                var to_remove = old_array.filter(x => !new_array.includes(x))
                if (to_remove.length > 0) {
                    this.removeUsersFromRole({ role_name: this.role_selected, people_to_remove: to_remove,
                        extra_data: extra_data }).then(response => { this.response = response })
                }

            }

        }
    }

}

</script>