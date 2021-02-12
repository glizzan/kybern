<template>
    <span>

        <b-card-group deck class="mb-4">

            <b-card v-if="governance_forum" class="bg-light border-secondary" no-body>
                <b-card-header>
                    <router-link v-if=governance_forum class="text-info"
                            :to="{ name: 'governance-forum-detail', params: { forum_id: governance_forum.pk } }">
                        {{ governance_forum.name }} </router-link>
                </b-card-header>
                <b-card-text id="forum-description" class="text-muted p-3">
                    {{ governance_forum.description }} of {{ group_name }}
                </b-card-text>
            </b-card>

            <b-card class="bg-light border-secondary" no-body>
                <b-card-header>
                    <router-link class="text-info" :to="{ name: 'templates', params: {scope: 'community'}}">
                        Community Templates </router-link>
                </b-card-header>
                <b-card-text id="community_templates_link" class="text-muted p-3">
                    Browse pre-existing governance setups and apply them to your community.
                </b-card-text>
            </b-card>

        </b-card-group>

        <leadership-component></leadership-component>

        <group-membership-component></group-membership-component>

        <role-component></role-component>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import LeadershipComponent from '../governance/LeadershipComponent'
import GroupMembershipComponent from '../governance/GroupMembershipComponent'
import RoleComponent from '../governance/RoleComponent'


export default {

    components: { LeadershipComponent, GroupMembershipComponent, RoleComponent },
    store,
    data: function() {
        return {
            error_message: null,
        }
    },
    computed: {
        ...Vuex.mapState({ forums: state => state.forums.forums, group_name: state => state.group_name }),
        governance_forum: function() {
            var gov_forum = null
            this.forums.forEach((forum) => { if (forum.special == "Gov") { gov_forum = forum } })
            return gov_forum
        }
    }

}

</script>