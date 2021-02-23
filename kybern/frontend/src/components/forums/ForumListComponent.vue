<template>

    <span>

        <h4 class="text-secondary pb-3">Forums
            <router-link :to="{ name: 'add-new-forum'}">
                <b-button v-if="user_permissions.add_forum" variant="outline-secondary"
                    class="btn-sm ml-3" id="new_forum_button">+ add new</b-button>
            </router-link>
        </h4>

        <b-card v-if=governance_forum class="bg-light text-info border-secondary mb-3">
            <router-link :to="{ name: 'forum-detail', params: {forum_id: governance_forum.pk}}">
                <b-card-title class="forum-link">{{ governance_forum.name }}<b-icon-star-fill class="ml-2">
                </b-icon-star-fill></b-card-title>
            </router-link>
            <p class="mb-1 text-secondary forum-description">  {{ governance_forum.description }}</p>
        </b-card>

        <span v-for="{ pk, name, description } in regular_forums" v-bind:key=pk>
            <b-card class="bg-light text-info border-secondary mb-3">
                <router-link :to="{ name: 'forum-detail', params: { forum_id: pk } }">
                    <b-card-title class="forum-link">{{ name }}</b-card-title></router-link>
                <p class="mb-1 text-secondary forum-description">  {{ description }}  </p>
            </b-card>
        </span>

        <span v-if="Object.keys(forums).length === 0">You do not have any forums yet.</span>

    </span>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    store,
    computed: {
        ...Vuex.mapState({
            forums: state => state.forums.forums,
            user_permissions: state => state.permissions.current_user_permissions,
            group_name: state => state.group_name
        }),
        regular_forums: function() {
            var regular_forums = []
            for (let index in this.forums) {
                if (this.forums[index].special != "Gov") { regular_forums.push(this.forums[index]) }
            }
            return regular_forums
        },
        governance_forum: function() {
            for (let index in this.forums) {
                if (this.forums[index].special == "Gov") { return this.forums[index] }
            }
            return null
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