<template>

    <span>

        <h3>Change leadership of {{ group_name }}</h3>

        <p class="font-weight-bold">Owners</p>

        <p>Groups can be owned by a combination of individuals and people with specific roles.  There must
            always be at least one person who is an owner. Here are the current individuals and roles who
            are owners:</p>

            <edit-leadership-component leadership_type="owner"></edit-leadership-component>

        <p class="mt-3">If owners have "unconditional" power this means any one owner - whether matched as an individual,
            or matched through roles - can make arbitrary changes to the community, including deleting it.
            Unless you have a small, new group, you probably don't want this, so we recommend setting a
            condition.  Here's the condition currently set:</p>

            <div class="border m-2 p-2 text-center">
                <span v-if="owner_condition_display">{{ owner_condition_display }}</span>
                <span v-else>No condition set</span>
                <router-link v-if="user_permissions.add_owner_condition || user_permissions.remove_owner_condition"
                    :to="{name: 'conditions', params: {conditioned_on: 'owner'}}">
                    <span class="badge badge-secondary ml-1 edit-condition">edit</span>
                </router-link>
            </div>

        <p class="font-weight-bold">Governors</p>

        <p>Often we want to give people power in a community without granting it to them completely or
            permanently.  For instance, if our owners are a large collective of people who take action by
            voting, we may want to give a small number of people the ability to "manage" the community so they
            can take action quickly.  But if they abuse that power, we want the ability to remove them.</p>
        <p>We call these people "governors".  By default, they can do most things in the community, although
            the group can always override their power to do specific things.  If the owners are unhappy with
            the governors, they can remove or change them.</p>
        <p>Governors are optional. Here are the current individuals and roles who are governors:</p>

            <edit-leadership-component leadership_type="governor"></edit-leadership-component>

        <p class="mt-3">Just as with owners, you can set a condition on governors.  This is less common, as the main point
            of appointing governors is so they can act efficiently, but can still be useful.  Here's the condition
            currently set:</p>

            <div class="border m-2 p-2 text-center">
                <span v-if="governor_condition_display">{{ governor_condition_display }}</span>
                <span v-else>No condition set</span>
                <router-link v-if="user_permissions.add_governor_condition || user_permissions.remove_governor_condition"
                    :to="{name: 'conditions', params: {conditioned_on: 'governor'}}">
                    <span class="badge badge-secondary ml-1 edit-condition">edit</span>
                </router-link>
            </div>

        <p class="font-weight-bold">Just so you know</p>

        <p>There are some actions that owners can't delegate to governors - in order to make these changes,
            the owners will have to take the action.  These changes are:</p>

        <ul>
            <li>adding and removing owners, both individuals and roles</li>
            <li>adding and removing governors, both individuals and roles</li>
            <li>making it so only owners can change a specific resource, or removing that restriction from a
                specific resource</li> <!-- aka enabling or disabling the foundational permission on an object -->
            <li>making it so governors cannot change a specific resource, or removing that restriction from a
                specific resource</li> <!-- aka enabling or disabling the governing permission on an object -->
        </ul>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    store,
    mounted () {
        this.checkPermissions({permissions: { add_owner_condition: null, remove_owner_condition: null,
            add_governor_condition: null, remove_governor_condition: null }}).catch(error => { console.log(error) })
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