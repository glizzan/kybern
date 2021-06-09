<template>

<b-container>

    <b-row>

        <b-col cols=6 class="pl-0">
            <div class="bg-white p-3">
                <p class="font-weight-bold">Owners</p>
                <edit-leadership-component leadership_type="owner"></edit-leadership-component>
            </div>
            <div class="bg-white p-3 mt-4">
                <p class="font-weight-bold">Owner Conditions</p>
                <condition-editor class="my-2" ref="owner_conditions" :initial_conditions="owner_condition">
                </condition-editor>
                <take-action-component :response=owner_condition_response :verb="'update conditions'"
                    :action_name="'add_condition'" :inline="true" class="mr-3"
                    v-on:take-action="update_condition('owner', $event)">
                </take-action-component>
            </div>
        </b-col>

        <b-col cols=6 class="pr-0">
            <div class="bg-white p-3">
                <p class="font-weight-bold">Governors</p>
                <edit-leadership-component leadership_type="governor"></edit-leadership-component>
            </div>
            <div class="bg-white p-3 mt-4">
                <p class="font-weight-bold">Governor Conditions</p>
                <condition-editor class="my-2" ref="governor_conditions" :initial_conditions="governor_condition">
                </condition-editor>
                <take-action-component :response=governor_condition_response :verb="'update conditions'"
                    :action_name="'add_condition'" :inline="true" class="mr-3"
                    v-on:take-action="update_condition('governor', $event)">
                </take-action-component>
            </div>
        </b-col>

    </b-row>
</b-container>
</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import EditLeadershipComponent from '../governance/EditLeadershipComponent'
import ConditionEditor from '../permissions/ConditionEditor'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    components: { EditLeadershipComponent, ConditionEditor, TakeActionComponent },
    store,
    data: function() {
        return {
            owner_condition_response: [],
            governor_condition_response: []
        }
    },
    computed: {
        ...Vuex.mapState({
            owner_condition: state => state.permissions.owner_condition,
            governor_condition: state => state.permissions.governor_condition,
            group_name: state => state.group_name
        }),
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions', 'leadershipAsOptions']),
        owner_condition_display: function() {
            if (this.owner_condition) { return this.owner_condition.how_to_pass_overall }
            else { return "No condition has been set on owners." }
        },
        governor_condition_display: function() {
            if (this.governor_condition) { return this.governor_condition.how_to_pass_overall }
            else { return "No condition has been set on governors." }
        }
    },
    methods: {
        ...Vuex.mapActions(['addLeadershipCondition', 'editLeadershipCondition', 'removeLeadershipCondition']),
        update_response(leadership_type, response ) {
            if (leadership_type == "owner") { this.owner_condition_response.push(response) }
            if (leadership_type == "governor") { this.governor_condition_response.push(response) }
        },
        add_new_condition(leadership_type, condition, extra_data) {
            var params = { leadership_type: leadership_type, extra_data: extra_data,
                condition_type: condition.condition_type, combined_condition_data: condition.combined_condition_data }
            console.log("Adding new condition with params: ", params)
            this.addLeadershipCondition(params).then(response => { this.update_response(leadership_type, response ) })
        },
        edit_existing_condition(leadership_type, condition, extra_data) {
            var params = { leadership_type: leadership_type, extra_data: extra_data,
                element_id: condition.element_id , condition_type: condition.condition_type,
                combined_condition_data: condition.combined_condition_data }
            console.log("editing condition with params: ", params)
            this.editLeadershipCondition(params).then(response => { this.update_response(leadership_type, response ) })
        },
        remove_condition(leadership_type, element_id, extra_data) {
            var params = { leadership_type: leadership_type, extra_data: extra_data, element_id: element_id }
            console.log("Deleteing conditions with params: ", params)
            this.removeLeadershipCondition(params).then(response => { this.update_response(leadership_type, response ) })
        },
        update_condition(leadership_type, extra_data) {

            var reference = null
            if (leadership_type == "owner") { reference = this.$refs.owner_conditions }
            if (leadership_type == "governor") { reference = this.$refs.governor_conditions }

            var condition_data = Object.values(reference.conditions_set).map(condition => {
                return {"condition_type": condition.name, "combined_condition_data": condition.fields,
                    "element_id": condition.element_id, "changed": condition.changed }
            })

            for (let index in condition_data) {
                var condition = condition_data[index]
                if (!condition["element_id"]) {
                    this.add_new_condition(leadership_type, condition, extra_data)
                }
                if (condition.changed) {
                    this.edit_existing_condition(leadership_type, condition, extra_data)
                }
            }

            if (reference.removed_condition_element_ids) {
                reference.removed_condition_element_ids.forEach(element_id => {
                    this.remove_condition(leadership_type, element_id, extra_data)
                })
            }
        }
    }

}

</script>