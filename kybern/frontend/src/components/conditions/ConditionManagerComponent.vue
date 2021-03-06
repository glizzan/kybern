<template>

    <span>

        <h5>Conditions for
            <span v-if="leadership_type" class="text-info">{{ group_name }}'s {{ leadership_type }}s</span>
            <span v-if="permission">permission <span class="text-info">'{{ permission.display}}'</span></span>
        </h5>

        <span id="existing_condition">
            <div v-for="(condition, index) in conditions" v-bind:key=condition.element_id class="mx-auto">
                <div class="rounded bg-light border p-3 mt-3 text-center edit-condition-text">
                <p>{{condition.how_to_pass}} <b-button class="btn-sm btn-light border edit-condition-button"
                    v-b-modal="'edit_condition_modal_'+condition.element_id">edit</b-button></p>
                <edit-condition-component :element_id=condition.element_id v-on:finished="clear_state">
                </edit-condition-component>
                </div>
                <p v-if="index < conditions.length - 1" class="text-center p-1">AND</p>
            </div>
            <span v-if="!conditions || conditions.length == 0">There are no conditions set.</span>
        </span>

        <hr />

        <span v-if="!condition_selected">
            <b-button v-if="!show_select" @click="show_select=true" class="btm-sm mt-3" id="new_condition">
                Add new condition</b-button>

            <span v-if="show_select && !condition_selected">
                <b>Select condition to add</b>
                <template><div>
                    <b-form-select v-model="condition_selected" :options="processed_condition_options" :select-size="4"
                        name="condition_select">
                    </b-form-select>
                </div></template>
            </span>

            <error-component :message=error_message></error-component>
        </span>

        <edit-condition-component v-if="condition_selected" :condition_selected=condition_selected v-on:finished="clear_state">
        </edit-condition-component>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import EditConditionComponent from '../conditions/EditConditionComponent'


export default {

    store,
    props: ['conditioned_on', 'dependency_scope'],
    components: { ErrorComponent, EditConditionComponent },
    data: function() {
        return {
            show_select: false,
            leadership_type: null,
            condition_selected: '',
            error_message : ''
        }
    },
    provide() {
        var dependency_scope = this.dependency_scope ? this.dependency_scope : "group"
        return {dependency_scope: dependency_scope}
    },
    created () {
        if (["owner", "governor"].indexOf(this.conditioned_on) > -1) {
            this.leadership_type = this.conditioned_on
        } else {
            this.fetchMissingPermission({pk: this.conditioned_on}).catch(error => console.log(error))
        }
    },
    computed: {
        ...Vuex.mapState({
            owner_condition: state => state.permissions.owner_condition,
            governor_condition: state => state.permissions.governor_condition,
            condition_options: state => state.permissions.condition_options,
            permissions: state => state.permissions.permissions,
            group_name: state => state.group_name
        }),
        processed_condition_options: function() {
            var options = []
            options.push({
                label: "Decision Conditions",
                options: this.condition_options.filter(option => !option.value.includes("Filter"))
            })
            if (!this.leadership_type) {
                options.push({
                    label: "Filter Conditions",
                    options: this.condition_options.filter(option => {
                        if (option.value.includes("Filter")) {
                            if (!option.linked) { return true }
                            if (this.permission.linked && this.permission.linked.includes(option.value)) {
                                return true
                            }
                        }
                        return false
                    })
                })
            }
            return options
        },
        permission: function() {
            if (!this.leadership_type) {
                return this.permissions[this.conditioned_on]
            } return undefined
        },
        conditions_with_keys: function() {
            if (this.permission && this.permission.condition) { return this.permission.condition }
            if (this.leadership_type == "owner" && this.owner_condition) { return this.owner_condition }
            if (this.leadership_type == "governor" && this.governor_condition) { return this.governor_condition }
            return undefined
        },
        conditions: function() {
            if (this.conditions_with_keys) {
                var conditions = this.conditions_with_keys
                delete conditions.how_to_pass_overall
                return Object.values(conditions).sort(function(a, b) {
                    if (a.how_to_pass < b.how_to_pass) { return -1 }
                    if (a.how_to_pass > b.how_to_pass) { return 1 }
                    return 0
                })
            } else { return [] }
        }
    },
    methods: {
        ...Vuex.mapActions(['fetchMissingPermission']),
        clear_state() {
            this.condition_selected = null
            this.show_select = false
        }
    }

}

</script>