<template>

    <b-modal id="list_modal" :title="title_string" size="lg" :visible=true hide-footer @hide="$router.go(-1)">

        <b-form-group id="name_form_group" label="List name:" label-for="list_name">
            <b-form-input id="list_name" name="list_name" v-model="name" required placeholder="Please pick a name">
            </b-form-input>
        </b-form-group>

        <b-form-group id="description_form_group" label="List description:" label-for="list_description">
            <b-form-textarea id="list_description" name="list_description" v-model="description" placeholder="Add a description">
            </b-form-textarea>
        </b-form-group>

        <span id="list_columns" class="my-4">

            <b-table-lite striped :items="columns" caption-top>
                <template v-slot:table-caption>Existing columns</template>
                <template v-slot:cell(delete)="data"><b-button :id="'delete_column_' + data.item.name"
                    @click='delete_column(data.item)'>delete</b-button></template>
            </b-table-lite>

            <error-component :message=column_error_message :dismissable=true></error-component>

            <p class="my-2">Add a new column:</p>

            <b-form inline>
                <b-form-input id="column_name" name="column_name" v-model="column_name"
                    placeholder="column name" required class="mr-2"></b-form-input>
                <b-form-input id="column_default" name="column_default" v-model="column_default"
                    placeholder="default value" class="mr-2"></b-form-input>
                <input type="checkbox" id="column_required" name="column_required"
                    v-model="column_required" class="mr-2"> required </input>
                <b-button variant="info" class="btn-sm ml-2" id="add_new_col_button"
                    @click="add_column()">add</b-button>
            </b-form>

        </span>

        <b-button v-if=!list_id variant="outline-secondary" class="btn-sm mt-4" id="add_list_button"
            @click="add_list">submit</b-button>
        <b-button v-if=list_id variant="outline-secondary" class="btn-sm mt-4" id="edit_list_save_button"
            @click="edit_list">submit</b-button>

        <error-component :message=error_message></error-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['list_id'],
    components: { ErrorComponent },
    store,
    data: function() {
        return {
            name: null,
            description: null,
            error_message: null,
            list_loaded: false,
            columns: [],
            column_name: "",
            column_required: false,
            column_default: "",
            column_error_message: null
        }
    },
    created () {
        if (this.list_id && !this.lists_loaded) { this.getLists() }
        this.populate_columns()
    },
    watch: {
        lists_loaded: function(val) { this.populate_columns() }
    },
    computed: {
        ...Vuex.mapState({ lists: state => state.simplelists.lists }),
        ...Vuex.mapGetters(['getListData']),
        title_string: function() {
            if (this.list_id) {  return "Edit list '" + this.name + "'" }
            else { return "Add a new list" }
        },
        lists_loaded: function() { if (this.lists.length == 0) { return false } else { return true } }
    },
    methods: {
        ...Vuex.mapActions(['getLists', 'addList', 'editList']),
        add_list() {
            this.addList({ name: this.name, description: this.description,
                configuration: this.reformat_columns_for_backend(this.columns)})
            .then(response => {
                this.$router.push({name: 'home'}) })
            .catch(error => {  console.log(error), this.error_message = error })
        },
        edit_list() {
            this.editList({ list_pk: parseInt(this.list_id), name: this.name, description: this.description,
                configuration: this.reformat_columns_for_backend(this.columns) })
            .then(response => {
                this.$router.push({name: 'list-detail', params: {list_id: this.list_id}}) })
            .catch(error => {  this.error_message = error })
        },
        populate_columns() {
            if (this.list_id) {
                if (this.lists_loaded) {
                    var list = this.getListData(this.list_id)
                    this.name = list.name
                    this.description = list.description
                    this.columns = this.reformat_columns(list.configuration)
                }
            } else {
                this.columns = this.reformat_columns({"content": {}})
            }
        },
        reformat_columns(input) {
            var columns = []
            for (let column in input) {
                var required = input[column].required ? input[column].required : false
                var default_value = input[column].default_value ? input[column].default_value : ""
                columns.push({name: column, required: required, default_value: default_value, delete: null})
            }
            return columns
        },
        reformat_columns_for_backend(columns) {
            var configuration = {}
            for (let index in columns) {
                var column = columns[index]
                configuration[column.name]= { required: column.required, default_value: column.default_value }
            }
            return configuration
        },
        add_column() {
            if (!this.column_name) {
                this.column_error_message = "New column must have a name"
                return
            }
            var existing_column = this.columns.find(column => column.name == this.column_name)
            if (existing_column) {
                this.column_error_message = "Columns must have unique names"
                return
            }
            if (this.list_id && this.column_required && this.column_default == "") {
                this.column_error_message = "If column is required, must supply default value"
                return
            }
            this.columns.push({name: this.column_name, required: this.column_required,
                default_value: this.column_default, delete: null})
        },
        delete_column(column_to_delete) {
            if (this.columns.length == 1) {
                this.column_error_message = "Must have at least one column"
            } else {
                var index = 0
                for (let column in this.columns) {
                    if (this.columns[column].name == column_to_delete.name) {
                        this.columns.splice(index, 1)
                    }
                    index++
                }
            }
        }
    }

}

</script>