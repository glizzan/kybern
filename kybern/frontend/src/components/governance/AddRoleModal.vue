<template>

    <b-modal id="add_role_modal" title="Add a new role" hide-footer>

        <div class="input-group mb-3">
            <div class="input-group-prepend">
                <span class="input-group-text" id="role_name_prompt">Role Name</span>
            </div>
            <input type="text" class="form-control" aria-label="role_name"
                aria-describedby="role_name_prompt" v-model="new_role_name" name="role_name">
        </div>

        <action-response-component :response=add_role_response></action-response-component>
        <b-button size="sm" variant="success" @click="submitRoleName()" id="save_role_button">
            Save</b-button>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ActionResponseComponent from '../actions/ActionResponseComponent'

export default {

    store,
    components: { ActionResponseComponent },
    data: function() {
        return {
            add_role_response: null,
            new_role_name: '',
        }
    },
    computed: {
        ...Vuex.mapState({ roles: state => state.governance.roles }),
    },
    methods: {
        ...Vuex.mapActions(['addRole']),
        submitRoleName() {
            this.addRole({ role_name: this.new_role_name })
            .then(response => { this.add_role_response = response })
        }
    }

}

</script>