<template>

    <b-modal id="edit_group_modal" size="md" :visible=true @hide="$router.go(-1)">

        <template v-slot:modal-header><h5>Edit Your Group</h5></template>

        <b-form-group v-if=user_permissions.change_name id="name"
                                                label="Group name:" label-for="group_name">
            <b-form-input id="group_name" v-model="edited_group_name" required>
            </b-form-input>
        </b-form-group>
        <span v-else>{{ edited_group_name }}</span>

        <b-form-group v-if=user_permissions.change_description id="description"
                                label="Group description:" label-for="group_description">
            <b-form-textarea id="group_description" v-model="edited_group_description" required
                placeholder="Add a group description">
            </b-form-textarea>
        </b-form-group>
        <span v-else>{{ edited_group_description }}</span>

        <error-component :message=error_message></error-component>

        <template v-slot:modal-footer>
            <b-button variant="outline-secondary" class="btn-sm"  @click="save_edited_group">
                save</b-button>
            <router-link class="button" :to="{ name: 'home'}">
                <b-button variant="outline-secondary" class="btn-sm">close</b-button>
            </router-link>
        </template>

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
            item_model: 'group',
            edited_group_name: '',
            edited_group_description: '',
            error_message: ''
        }
    },
    created () {
        this.edited_group_name = this.group_name
        this.edited_group_description = this.group_description
        this.checkPermissions({
            permissions:
                {change_name_of_community: null, change_group_description: null},
            aliases:
                {change_name_of_community: "change_name", change_group_description: "change_description"}})
    },
    computed: {
        ...Vuex.mapState({
            group_name: state => state.group_name,
            group_description: state => state.group_description,
            user_permissions: state => state.permissions.current_user_permissions,
            item_id: state => state.group_pk })
    },
    methods: {
        ...Vuex.mapActions(['changeGroupName', 'changeGroupDescription', 'checkPermissions']),
        save_edited_group() {

            if (this.group_name != this.edited_group_name ) {
                this.changeGroupName({ group_pk: this.item_id, new_name: this.edited_group_name })
                .catch(error => { this.error_message = error })
            }

            if (this.group_description != this.edited_group_description) {
                this.changeGroupDescription({ group_pk: this.item_id,
                    group_description: this.edited_group_description })
                .catch(error => { this.error_message = error })
            }
        }
    }

}

</script>