<template>

        <b-modal id="column_modal" :title=title size="md" @show="onShow">

            <!-- Data -->
            <b-input-group prepend="Column Name" class="my-2">
                <b-form-input name="columnName" v-model=column_name></b-form-input>
            </b-input-group>
            <b-input-group prepend="Default Value" class="my-2">
                <b-form-input name="defaultValue" v-model=column_default></b-form-input>
            </b-input-group>
            <b-form-checkbox id="required_checkbox" name="required_checkbox" class="popover-checkbox"
                v-model=column_required>Required</b-form-checkbox>

            <!-- Messages -->
            <span v-if="validation_error" class="text-danger">{{validation_error}}</span>
            <action-response-component :response=column_response class="mt-4"></action-response-component>

            <template #modal-footer>
            <!-- Actions -->
            <b-button v-if="can_add && mode == 'add'" variant="info" class="btn-sm mr-2 my-2" id='add_column_submit'
                @click='add_column'>Save</b-button>
            <b-button v-if="can_edit && mode == 'edit'" variant="info" class="btn-sm mr-2 my-2" id='edit_column_submit'
                @click='edit_column'>
                Save</b-button>
            <b-button variant="outline-secondary" class="btn-sm my-2" @click='reset_column'>Reset</b-button>
            <b-button v-if="can_delete && mode == 'edit'" variant="danger" class="float-right btn-sm my-2"
                id='delete_column_submit' @click='delete_column'>Delete</b-button>
            </template>

        </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ActionResponseComponent from '../actions/ActionResponseComponent'

export default {

    components: { ActionResponseComponent },
    props: ['list_id', 'column_data', 'can_add', 'can_edit', 'can_delete', 'mode', 'has_rows'],
    store,
    data: function() {
            return {
                validation_error: null,
                column_response: null,
                column_name: null,
                column_required: null,
                column_default: null
            }
        },
    computed: {
        title: function() { return this.mode.charAt(0).toUpperCase() + this.mode.slice(1) + " column"},
    },
    methods: {
        ...Vuex.mapActions(['addColumn', 'editColumn', 'deleteColumn']),
        onShow() { this.reset_column() },
        reset_column() {
            this.column_name = this.column_data.key
            this.column_default = this.column_data.default_value
            this.column_required = this.column_data.required
        },
        validate() {
            if (!this.column_name) {
                this.validation_error = "Column must have a name"
                return false
            }
            if (this.column_required && this.column_required != this.column_data.required) {
                if (this.column_default == "" && this.has_rows) {
                    if (this.mode == 'edit') {
                        this.validation_error = "When making a column required, you must supply a default value unless your list is empty"
                    }
                    if (this.mode == 'add') {
                        this.validation_error = "When adding a required column, you must supply a default value unless your list is empty"
                    }
                    return false
                }
            }
            return true
        },
        add_column() {
            if (this.validate() == false) { return }
            this.addColumn({list_pk: this.list_id, column_name: this.column_name, required: this.column_required,
                default_value: this.column_default})
            .then(response => { this.column_response = response })
        },
        edit_column() {
            if (this.validate() == false) { return }
            var params = {list_pk: this.list_id, required: this.column_required, default_value: this.column_default }
            if (this.column_name != this.column_data.key) {
                params["column_name"] = this.column_data.key
                params["new_name"] = this.column_name
            } else {
                params["column_name"] = this.column_name
            }
            this.editColumn(params).then(response => { this.column_response = response })
        },
        delete_column() {
            var name = this.column_name == this.column_data.key ? this.column_name : this.column_data.key
            this.deleteColumn({list_pk: this.list_id, column_name: name})
            .then(response => { this.column_response = response })
        }
    }
}

</script>
