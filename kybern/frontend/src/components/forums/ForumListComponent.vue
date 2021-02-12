<template>

    <span>

        <h4 class="text-secondary pb-3">{{ group_name }}'s Forums
            <router-link :to="{ name: 'add-new-forum'}">
                <b-button v-if="user_permissions.add_forum" variant="outline-secondary"
                    class="btn-sm ml-3" id="new_forum_button">+ add new</b-button>
            </router-link>
        </h4>

        <governance-forum-link-component :forum=governance_forum :star=true>
        </governance-forum-link-component>

        <router-link v-for="{ pk, name, description } in regular_forums" v-bind:key=pk
                                :to="{ name: 'forum-detail', params: { forum_id: pk } }">
            <b-card :title=name v-bind:key=pk class="bg-light text-info border-secondary mb-3">
                <p class="mb-1 text-secondary forum-description">  {{ description }}  </p>
            </b-card>
        </router-link>

        <span v-if="Object.keys(forums).length === 0">You do not have any forums yet.</span>

    </span>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import GovernanceForumLinkComponent from '../forums/GovernanceForumLinkComponent'


export default {

    store,
    components: { GovernanceForumLinkComponent },
    data: function() {
        return {
            governance_forum: null
        }
    },
    computed: {
        ...Vuex.mapState({
            forums: state => state.forums.forums,
            user_permissions: state => state.permissions.current_user_permissions,
            group_name: state => state.group_name
        }),
        regular_forums: function() {
            var regular_forums = []
            for (let index in this.forums) {
                if (this.forums[index].special == "Gov") {
                    this.governance_forum = this.forums[index]
                } else {
                    regular_forums.push(this.forums[index])
                }
            }
            return regular_forums
        }
    },
    created () {
        this.checkPermissions({permissions: {"add_forum": null}})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions'])
    }

}

</script>