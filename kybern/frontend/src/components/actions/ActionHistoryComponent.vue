<template>

  <div class="bg-white p-3 rounded">

    <b-container fluid id="action_history_table">
      <b-row align-h="end" class="my-2">

        <!-- Quick Filter Buttons -->
        <b-col lg="7" class="my-4">
        <b-button-group>
            <b-button :variant="get_variant('open')" @click="setFilter('open')">Open proposals</b-button>
            <b-button :variant="get_variant('waiting')" @click="setFilter('waiting')">Waiting on decisions</b-button>
            <b-button :variant="get_variant('governing')" @click="setFilter('governing')">Governing actions</b-button>
            <b-button :variant="get_variant('yours')" @click="setFilter('yours')">Your actions</b-button>
        </b-button-group>
        </b-col>

        <b-col lg="5" class="my-4">
            <b-form-group>
            <b-input-group size="sm">
                <b-form-input v-model="filterObject.filter_text" type="search" id="filterInput"
                    placeholder="Type to Search"></b-form-input>
            </b-input-group>
            </b-form-group>
        </b-col>

        </b-row>

          <b-table hover :items="item_actions" :fields="action_fields"
              :sort-by.sync="sortBy" :sort-desc.sync="sortDesc" :filter=filterObject :filter-function=filterFunction
              id="action_history_table_element" responsive>

          <template v-slot:cell(actor)="data">
            <router-link :to="{ name: 'user-permissions', params: { user_pk: data.item.actor_pk }}"
                class="font-weight-bold text-info">{{ data.item.actor}}
            </router-link>
          </template>

          <template v-slot:cell(action)="data">
              {{ data.item.description }}
              <b-badge v-if="data.item.is_template" variant="warning" class="ml-2">template action</b-badge>
          </template>

          <template v-slot:cell(date)="data">
              {{ data.item.display_date }}
          </template>

          <template v-slot:cell(status)="data">
              <span v-if="data.item.status == 'propose-req'">proposed </span>
              <span v-if="data.item.status == 'propose-vol'">proposed (voluntary)</span>
              <span v-if="data.item.status != 'propose-req' && data.item.status != 'propose-vol'">
                  {{ data.item.status }}</span>
              <b-badge v-if="data.item.has_condition.exists" variant="info" class="ml-2">has condition</b-badge>
          </template>

          <template v-slot:cell(more)="data">
            <router-link :to="{ name: 'action-detail', params: { action_id: data.item.action_pk }}">
                <b-button variant="outline-secondary" class="btn-sm ml-2 action-link-button">see more</b-button>
            </router-link>
          </template>

        </b-table>

    </b-container>

  </div>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import { ReplacePKsWithUsernamesMixin } from '../utils/Mixins'


export default {

    props: ['item_id', 'item_model', 'item_name'],
    store,
    mixins: [ReplacePKsWithUsernamesMixin],
    data: function() {
          return {
            action_fields: [
                { key: 'actor', label: "Actor", sortable: true },
                { key: 'description', label: "Action", sortable: true },
                { key: 'display_date', label: "When", sortable: true },
                { key: 'status', label: "Status", sortable: true },
                { key: 'more', label: "More Info", sortable: false }

            ],
            sortBy: 'created',
            sortDesc: true,
            filterObject: { filter_text: null, filter_function: null },
            filterOn: [],
            processed_item_actions: []
          }
    },
    created: function () {
      this.loadActions({ item_id: this.final_item_id, item_model: this.final_item_model })
        .then(response => this.processed_item_actions = this.replace_pks_with_usernames(this.actions[this.item_key]) )
        .catch(error => {  console.log(error) })
    },
    watch: {
        item_actions: function(val) {
            this.processed_item_actions = this.replace_pks_with_usernames(val)
        }
    },
    computed: {
      ...Vuex.mapGetters(['getUserName']),
      ...Vuex.mapState({
          actions: state => state.concord_actions.actions,
          user_pk: state => state.user_pk
        }),
      final_item_id: function() {
        return (typeof this.item_id === "undefined") ? store.state.group_pk : this.item_id },
      final_item_model: function() {
        return (typeof this.item_model === "undefined") ? 'group' : this.item_model },
      final_item_name: function() {
        return (typeof this.item_name === "undefined") ? store.state.group_name : this.item_name },
      item_key: function() {
          return this.final_item_id + "_" + this.final_item_model
      },
      item_actions: function() {
        if (this.actions[this.item_key]) { return this.actions[this.item_key] } else { return [] }
      },
      modal_id: function() {
        return "action_history_modal_" + this.final_item_id + "_" + this.final_item_model
      }
    },
    methods: {
      ...Vuex.mapActions(['loadActions']),
      get_variant(filter_name) {
          if (this.filterObject.filter_function == filter_name) { return "secondary" } else { return "outline-secondary" }
      },
      setFilter(filter_name) {
          if (this.filterObject.filter_function == filter_name ) {
              this.filterObject.filter_function = null
            }
          else { this.filterObject.filter_function = filter_name }
      },
      filter_item(item) {
          if (this.filterObject.filter_function == "open") {
              return item.status == "propose-req" || item.status == "propose-vol"
          }
          if (this.filterObject.filter_function == "waiting") {
              return item.has_condition.exists && item.status == "waiting"
          }
          if (this.filterObject.filter_function == "governing") {
              return item.resolution_passed_by == "governing"
          }
          if (this.filterObject.filter_function == "yours") {
              return item.actor_pk == this.user_pk
          }
      },
      filterFunction(item, filterObject) {

        // passed_text is true if the text is found in the item or if there is no filter_text specified
        var passed_text = filterObject.filter_text ? JSON.stringify(item).includes(filterObject.filter_text) : true

        // passed_function is true if it passes the specified function or if there is no function set
        var passed_function = filterObject.filter_function ? this.filter_item(item) : true

        return passed_text && passed_function
      }
    }

}

</script>
