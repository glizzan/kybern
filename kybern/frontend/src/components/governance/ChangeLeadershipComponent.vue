<template>

<b-container>

    <b-row>

        <b-col cols=6 class="pl-0">
            <div class="bg-white p-3">

                <p class="font-weight-bold">Change Owners</p>

                <edit-leadership-component leadership_type="owner"></edit-leadership-component>

                <h6 class="font-italic">Condition on owners:</h6>

                <div class="border m-2 p-2 text-center">
                    <span v-if="owner_condition_display">{{ owner_condition_display }}</span>
                    <span v-else>No condition set</span>
                    <router-link v-if="user_permissions.add_owner_condition || user_permissions.remove_owner_condition"
                        :to="{name: 'conditions', params: {conditioned_on: 'owner'}}">
                        <span class="badge badge-secondary ml-1 edit-condition">edit</span>
                    </router-link>
                </div>

            </div>
        </b-col>

        <b-col cols=6 class="pr-0">
            <div class="bg-white p-3">

                <p class="font-weight-bold">Change Governors</p>

                <edit-leadership-component leadership_type="governor"></edit-leadership-component>

                <h6 class="font-italic">Condition on governors:</h6>

                <div class="border m-2 p-2 text-center">
                    <span v-if="governor_condition_display">{{ governor_condition_display }}</span>
                    <span v-else>No condition set</span>
                    <router-link v-if="user_permissions.add_governor_condition || user_permissions.remove_governor_condition"
                        :to="{name: 'conditions', params: {conditioned_on: 'governor'}}">
                        <span class="badge badge-secondary ml-1 edit-condition">edit</span>
                    </router-link>
                </div>

            </div>
        </b-col>

    </b-row>
</b-container>
</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import EditLeadershipComponent from '../governance/EditLeadershipComponent'


export default {

    components: { EditLeadershipComponent },
    store,
    mounted () {
        this.checkPermissions({
            permissions: {
                add_condition: {leadership_type: 'owner'},
                remove_condition: {leadership_type: 'owner'}
            },
            aliases: {
                add_condition: "add_owner_condition", remove_condition: "remove_owner_condition"
            }
        }).catch(error => { console.log(error) })
        this.checkPermissions({
            permissions: {
                add_condition: {leadership_type: 'governor'},
                remove_condition: {leadership_type: 'governor'}
            },
            aliases: {
                add_condition: "add_governor_condition", remove_condition: "remove_governor_condition"
            }
        }).catch(error => { console.log(error) })
    },
    computed: {
        ...Vuex.mapState({
            owner_condition: state => state.permissions.owner_condition,
            governor_condition: state => state.permissions.governor_condition,
            user_permissions: state => state.permissions.current_user_permissions,
            group_name: state => state.group_name
        }),
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions', 'leadershipAsOptions']),
        owner_condition_display: function() {
            if (this.owner_condition) { return this.owner_condition.how_to_pass_overall }
            else { return "No condition has been set on owners." }
        },
        governor_condition_display: function() {
            if (this.governor_condition) { return this.governor_condition.how_to_pass_overall }
            else { return "No condition has been set on governors." }
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions']),
    }

}

</script>