<template>

    <div class="bg-white p-3" v-if="list">

        <div class="title-and-actions mb-4">

            <span class="h3 font-weight-bold">{{ list.name }}</span>

            <resource-action-icons class="float-right" v-on:delete="delete_list" :response=list_response :item_id=list_id
                :item_model="'list'" :item_name=list.name :export_url=csv_export_url :export_text="'export as csv'">
                </resource-action-icons>

        </div>

        <p>{{ list.description }}</p>

        <b-form inline id="table_controls" class="my-4">
            <b-button variant="info" class="btn-sm mr-2" id="add_column_button" @click="prep_modal('add', null)"
                v-b-modal.column_modal>new column</b-button>
            <b-button variant="info" class="btn-sm mr-2" v-if="user_permissions.add_row_to_list"
                id="add_row_button" @click="new_item = true; edit_item = 'new_row'">new row</b-button>
            <b-input-group size="sm">
                <b-form-input id="filter-input" v-model="filter" type="search" placeholder="Type to Search">
                    </b-form-input>
                <b-input-group-append><b-button :disabled="!filter" @click="filter = ''">Clear</b-button>
                    </b-input-group-append>
            </b-input-group>
        </b-form>

        <b-table striped hover :items="list_data" :fields="list_fields" class="mt-2" :filter=filter>

                <!-- Display controls column -->
                <template v-slot:cell(controls)="data">

                    <b-form inline>

                        <span v-if="edit_item == data.item.unique_id">
                            <span v-if="new_item">
                                <take-action-component v-on:take-action="add_row" v-on:close-modal="modal_closed('add')"
                                    :response=add_row_response :alt_target=alt_target :verb="'add row to list'">
                                    <b-icon-check class="mx-1" id="submit_add_row"></b-icon-check>
                                </take-action-component>
                                <b-icon-x class="mx-1" id="discard_edit_row" @click="edit_item = null; new_item = null"></b-icon-x>
                            </span>
                            <span v-else>
                                <take-action-component v-on:take-action="edit_row(data.item, $event)" :response=edit_row_response
                                    v-on:close-modal="modal_closed('edit')" :alt_target=alt_target :verb="'edit row in list'">
                                    <b-icon-check class="mx-1" id="submit_edit_row"></b-icon-check>
                                </take-action-component>
                                <b-icon-x class="mx-1" id="discard_edit_row" @click="edit_item = null"></b-icon-x>
                            </span>
                        </span>

                        <span v-else>
                            <b-icon-pencil-square class="mx-1" @click="edit_item = data.item.unique_id"
                                :id="'edit_row_' + data.index"></b-icon-pencil-square>
                            <take-action-component v-on:take-action="delete_row(data.item, $event)" :alt_target=alt_target
                                v-on:close-modal="modal_closed('delete')" :response=delete_row_response
                                :verb="'delete row in list'" :unique=data.index>
                                <b-icon-trash class="mx-1" :id="'delete_row_' + data.index"></b-icon-trash>
                            </take-action-component>
                        </span>

                    </b-form>

                </template>

                <!-- Default display for cell, displays in edit mode if row is selected-->
                <template v-slot:cell()="data">
                    <b-form-input v-if="edit_item == data.item.unique_id" :id="data.item.unique_id + '_' + data.field.key"
                        :name="'edit_' + data.field.key" :value="data.value"></b-form-input>
                    <span v-else>{{data.value}}</span>
                </template>

                <!-- Display column headers -->
                <template #head()="data">

                    <span v-if="data.label != 'Controls'">
                        <span v-on:click.stop="prep_modal('edit', data.field)" :id="'edit_column_' + data.label"
                            v-b-modal.column_modal>
                            {{ data.label }}
                            <b-icon-asterisk v-if="data.field.required" scale="0.5" shift-v="5"></b-icon-asterisk>
                            <b-icon-textarea-t v-if="data.field.default_value" scale="0.5" shift-v="5"></b-icon-textarea-t>
                        </span>

                    </span>
                    <span v-else></span>  <!-- Don't display 'Controls' title -->

                </template>

        </b-table>

        <span v-if="Object.keys(list.rows).length === 0">There are no items yet in this list.</span>

        <column-modal-component :mode=mode :column_data=column_data :has_rows="list_data.length > 0" :alt_target=alt_target>
        </column-modal-component>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ColumnModalComponent from './ColumnModalComponent'
import ResourceActionIcons from '../utils/ResourceActionIcons'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    components: { TakeActionComponent, ColumnModalComponent, ResourceActionIcons },
    props: ['list_id'],
    store,
    mixins: [UtilityMixin],
    data: function() {
            return {
                list_response: null,
                add_row_response: null,
                edit_row_response: null,
                delete_row_response: null,
                base_export_url: "",
                edit_item: null,
                new_item: null,
                filter: null,
                mode: "add",
                column_data: null
            }
        },
    created (){
        if (!this.lists_loaded) {  this.getLists()  }
        if (this.list_id) {
            var alt_target = "simplelist_" + this.list_id
            this.checkPermissions({
                permissions:
                    {
                        add_row_to_list: {alt_target : alt_target},
                        edit_row_in_list: {alt_target : alt_target},
                        delete_row_in_list: {alt_target : alt_target}}
            }).catch(error => { console.log(error) })
        } else {
            console.log("Missing list_id in SimpleListComponent")
        }
        this.url_lookup('export_as_csv').then(response => this.base_export_url = response)
    },
    computed: {
        ...Vuex.mapState({
            lists: state => state.simplelists.lists,
            user_permissions: state => state.permissions.current_user_permissions
        }),
        ...Vuex.mapGetters(['getListData', 'getUserName', 'url_lookup']),
        alt_target: function() { return "simplelist_" + this.list_id },
        lists_loaded: function() { if (this.lists.length == 0) { return false } else { return true }},
        list: function() { if (this.lists_loaded) { return this.getListData(this.list_id) } else { return null }},
        list_fields: function() {
            var list_fields = [{controls: {class: 'changecolumn', sortable: false}}]
            for (let field in this.list.columns) {
                list_fields.push({key: field, sortable: true, required: this.list.columns[field].required,
                                    default_value: this.list.columns[field].default_value})
            }
            return list_fields
        },
        list_data: function() {
            var list_data = []
            if (this.new_item) {
                var new_row_data = {unique_id: "new_row"}
                for (let field in this.list.columns) { new_row_data[field] = "" }
                list_data.push(new_row_data)
            }
            for (let row in this.list.rows) {
                var row_dict = {unique_id: row}
                for (let field in this.list.rows[row]) {
                    row_dict[field] = this.list.rows[row][field]
                }
                list_data.push(row_dict)
            }
            return list_data
        },
        csv_export_url: function() {
            return this.base_export_url + "?item_id=" + this.list_id + "&item_model=simplelist"
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getLists', 'deleteList', 'addRow', 'editRow', 'deleteRow']),
        display_date(date) { return Date(date) },
        prep_modal(mode, data) {
            this.mode = mode
            this.column_data = data ? data : { key: "", required: false, default_value: "" }
        },
        modal_closed(mode) {
            if (mode == "edit") { this.edit_item = null }
            if (mode == "add") { this.new_item = null; this.edit_item = null }
            this.add_row_response = null
            this.edit_row_response = null
            this.delete_row_response = null
        },
        delete_list(extra_data) {
            this.deleteList({pk: this.list_id, extra_data: extra_data })
            .then(response => {
                if (response.data.action_status == "implemented") { this.$router.push({name: 'home'}) }
                else { this.list_response = response }
            })
        },
        add_row(extra_data) {
            var row_content = {}
            for (let field in this.list.columns) {
                row_content[field] = document.getElementById("new_row_" + field).value
            }
            this.addRow({list_pk: this.list_id, row_content: row_content, extra_data: extra_data })
            .then(response => { this.add_row_response = response })
        },
        edit_row(item, extra_data) {
            var row_content = {}
            for (let field in this.list.columns) {
                row_content[field] = document.getElementById(item.unique_id + "_" + field).value
            }
            this.editRow({list_pk: this.list_id, row_content: row_content, unique_id: item.unique_id, extra_data: extra_data})
            .then(response => { this.edit_row_response = response })
        },
        delete_row(item, extra_data) {
            this.deleteRow({list_pk: this.list_id, unique_id: item.unique_id, extra_data: extra_data})
            .then(response => { this.delete_row_response = response })
        }
    }

}

</script>

<style>
    .changecolumn {
        width: 100px;
    }
</style>