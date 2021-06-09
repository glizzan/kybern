<template>

    <b-modal id="add_role_modal" title="Add a new role" hide-footer>

        <div class="input-group mb-3">
            <div class="input-group-prepend">
                <span class="input-group-text" id="role_name_prompt">Role Name</span>
            </div>
            <input type="text" class="form-control" aria-label="role_name"
                aria-describedby="role_name_prompt" v-model="new_role_name" name="role_name">
        </div>

        <take-action-component v-on:take-action=submitRoleName :response=response :verb="'add role'"
            :inline=true :action_name="'add_role_to_community'">
        </take-action-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import TakeActionComponent from '../actions/TakeActionComponent'

export default {

    store,
    components: { TakeActionComponent },
    data: function() {
        return {
            response: null,
            new_role_name: ''
        }
    },
    computed: {
        ...Vuex.mapState({ roles: state => state.governance.roles }),
    },
    methods: {
        ...Vuex.mapActions(['addRole']),
        submitRoleName(extra_data) {
            this.addRole({ role_name: this.new_role_name, extra_data: extra_data })
            .then(response => { this.response = response })
        }
    }

}

</script>