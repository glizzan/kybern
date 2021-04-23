<template>

    <b-modal id="role_membership_modal" :title="title_string" hide-footer>

        <span class="font-weight-bold">{{ permission_string }}</span>

        <div v-if="can_edit">

            <span id="change_membership_multiselect">
                <vue-multiselect v-model="people_selected" :options="people_to_choose_from" :multiple="true"
                :close-on-select="true" :clear-on-select="false" placeholder="No one selected"
                label="name" track-by="pk" class="mt-3">
                </vue-multiselect>
            </span>

            <action-response-component :response=add_people_response></action-response-component>
            <action-response-component :response=remove_people_response></action-response-component>

            <b-button class="btn-sm mt-3" @click="updateMembers()" id="save_member_changes">Save your changes</b-button>

        </div>

        <div v-else class="mt-3">
            <span class="font-weight-bold">Current Members in Role</span><br />
            <b-badge v-for="member in people_selected" v-bind:key="member.pk" pill variant="info" class="mx-1">
                {{ member.name }}</b-badge>
        </div>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    props: ['role_selected'],
    store,
    components: { "vue-multiselect": Multiselect, ActionResponseComponent },
    data: function() {
        return {
            add_people_response: null,
            remove_people_response: null,
            people_selected: []
        }
    },
    created () {
        this.checkPermissions({permissions:
            {"add_people_to_role": {"role_name": this.role_selected}, "remove_people_from_role": {"role_name": this.role_selected}}})
        .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        ...Vuex.mapGetters(['membersAsOptions']),
        people_to_choose_from: function() {
            return this.membersAsOptions("members")
        },
        people_in_role: function() {
            if (this.role_selected) {
                return this.membersAsOptions(this.role_selected)
            } else {
                return []
            }
        },
        title_string: function() {
            return "Change members with role '" + this.role_selected + "'"
        },
        can_edit: function() {
            if (this.user_permissions.add_people_to_role || this.user_permissions.remove_people_from_role) {
                return true } else { return false }
        },
        permission_string: function() {
            if (this.user_permissions.add_people_to_role && this.user_permissions.remove_people_from_role) {
                return "You have permission to add and remove people from this role." }
            if (this.user_permissions.add_people_to_role) {
                return "You have permission to add people to this role, but not to remove people from it." }
            if (this.user_permissions.remove_people_from_role) {
                return "You have permission to remove people from this role, but not to add people to it." }
            return "You do not have permission to add people to or remove people from this role."
        }
    },
    watch: {
        role_selected: function() {
            console.log(this.people_in_role)
            this.people_selected = this.people_in_role  // populate with current data initially
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'addUsersToRole', 'removeUsersFromRole']),
        updateMembers() {

            var old_array = this.people_in_role.map(person => person.pk)
            var new_array  =this.people_selected.map(person => person.pk)
            var to_remove = old_array.filter(x => !new_array.includes(x))
            var to_add = new_array.filter(x => !old_array.includes(x))

            if (to_add.length > 0) {
                this.addUsersToRole({ role_name: this.role_selected, user_pks: to_add })
                    .then(response => { this.add_people_response = response })
            }

            if (to_remove.length > 0) {
                this.removeUsersFromRole({ role_name: this.role_selected, user_pks: to_remove })
                    .then(response => { this.remove_people_response = response })
            }
        }
    }

}

</script>