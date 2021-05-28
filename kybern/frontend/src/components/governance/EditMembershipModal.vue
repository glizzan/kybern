<template>

    <b-modal id="group_membership_display" title="Group Membership" class="modal fade"
            size="lg" hide-footer @hide="refresh">

        <b>Current Members:</b>
            <span id="current_member_list"> <b-badge v-for="member in groupMembersAsOptions" v-bind:key="member.pk"
            pill variant="info" class="mx-1">{{ member.name }}</b-badge></span>

        <span v-if="mode=='add'">

            <vue-multiselect v-model="members_to_add_selected" :options="nonmembersAsOptions"
                :multiple="true" :close-on-select="true" :clear-on-select="false" class="my-3"
                placeholder="Select people to add" label="name" track-by="name"></vue-multiselect>

            <take-action-component v-on:take-action=add_members :response=response :inline="'true'"
                :verb="'add members to community'"></take-action-component>

        </span>

        <span v-else>

            <vue-multiselect v-model="members_to_remove_selected" :options="groupMembersAsOptions"
                :multiple="true" :close-on-select="true" :clear-on-select="false" class="my-3"
                placeholder="Select people to remove" label="name" track-by="name"></vue-multiselect>

            <take-action-component v-on:take-action=remove_members :response=response :inline="'true'"
                :verb="'remove members from community'"></take-action-component>

        </span>

    </b-modal>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    props: ['mode'],
    store,
    components: { TakeActionComponent, "vue-multiselect": Multiselect },
    data: function() {
        return {
            item_model: 'group',  // group model
            members_to_add_selected: [],
            members_to_remove_selected: [],
            response: null
        }
    },
    computed: {
        ...Vuex.mapState({
            item_id: state => state.group_pk
        }),
        ...Vuex.mapGetters(['groupMembersAsOptions', 'nonmembersAsOptions'])
    },
    methods: {
        ...Vuex.mapActions(['addMembers', 'removeMembers']),
        refresh() {
            this.members_to_add_selected = []
            this.members_to_remove_selected = []
            this.response = null
        },
        add_members() {
            var members_to_add = this.members_to_add_selected.map(actor => actor.pk)
            this.addMembers({ member_pk_list: members_to_add })
                .then(response => { this.response = response })
        },
        remove_members() {
            var members_to_remove = this.members_to_remove_selected.map(actor => actor.pk)
            this.removeMembers({ member_pk_list: members_to_remove })
                .then(response => { this.response = response })
        }
    }

}

</script>
