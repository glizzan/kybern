<template>

    <div class="bg-white p-3">

        <h3>{{ list_name }}</h3>
        <p>{{ list_description }}</p>

        <router-link v-if="user_permissions.edit_list"
                :to="{ name: 'edit-list-info', params: { list_id: list_id } }">
            <b-button variant="outline-secondary" class="btn-sm mr-2" id="edit_list_button">
                edit list info</b-button>
        </router-link>

        <b-button v-if="user_permissions.delete_list" variant="outline-secondary" class="btn-sm mr-2"
            id="delete_list_button" @click="delete_list(list_id)">delete list</b-button>

        <router-link :to="{ name: 'action-history', params: {item_id: list_id, item_model: 'simplelist', item_name: list_name }}">
                <b-button variant="outline-secondary" class="btn-sm mr-2" id="list_history_button">
                    list history</b-button>
        </router-link>

        <b-button variant="outline-secondary" id="list_permissions" v-b-modal.item_permissions_modal
            class="btn-sm mr-2">list permissions</b-button>
        <item-permissions-modal :item_id=list_id :item_model="'simplelist'" :item_name=list_name>
        </item-permissions-modal>

        <b-button :href=csv_export_url variant="outline-secondary" class="btn-sm  mr-2" download>
            export as csv</b-button>

        <router-link v-if="user_permissions.add_row_to_list"
                    :to="{ name: 'add-list-row', params: { list_id: list_id, mode: 'create' } }">
                <b-button variant="outline-info" class="btn-sm" id="add_row_button">
                    add a row</b-button>
        </router-link>

        <error-component :message="error_message"></error-component>

        <hr >

        <b-table striped hover :items="list_data" :fields="list_fields">

                <template v-slot:cell(change)="data">

                    <b-form inline>

                        <router-link v-if="user_permissions.edit_row_in_list" :to="{ name: 'edit-list-row',
                            params: { list_id: list_id, mode: 'edit', row_index: data.item.index } }"
                            :id="'edit_row_' + data.item.index">
                            <b-button variant="outline-secondary" class="btn-sm mx-1">edit</b-button>
                        </router-link>

                        <b-button v-if="user_permissions.delete_row_in_list" variant="outline-secondary"
                            class="btn-sm mx-1" @click="delete_row(data.item)" :id="'delete_row_' + data.item.index">
                        delete</b-button>

                        <b-button v-if="user_permissions.move_row_in_list" variant="outline-secondary"
                            class="btn-sm mx-1" v-b-modal.move_row_modal @click="old_index=data.item.index"
                            :id="'move_row_' + data.item.index">
                        move</b-button>

                    </b-form>

                </template>

        </b-table>

        <span v-if="Object.keys(rows).length === 0">There are no items yet in this list.</span>

        <b-modal id="move_row_modal" title="Move Row" size="sm" :visible=false hide-footer>

            Current row index: {{ old_index }}

            <b-input-group prepend="New index" class="sm my-2 mx-1">
                <b-form-input v-model="new_index" type="number" min="0" :max="list_data.length - 1"></b-form-input>
            </b-input-group>

            <b-button variant="outline-secondary" class="btn-sm my-2" id="move_row_save_button"
                @click="move_row()">save</b-button>

            <error-component :message=move_error_message></error-component>

        </b-modal>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ErrorComponent from '../utils/ErrorComponent'
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'


export default {

    components: { ErrorComponent, ItemPermissionsModal },
    props: ['list_id'],
    store,
    mixins: [UtilityMixin],
    data: function() {
            return {
                error_message: "",
                move_error_message: "",
                old_index: null,
                new_index: null,
                base_export_url: ""
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
                        move_row_in_list: {alt_target : alt_target},
                        delete_row_in_list: {alt_target : alt_target}}
            }).catch(error => { this.error_message = error; })
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
        rows: function() {
            if (this.lists_loaded) { return this.getListData(this.list_id).rows } else { return [] }},
        configuration: function() {
            if (this.lists_loaded) { return this.getListData(this.list_id).configuration } else { return {} }},
        list_name: function() {
            if (this.lists_loaded) { return this.getListData(this.list_id).name } else { return "" }},
        list_description: function() {
            if (this.lists_loaded) { return this.getListData(this.list_id).description }
            else { return undefined }},
        list_fields: function() {
            var list_fields = [{ key: 'index', sortable: true }]
            if (this.lists_loaded) {
                for (let field in this.configuration) {
                    list_fields.push({key: field, sortable: true})
                }
            }
            list_fields.push('change')
            return list_fields
        },
        list_data: function() {
            var list_data = []
            var index = 0
            for (let row in this.rows) {
                var row_dict = {}
                for (let field in this.rows[row]) {
                    row_dict[field] = this.rows[row][field]
                }
                row_dict["index"] = index
                list_data.push(row_dict)
                index++
            }
            return list_data
        },
        csv_export_url: function() {
            return this.base_export_url + "?item_id=" + this.list_id + "&item_model=simplelist"
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getLists', 'deleteList', 'moveRow', 'deleteRow']),
        display_date(date) { return Date(date) },
        delete_list(list_id) {
            this.deleteList({list_pk: list_id})
            .then(response => { this.$router.push({name: 'home'}) })
            .catch(error => {  this.error_message = error })
        },
        delete_row(item) {
            this.deleteRow({list_pk: this.list_id, index:item.index})
            .catch(error => {  this.error_message = error })
        },
        move_row() {
            this.new_index = parseInt(this.new_index)
            if (this.old_index == this.new_index) {
                this.move_error_message = "Must specify different index"
                return
            }
            if (this.new_index > this.list_data.length-1) {
                this.move_error_message = "New index is too high"
                return
            }
            this.moveRow({list_pk: this.list_id, old_index: this.old_index, new_index: this.new_index})
            .then(response => { this.old_index = null; this.new_index = null; this.$bvModal.hide("move_row_modal") })
            .catch(error => {  this.move_error_message = error })
        }
    }

}

</script>