<template>

    <div class="bg-white p-3" v-if="list">

        <h3>{{ list.name }}</h3>
        <p>{{ list.description }}</p>

        <form-button-and-modal v-if="user_permissions.edit_list" :id_add="'main'" :item_id=list_id
            :item_model="'list'" :button_text="'edit metadata'"></form-button-and-modal>

        <action-response-component :response=delete_list_response></action-response-component>
        <b-button v-if="user_permissions.delete_list" variant="outline-secondary" class="btn-sm mr-2"
            id="delete_list_button" @click="delete_list(list_id)">delete list</b-button>

        <router-link :to="{ name: 'action-history', params: {item_id: list_id, item_model: 'simplelist', item_name: list.name }}">
                <b-button variant="outline-secondary" class="btn-sm mr-2" id="list_history_button">
                    list history</b-button>
        </router-link>

        <b-button variant="outline-secondary" id="list_permissions" v-b-modal.item_permissions_modal
            class="btn-sm mr-2">list permissions</b-button>
        <item-permissions-modal :item_id=list_id :item_model="'simplelist'" :item_name=list.name>
        </item-permissions-modal>

        <b-button :href=csv_export_url variant="outline-secondary" class="btn-sm  mr-2" download>
            export as csv</b-button>

        <action-response-component :response=row_response class="mt-4"></action-response-component>

        <b-form inline id="table_controls" class="my-4">
            <b-button variant="info" class="btn-sm mr-2" v-if="user_permissions.add_column_to_list"
                id="add_column_button" @click="prep_modal('add', null)" v-b-modal.column_modal>new column</b-button>
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
                            <b-icon-check v-if="new_item" class="mx-1" id="submit_add_row"
                                @click="add_row"></b-icon-check>
                            <b-icon-check v-else class="mx-1" id="submit_edit_row"
                                @click="edit_row(data.item)"></b-icon-check>
                            <b-icon-x v-if="new_item" class="mx-1" id="discard_edit_row"
                                @click="edit_item = null; new_item = null"></b-icon-x>
                            <b-icon-x v-else class="mx-1" id="discard_edit_row" @click="edit_item = null">
                                </b-icon-x>
                        </span>
                        <span v-else>
                            <b-icon-pencil-square v-if="user_permissions.edit_row_in_list" class="mx-1"
                                @click="edit_item = data.item.unique_id" :id="'edit_row_' + data.index">
                            </b-icon-pencil-square>
                            <b-icon-trash v-if="user_permissions.delete_row_in_list" class="mx-1"
                                @click="delete_row(data.item)" :id="'delete_row_' + data.index">
                            </b-icon-trash>
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

        <column-modal-component :mode=mode :column_data=column_data :has_rows="list_data.length > 0" :list_id=list_id
            :can_add=user_permissions.add_column_to_list
            :can_edit=user_permissions.edit_column_in_list :can_delete=user_permissions.delete_column_from_list>
        </column-modal-component>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'
import ActionResponseComponent from '../actions/ActionResponseComponent'
import ColumnModalComponent from './ColumnModalComponent'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: { ItemPermissionsModal, ActionResponseComponent, ColumnModalComponent, FormButtonAndModal},
    props: ['list_id'],
    store,
    mixins: [UtilityMixin],
    data: function() {
            return {
                delete_list_response: null,
                row_response: null,
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
                    { edit_list: {alt_target : alt_target},
                        delete_list: {alt_target : alt_target},
                        add_row_to_list: {alt_target : alt_target},
                        edit_row_in_list: {alt_target : alt_target},
                        delete_row_in_list: {alt_target : alt_target},
                        add_column_to_list: {alt_target: alt_target},
                        edit_column_in_list: {alt_target: alt_target},
                        delete_column_from_list: {alt_target: alt_target}}
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
        delete_list(list_id) {
            this.deleteList({list_pk: list_id})
            .then(response => {
                if (response.data.action_status == "implemented") { this.$router.push({name: 'home'}) }
                else { this.delete_list_response = response }
            })
        },
        add_row() {
            var row_content = {}
            for (let field in this.list.columns) {
                row_content[field] = document.getElementById("new_row_" + field).value
            }
            this.addRow({list_pk: this.list_id, row_content: row_content})
            .then(response => {
                if (response.data.action_status == "implemented") { this.new_item = null; this.edit_item = null }
                this.row_response = response
            })
        },
        edit_row(item) {
            var row_content = {}
            for (let field in this.list.columns) {
                row_content[field] = document.getElementById(item.unique_id + "_" + field).value
            }
            this.editRow({list_pk: this.list_id, row_content: row_content, unique_id: item.unique_id})
            .then(response => {
                if (response.data.action_status == "implemented") { this.edit_item = null }
                this.row_response = response
            })
        },
        delete_row(item) {
            this.deleteRow({list_pk: this.list_id, unique_id: item.unique_id})
            .then(response => { this.row_response = response })
        }
    }

}

</script>

<style>
    .changecolumn {
        width: 100px;
    }
</style>