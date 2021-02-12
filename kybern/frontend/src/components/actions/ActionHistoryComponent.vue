<template>

  <span>

    <h5>{{ title_string }}</h5>

    <b-container fluid id="action_history_table">
      <b-row>

          <b-col lg="6" class="my-4">
              <b-form-group label="Filter" label-cols-sm="3" label-align-sm="left" label-size="sm"
                                                              label-for="filterInput" class="mb-0">
                <b-input-group size="sm">
                  <b-form-input v-model="filter" type="search" id="filterInput"
                                        placeholder="Type to Search"></b-form-input>
                </b-input-group>
              </b-form-group>
          </b-col>

          <b-col lg="6" class="my-4">
              <b-form-group label="Sort" label-cols-sm="3" label-align-sm="right" label-size="sm"
                                                              label-for="sortBySelect" class="mb-0">
                <b-input-group size="sm">
                  <b-form-select v-model="sortBy" id="sortBySelect" :options="sortOptions" class="w-75">
                    <template v-slot:first><option value=""></option></template>
                  </b-form-select>
                  <b-form-select v-model="sortDesc" size="sm" :disabled="!sortBy" class="w-25">
                    <option :value="false">Asc</option>
                    <option :value="true">Desc</option>
                  </b-form-select>
                </b-input-group>
              </b-form-group>
          </b-col>
        </b-row>

          <b-table hover fixed :items="item_actions" :fields="action_fields"
              :sort-by.sync="sortBy" :sort-desc.sync="sortDesc" :filter="filter"
              :filterIncludedFields="filterOn" id="action_history_table_element">

          <!-- Custom formatting for see more column -->
          <template v-slot:cell(description)="data">

            <router-link :to="{ name: 'user-permissions', params: { user_pk: data.item.actor_pk }}" class="text-info">
                {{ data.item.actor}}
            </router-link>
            {{ data.item.description}}

            <router-link :to="{ name: 'action-detail', params: { action_id: data.item.action_pk }}">
                <b-button variant="outline-secondary" class="btn-sm action-link-button float-right">link</b-button>
            </router-link>

            <br />

            <small>
                  <b>Status: {{ data.item.status }}
                    <span v-if="data.item.status == 'implemented'">
                        (passed via {{ data.item.resolution_passed_by }} permission)</span></b>

                  {{ data.item.display_date }}
            </small>
            <b-badge v-if="data.item.has_condition.exists" variant="info">has condition</b-badge>
            <b-badge v-if="data.item.is_template" variant="warning">template action</b-badge>

          </template>

        </b-table>

    </b-container>

  </span>

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
              { key: 'description', label: "Actions", sortable: false },
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
      },
      title_string: function() {
        return "Action history for " + this.final_item_model + " " + this.final_item_name
      }
    },
    methods: {
      ...Vuex.mapActions(['loadActions'])
    }

}

</script>