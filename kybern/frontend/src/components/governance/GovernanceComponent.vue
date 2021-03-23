<template>

    <b-row>
        <b-col cols=3 class="p-3">

            <b-list-group class="mb-3">
                <b-list-group-item :active="selected_component=='leadership'" @click="selected_component='leadership'">
                    Leadership</b-list-group-item>
                <b-list-group-item :active="selected_component=='membership'" @click="selected_component='membership'">
                    Members</b-list-group-item>
                <b-list-group-item :active="selected_component=='customroles'" @click="selected_component='customroles'">
                    Custom Roles</b-list-group-item>
            </b-list-group>

            <b-card v-if="governance_forum" class="bg-white mb-3">
                <router-link :to="{ name: 'forum-detail', params: { forum_id: governance_forum.pk } }"
                    class="text-info">{{ governance_forum.name }}</router-link>
                <p id="forum-description" class="my-2"> {{ governance_forum.description }} of {{ group_name }}</p>
            </b-card>

            <b-card class="bg-white mb-3">
                <router-link class="text-info" :to="{ name: 'templates', params: {scope: 'community'}}">
                    Community Templates </router-link>
                <p id="community_templates_link" class="my-2">
                    Browse pre-existing governance setups and apply them to your community.</p>

            </b-card>

        </b-col>
        <b-col cols=9>
                <leadership-component v-if="selected_component=='leadership'"></leadership-component>

                <group-membership-component v-if="selected_component=='membership'"></group-membership-component>

                <role-component v-if="selected_component=='customroles'"></role-component>
        </b-col>
    </b-row>


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
            selected_component: "leadership"
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


<style scoped>

    .list-group-item a {
        color: #17a2b8;
    }

    .list-group-item.active {
        z-index: 2;
        color: #fff;
        background-color: #17a2b8;
        border-color: #17a2b8;
    }

    .list-group-item.active a {
        color: white;
    }

</style>