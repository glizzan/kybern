<template>

        <b-modal id="column_modal" :title=title size="md" @show="onShow" @close="clear">

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

            <!-- Actions -->
            <template #modal-footer>
                <take-action-component v-if="mode == 'add'" v-on:take-action=add_column :response=add_response
                    :inline="'true'" :verb="'add column'" :action_name="'add_column_to_list'" :alt_target=alt_target>
                </take-action-component>
                <take-action-component v-if="mode == 'edit' && not_deleted" v-on:take-action=edit_column :response=edit_response
                    :inline="'true'" :verb="'edit column'" :action_name="'edit_column_in_list'" :alt_target=alt_target>
                </take-action-component>
                <take-action-component v-if="mode == 'edit'" v-on:take-action=delete_column :response=delete_response
                    :inline="'true'" :verb="'delete column'" :action_name="'delete_column_from_list'" :alt_target=alt_target>
                </take-action-component>
            </template>

        </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    components: { TakeActionComponent },
    props: ['alt_target', 'column_data', 'mode', 'has_rows'],
    store,
    data: function() {
            return {
                validation_error: null,
                add_response: null,
                edit_response: null,
                delete_response: null,
                column_name: null,
                column_required: null,
                column_default: null,
                not_deleted: true
            }
        },
    computed: {
        title: function() { return this.mode.charAt(0).toUpperCase() + this.mode.slice(1) + " column"},
    },
    methods: {
        ...Vuex.mapActions(['addColumn', 'editColumn', 'deleteColumn']),
        onShow() { this.reset_column() },
        clear() { this.validation_error = null; this.add_response = null; this.edit_response = null, this.delete_response = null },
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
        add_column(extra_data) {
            if (this.validate() == false) { return }
            this.addColumn({alt_target: this.alt_target, column_name: this.column_name, required: this.column_required,
                default_value: this.column_default, extra_data: extra_data})
            .then(response => { this.add_response = response })
        },
        edit_column(extra_data) {
            if (this.validate() == false) { return }
            var params = {alt_target: this.alt_target, required: this.column_required, default_value: this.column_default, extra_data: extra_data }
            if (this.column_name != this.column_data.key) {
                params["column_name"] = this.column_data.key
                params["new_name"] = this.column_name
            } else {
                params["column_name"] = this.column_name
            }
            this.editColumn(params).then(response => { this.edit_response = response })
        },
        delete_column(extra_data) {
            var name = this.column_name == this.column_data.key ? this.column_name : this.column_data.key
            this.deleteColumn({alt_target: this.alt_target, column_name: name, extra_data: extra_data})
            .then(response => { this.delete_response = response })
        }
    }
}

</script>
