<template>

    <b-modal id="add_role_modal" title="Add a new role" hide-footer>

        <div class="input-group mb-3">
            <div class="input-group-prepend">
                <span class="input-group-text" id="role_name_prompt">Role Name</span>
            </div>
            <input type="text" class="form-control" aria-label="role_name"
                aria-describedby="role_name_prompt" v-model="new_role_name" name="role_name">
        </div>

        <error-component :message=error_message></error-component>

        <b-button size="sm" variant="success" @click="submitRoleName()" id="save_role_button">Save</b-button>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    store,
    components: { ErrorComponent },
    data: function() {
        return {
            error_message: '',
            new_role_name: '',
        }
    },
    computed: {
    ...Vuex.mapState({ roles: state => state.governance.roles }),
    },   // Gets existing roles from data store
    methods: {
        ...Vuex.mapActions(['addRole']),
        submitRoleName() {
            this.addRole({ role_name: this.new_role_name }).catch(error => {  this.error_message = error  })
        }
    }

}

</script>