<template>

  <div class="bg-white p-3 rounded">

    <b-container fluid id="action_history_table">
      <b-row align-h="end" class="my-2">

          <b-col lg="6" class="my-4">
              <b-form-group label="Filter" label-cols-sm="3" label-align-sm="left" label-size="sm"
                                                              label-for="filterInput" class="mb-0">
                <b-input-group size="sm">
                  <b-form-input v-model="filter" type="search" id="filterInput"
                                        placeholder="Type to Search"></b-form-input>
                </b-input-group>
              </b-form-group>
          </b-col>

        </b-row>

          <b-table hover :items="item_actions" :fields="action_fields"
              :sort-by.sync="sortBy" :sort-desc.sync="sortDesc" :filter="filter"
              :filterIncludedFields="filterOn" id="action_history_table_element" responsive>

          <template v-slot:cell(actor)="data">
            <router-link :to="{ name: 'user-permissions', params: { user_pk: data.item.actor_pk }}"
                class="font-weight-bold text-info">{{ data.item.actor}}
            </router-link>
          </template>

          <template v-slot:cell(action)="data">
              {{ data.item.description}}
          </template>

          <template v-slot:cell(date)="data">
              {{ data.item.display_date }}
          </template>

          <template v-slot:cell(status)="data">
              {{ data.item.status }}
          </template>

          <template v-slot:cell(more)="data">
            <router-link :to="{ name: 'action-detail', params: { action_id: data.item.action_pk }}">
                <b-button variant="outline-secondary" class="btn-sm ml-2 action-link-button">see more</b-button>
            </router-link>
            <b-badge v-if="data.item.has_condition.exists" variant="info" class="ml=2">has condition</b-badge>
            <b-badge v-if="data.item.is_template" variant="warning" class="ml=2">template action</b-badge>
          </template>

        </b-table>

    </b-container>

  </div>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    props: ['item_id', 'item_model', 'item_name'],
    store,
    data: function() {
          return {
            action_fields: [
                { key: 'actor', label: "Actor", sortable: true },
                { key: 'action', label: "Action", sortable: true },
                { key: 'date', label: "When", sortable: true },
                { key: 'status', label: "Status", sortable: true },
                { key: 'more', label: "More Info", sortable: true }

            ],
            sortBy: 'created',
            sortDesc: true,
            sortOptions: [
              { text: "Date created", value: "created" },
              { text: "Status", value: "status" },
              { text: "Actor", value: "actor" },
            ],
            filter: null,
            filterOn: []
          }
    },
    created: function () {
      this.loadActions({ item_id: this.final_item_id, item_model: this.final_item_model })
        .catch(error => {  console.log(error) })
    },
    computed: {
      ...Vuex.mapState({ actions: state => state.concord_actions.actions }),
      final_item_id: function() {
        return (typeof this.item_id === "undefined") ? store.state.group_pk : this.item_id },
      final_item_model: function() {
        return (typeof this.item_model === "undefined") ? 'group' : this.item_model },
      final_item_name: function() {
        return (typeof this.item_name === "undefined") ? store.state.group_name : this.item_name },
      item_actions: function() {
        var item_key = this.final_item_id + "_" + this.final_item_model
        if (this.actions[item_key]) { return this.actions[item_key] } else { return [] }
      },
      modal_id: function() {
        return "action_history_modal_" + this.final_item_id + "_" + this.final_item_model
      }
    },
    methods: {
      ...Vuex.mapActions(['loadActions'])
    }

}

</script>
