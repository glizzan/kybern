<template>

    <b-modal id="list_modal" :title="title_string" size="md" :visible=true hide-footer @hide="$router.go(-1)">

        <b-form-group v-if="mode=='create'" id="index_form_group">
            Index to add row at: <b> {{ index }} </b>
            <b-form-input id="index" v-model="index" type="range" min="0" :max="row_length">
            </b-form-input>
        </b-form-group>
        <span class="mb-3" v-else>
            You are editing the item at index: {{ index }}.
        </span>

        <span class="my-3">
            <b-form-group v-for="column in columns" :label=column.name :label-for=column.name v-bind:key=column.name>
                <b-form-input :id=column.name :name=column.name v-model=column.current_value></b-form-input>
                <b-form-text>
                    <span v-if=is_column_required(column)>You must fill out a value for this column.</span>
                    <span v-if=column.default_value>The default value for this column is
                        {{ column.default_value }}.</span>
                </b-form-text>
            </b-form-group>
        </span>

        <action-response-component :response=row_response></action-response-component>
        <b-button v-if="mode=='create'" variant="outline-secondary" class="btn-sm" id="add_row_save_button"
            @click="add_row">submit</b-button>
        <b-button v-if="mode=='edit'" variant="outline-secondary" class="btn-sm" id="edit_row_save_button"
            @click="edit_row">submit</b-button>

        <error-component :message=error_message></error-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    props: ['list_id', 'row_index', 'mode'],
    components: { ErrorComponent, ActionResponseComponent },
    store,
    data: function() {
        return {
            index: null,
            columns: [],
            row_length: 0,
            error_message: null,
            row_response: null
        }
    },
    created () {
        if (this.lists_loaded) { this.get_initial_data() }
        else { this.getLists().then(response => { this.get_initial_data() }) }
    },
    computed: {
        ...Vuex.mapState({ lists: state => state.simplelists.lists }),
        ...Vuex.mapGetters(['getListData']),
        lists_loaded: function() { if (this.lists.length == 0) { return false } else { return true }},
        title_string: function() {
            if (this.mode == 'edit') {  return "Edit row '" + this.row_index + "'" }
            else { return "Add a new row" }
        }
    },
    methods: {
        ...Vuex.mapActions(['getLists', 'addRow', 'editRow']),
        get_initial_data() {
            var list = this.getListData(this.list_id)
            this.row_length = list.rows.length
            if (this.mode == 'edit') { this.index = this.row_index } else { this.index = 0 }
            var row_data = (this.mode == 'edit') ? list.rows[this.index] : null
            this.columns = this.initialize_columns(list.configuration, row_data)
        },
        initialize_columns(configuration, row_data){
            var columns = []
            for (let col_name in configuration){
                var params =configuration[col_name]
                var current_value = row_data ? row_data[col_name] : ""
                columns.push({name: col_name, required: params.required,
                    default_value: params.default_value, current_value: current_value })
            }
            return columns
        },
        add_row() {
            this.addRow({list_pk:this.list_id, index:parseInt(this.index), row_content: this.format_row_content()})
            .then(response => { this.row_response = response })
        },
        edit_row() {
            this.editRow({list_pk:this.list_id, index:parseInt(this.index), row_content: this.format_row_content()})
            .then(response => { this.row_response = response })
        },
        format_row_content() {
            var column_data = {}
            for (let index in this.columns) {
                var column = this.columns[index]
                column_data[column.name] = document.getElementById(column.name).value
            }
            return column_data
        },
        is_column_required(column){
            if (column.required && column.default_value == "") { return true } else { return false }
        }
    }

}

</script>