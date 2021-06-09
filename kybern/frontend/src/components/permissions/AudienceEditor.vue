<template>

        <b-row class="mt-2 bg-white m-2 p-2">

            <b-col>Audience {{ audience.ref }}

                <!-- Roles -->

                <vue-multiselect v-model=roles_selected :multiple=true :options=rolesAsOptions :allow-empty="true"
                    :close-on-select="true" placeholder="Select roles" label="name" track-by="name"
                    name="permission_role_select" class="mt-2">
                </vue-multiselect>

                <!-- Actors -->

                <vue-multiselect v-model=actors_selected :multiple=true :options=groupMembersAsOptions :allow-empty="true"
                    :close-on-select="true" placeholder="Select actors" label="name" track-by="pk"
                    name="permission_actor_select" class="my-2">
                </vue-multiselect>

                <!-- Anyone: warning, will override roles and actors -->
                <b-form-checkbox v-model="anyone" name="anyone-button" switch>
                    Anyone can take this action
                    <b-icon-info-circle-fill class="ml-1" v-b-tooltip.hover
                        title="All Kybern users will be able to take the action. This overrides actors and roles selected above.">
                        </b-icon-info-circle-fill>
                </b-form-checkbox>

            </b-col>

            <b-col>Condition(s) (Optional)
                                        <b-icon-x class="float-right" @click="discard_audience"></b-icon-x>

                <condition-editor class="my-2" ref="audience_conditions" :conditioned_on="'permission'"
                    :initial_conditions="initial_conditions"></condition-editor>

            </b-col>

        </b-row>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import ConditionEditor from '../permissions/ConditionEditor'


export default {

    props: ['audience', 'target_selected', 'permission_selected'],
    components: { "vue-multiselect": Multiselect, ConditionEditor },
    mixins: [],
    store,
    data: function() {
        return {
            anyone: false,
            roles_selected: [],
            actors_selected: [],
            // dependent_field_info: null  // initialize here
        }
    },
    created() {
        if (this.audience) {
            this.anyone = this.audience.initial_anyone
            this.roles_selected = this.initial_roles
            this.actors_selected = this.initial_actors
        }
    },
    provide() {
        const dependent_field_info = {}
        // need to do this elaborate setup so it's reactive
        // see: https://stackoverflow.com/questions/61518656/vue-state-not-updated-with-default-injected-value
        Object.defineProperty(dependent_field_info, 'dependency_scope', {
            enumerable: false,
            get: () => this.target_selected.model,
        })
        Object.defineProperty(dependent_field_info, 'permission_option', {
            enumerable: false,
            get: () => this.permission_selected,
        })
        return { dependent_field_info }
    },
    computed: {
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions','role_to_options', 'user_pk_to_options']),
        initial_roles: function() {
            if (this.audience) { return this.role_to_options(this.audience.initial_roles) } else { return [] }
        },
        initial_actors: function() {
            if (this.audience) { return this.user_pk_to_options(this.audience.initial_actors) } else { return [] }
        },
        pk: function() {
            if (this.audience) { return this.audience.pk } else { return null }
        },
        initial_conditions: function() {
            if (this.audience) { return this.audience.initial_conditions } else { return null }
        },
        removed_conditions: function() {
            return this.$refs.audience_conditions.removed_condition_element_ids
        },
        condition_data: function() {
            return Object.values(this.$refs.audience_conditions.conditions_set).map(condition => {
                return {"condition_type": condition.name, "combined_condition_data": condition.fields,
                    "element_id": condition.element_id, "changed": condition.changed }
            })
        },
        changed_data: function() {
            var changes = []

            if (this.anyone != this.audience.initial_anyone) {
                changes.push("anyone")
            }

            var selected_roles = this.roles_selected
            selected_roles.sort()
            var initial_roles = this.initial_roles
            initial_roles.sort()
            if (JSON.stringify(selected_roles) != JSON.stringify(initial_roles)) {
                changes.push("roles_selected")
            }

            var selected_actors = this.actors_selected
            selected_actors.sort()
            var initial_actors = this.initial_actors
            initial_actors.sort()
            if (JSON.stringify(selected_actors) != JSON.stringify(initial_actors)) {
                changes.push("actors_selected")
            }

            return changes
        }
    },
    methods: {
        discard_audience() {
            this.$emit('discard', {audience: this. audience})
        }
    }

}

</script>
