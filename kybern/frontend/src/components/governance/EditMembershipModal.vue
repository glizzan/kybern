<template>

    <b-modal id="group_membership_display" title="Group Membership" class="modal fade" size="lg" hide-footer>

        <error-component :message=error_message></error-component>

        <b>Current Members:</b>
            <span id="current_member_list"> <b-badge v-for="member in groupMembersAsOptions" v-bind:key="member.pk"
            pill variant="info" class="mx-1">{{ member.name }}</b-badge></span>

        <hr >

        <span v-if="user_permissions.add_members_to_community">

            <span v-if="add_member_button_selected">
                <vue-multiselect v-model="members_to_add_selected" :options="nonmembersAsOptions" :multiple="true"
                    :close-on-select="true" :clear-on-select="false" placeholder="No one selected"
                    label="name" track-by="name">
                </vue-multiselect>
                <b-button class="btn-sm mt-2 mb-3 mr-3" id="save_add_member_button" @click="add_members()">Save</b-button>
                <b-button class="btn-sm mt-2 mb-3" @click="add_member_button_selected = false">Discard</b-button>
            </span>
            <span v-else>
                <span v-if="!remove_member_button_selected">
                    <b-button class="btn-sm mb-3 mr-3" id="add_member_button"
                        @click="add_member_button_selected = true">Add Members</b-button>
                </span>
            </span>

        </span>

        <span v-if="user_permissions.remove_members_from_community">

            <span v-if="remove_member_button_selected">
                <vue-multiselect v-model="members_to_remove_selected" :options="groupMembersAsOptions" :multiple="true"
                    :close-on-select="true" :clear-on-select="false" placeholder="No one selected"
                    label="name" track-by="name">
                </vue-multiselect>
                <b-button class="btn-sm mt-2 mb-3 mr-3" id="save_remove_member_button" @click="remove_members()">Save</b-button>
                <b-button class="btn-sm mt-2 mb-3" @click="remove_member_button_selected = false">Discard</b-button>
            </span>
            <span v-else>
                <span v-if="!add_member_button_selected">
                    <b-button class="btn-sm mb-3" id="remove_member_button"
                        @click="remove_member_button_selected = true">Remove Members</b-button>
                </span>
            </span>

        </span>

    </b-modal>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    store,
    components: { ErrorComponent, "vue-multiselect": Multiselect },
    data: function() {
        return {
            item_model: 'group',  // group model
            add_member_button_selected: false,
            remove_member_button_selected: false,
            members_to_add_selected: [],
            members_to_remove_selected: [],
            error_message: null
        }
    },
    created () {
        this.checkPermissions({permissions: {"add_members_to_community": null, "remove_members_from_community": null }})
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
        ...Vuex.mapGetters(['groupMembersAsOptions', 'nonmembersAsOptions'])
    },
    methods: {
        ...Vuex.mapActions(['getPermissionsForItem', 'checkPermissions', 'addMembers', 'removeMembers']),
        add_members() {
            var members_to_add = this.members_to_add_selected.map(actor => actor.pk)
            this.addMembers({ user_pks: members_to_add }).catch(error => this.error_message = error)
        },
        remove_members() {
            var members_to_remove = this.members_to_remove_selected.map(actor => actor.pk)
            this.removeMembers({ user_pks: members_to_remove }).catch(error => this.error_message = error)
        }
    }

}

</script>
