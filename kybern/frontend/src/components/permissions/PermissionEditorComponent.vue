<template>

    <b-modal :id=modal_id :title=modal_title :body-bg-variant="'light'" size="lg" @show="refresh">

        <!-- Section 1 -->

        <span class="big-text">1. Set Permission Scope</span> <b-icon-info-circle class="ml-2"></b-icon-info-circle>
        Which action are you proposing to allow, and what does it affect?

        <b-row class="mt-2">

            <b-col>A. Permission Target

                <vue-multiselect v-model="target_selected" :options="target_options_to_use" :allow-empty="true"
                :close-on-select="true" placeholder="Choose Target" label="name" track-by="value" :max-height="200"
                group-values="items" group-label="resource_type" name="target_select">
                </vue-multiselect>

            </b-col>

            <b-col>B. Permission Action

                <vue-multiselect v-model="permission_selected" :options="permission_options_to_use" :allow-empty="true"
                :close-on-select="true" placeholder="Choose Action" label="text" track-by="value" :max-height="200"
                name="permission_select" group-values="permissions" group-label="section">
                </vue-multiselect>

            </b-col>

        </b-row>

        <hr class="my-4" />

        <!-- Section 2 -->
        <span v-if="target_selected && permission_selected">

            <span class="big-text">2. Set Permission Audience</span> <b-icon-info-circle class="ml-2"></b-icon-info-circle>
            Who gets this permission, and under what conditions (if any)?

            <audience-editor v-for="audience in audiences" v-bind:key=audience.ref :audience=audience :ref=audience.ref
                v-on:discard="discard" :target_selected=target_selected :permission_selected=permission_selected>
            </audience-editor>

            <b-button class="my-2 btn-sm" id="add_audience" variant="outline-info" @click="add_audience">
                add audience</b-button>

        </span>

        <template #modal-footer>

            <take-action-component :response=response :verb="'update'" :action_name=action_name :alt_target=alt_target
                :inline="true" class="mr-3" v-on:take-action="save_changes">
            </take-action-component>

        </template>

    </b-modal>

</template>


<script>

import Vue from 'vue'
import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import { ConfiguredFieldsMixin, PermissionGroupMixin, TargetGroupMixin } from '../utils/Mixins'
import AudienceEditor from '../permissions/AudienceEditor'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    props: ['mode', 'edit_target', 'edit_change', 'default_selection', 'role_to_edit'],
    components: { "vue-multiselect": Multiselect, AudienceEditor, TakeActionComponent },
    mixins: [ConfiguredFieldsMixin, PermissionGroupMixin, TargetGroupMixin],
    store,
    data: function() {
        return {
            target_selected: null,
            target_options_to_use: [],
            permission_selected: '',
            audiences: [],
            audience_index: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            initial_audience_pks: [],
            response: [],
            delete_response: null
        }
    },
    watch: {
        resources_loaded: function (val) {
            if (val) {
                this.target_options_to_use = this.create_target_groups()
            }
        }
    },
    computed: {
        ...Vuex.mapState({
            permission_options: state => state.permissions.permission_options,
            permissions: state => state.permissions.permissions
        }),
        modal_id() {
            if (!this.edit_target && !this.edit_change) { return "add_permission_modal" }
            if (this.mode == "add") { return "add_permission_modal_" + this.edit_target + "_" + this.edit_change }
            return "permission_modal_" + this.edit_target + "_" + this.edit_change
        },
        modal_title() {
            if (this.mode == "add") { return "Add permission" }
            return "Edit permission"
        },
        action_name() {
            if (this.mode == "add") { return 'add_permission' }
            else { return 'edit_permission' }
        },
        permission_options_to_use() {
            if (this.target_selected) {
                return this.create_permission_groups(this.permission_options[this.target_selected.model])
            }
            return []
        },
        alt_target() {
            if (this.target_selected && this.target_selected.model != "group") {
                return this.target_selected.model + "_" + this.target_selected.pk
            }
            return null
        }
    },
    methods: {
        ...Vuex.mapActions(['addPermission', 'editPermission', 'removePermission', 'addConditionToPermission',
            'editConditionOnPermission', 'removeConditionFromPermission']),
        refresh() {
            if (this.edit_target) { this.target_selected = this.find_matching_target_option() }
            if (this.edit_change) { this.permission_selected = this.find_matching_permission_option() }
            if (this.audiences.length == 0) { this.audiences = this.get_initial_audiences() }
        },
        find_matching_target_option() {
            var selection = null
            if (this.target_options_to_use && this.edit_target) {
                this.target_options_to_use.forEach(option_group => {
                    option_group.items.forEach(item => {
                        var item_name = item.model != "group" ? item.model + " '" + item.name + "'" : "community"
                        if (item_name.toLowerCase() == this.edit_target.toLowerCase()) { selection = item }
                    })
                })
            }
            return selection
        },
        find_matching_permission_option() {
            var selection = null
            if (this.permission_options_to_use && this.edit_change) {
                this.permission_options_to_use.forEach(section => {
                    section.permissions.forEach(option => {
                        if (option.text.toLowerCase() == this.edit_change.toLowerCase()) { selection = option }
                    })
                })
            }
            return selection
        },
        add_audience() {
            var next_letter = this.audience_index[this.audiences.length]
            this.audiences.push({ref: next_letter, pk: null, initial_roles: [], initial_actors: [],
                initial_anyone: false, initial_conditions:[]})
        },
        discard(data) {
            const index = this.audiences.indexOf(data.audience);
            if (index > -1) {
                this.audience_index = this.audience_index.replace(data.audience, "")
                this.audiences.splice(index, 1);
            }
        },
        reformat_permission_to_audience(permission, next_letter) {
            return { initial_roles: permission.roles, initial_actors: permission.actors,
                     initial_conditions: permission.condition, initial_anyone: permission.anyone,
                     pk: permission.pk, ref: next_letter }
        },
        get_initial_audiences() {
            var initial_audiences = []
            if (this.mode == "edit") {
                for (let pk in this.permissions) {
                    var permission = this.permissions[pk]
                    if (permission.target == this.edit_target && permission.change_name == this.edit_change) {
                        var next_letter = this.audience_index[initial_audiences.length]
                        initial_audiences.push(this.reformat_permission_to_audience(permission, next_letter))
                        this.initial_audience_pks.push(permission.pk)
                    } } }
            return initial_audiences
        },
        replace_audience_using_ref(ref, created_instance) {
            var index = this.audiences.findIndex(element => element.ref == ref)
            var reformatted = this.reformat_permission_to_audience(created_instance, ref)
            this.audiences.splice(index, 1, reformatted)
        },
        // Backend calls
        add_new_permission(audience, extra_data, ref) {
            var params = { alt_target: this.alt_target, item_id: this.target_selected.pk,
                item_model: this.target_selected.model, change_type: this.permission_selected.value,
                roles: audience.roles_selected, actors: audience.actors_selected, condition_data: audience.condition_data,
                extra_data: extra_data }
            this.addPermission(params).then(response => {
                this.response.push(response)
                if (response.data.action_status == "implemented") {
                    this.initial_audience_pks = response.data.created_instance.pk
                    this.replace_audience_using_ref(ref, response.data.created_instance)
                }
            })
        },
        edit_existing_permission(audience, extra_data) {
            var params = { alt_target: "permissionsitem_" + audience.pk, pk: audience.pk, extra_data: extra_data }
            if (audience.changed_data.includes("anyone")) { params["anyone"] = audience.anyone }
            if (audience.changed_data.includes("actors_selected")) { params["permission_actors"] = audience.actors_selected }
            if (audience.changed_data.includes("roles_selected")) { params["permission_roles"] = audience.roles_selected }
            this.editPermission(params).then(response => { this.response.push(response) })
        },
        delete_permission(pk, extra_data) {
            var params = { item_id: pk, item_model: "permissionsitem", extra_data: extra_data, item: this.alt_target }
            this.removePermission(params).then(response => { this.response.push(response) })
        },
        add_new_condition(audience, condition, extra_data, ref) {
            var params = { alt_target: "permissionsitem_" + audience.pk, permission_pk: audience.pk,
                extra_data: extra_data, condition_type: condition.condition_type,
                combined_condition_data: condition.combined_condition_data }
            this.addConditionToPermission(params).then(response => {
                this.response.push(response)
                if (response.data.action_status == "implemented") {
                    this.audiences.forEach(aud => {
                        console.log(aud)
                        if (aud.ref == ref) {
                            Vue.set(aud, "initial_conditions", response.data.condition_data)
                        }
                    })
                }
            })
        },
        edit_existing_condition(audience, condition, extra_data) {
            var params = { alt_target: "permissionsitem_" + audience.pk, permission_pk: audience.pk,
                extra_data: extra_data, condition_type: condition.condition_type,
                combined_condition_data: condition.combined_condition_data, element_id: condition.element_id }
            this.editConditionOnPermission(params).then(response => { this.response.push(response) })
        },
        remove_condition(audience, element_id, extra_data) {
            var params = { alt_target: "permissionsitem_" + audience.pk, permission_pk: audience.pk,
                extra_data: extra_data, element_id: element_id }
            this.removeConditionFromPermission(params).then(response => { this.response.push(response) })
        },
        save_changes(extra_data) {

            var final_audience_pks = []

            for (const [ref, audience] of Object.entries(this.$refs)) {  // iterate through audiences

                if (!audience[0]) { continue }

                if (!audience[0].pk) {  // if audience is new, add permission with (if existing) condition data
                    this.add_new_permission(audience[0], extra_data, ref)
                    break
                } else {
                    final_audience_pks.push(audience[0].pk)
                }

                if (audience[0].changed_data.length > 0) {     // if permission data has changed, edit it
                    this.edit_existing_permission(audience[0], extra_data)
                }

                for (let index in audience[0].condition_data) {
                    if (!audience[0].condition_data[index]["element_id"]) {     // if a new condition, add it
                        this.add_new_condition(audience[0], audience[0].condition_data[index], extra_data, ref)
                    }
                    if (audience[0].condition_data[index].changed) {        // if existing condition changed, edit
                        this.edit_existing_condition(audience[0], audience[0].condition_data[index], extra_data)
                    }
                }

                if (audience[0].removed_conditions) {
                    audience[0].removed_conditions.forEach(element_id => {
                        this.remove_condition(audience[0], element_id, extra_data)
                    })
                }
            }

            // Delete individual audiences that have been removed (but not the whole permission)
            for (let index in this.initial_audience_pks) {
                var pk = this.initial_audience_pks[index]
                if (!final_audience_pks.includes(pk)) {
                    this.delete_permission(pk, extra_data)
                }
            }

        }
    }

}

</script>

<style scoped>

    .big-text {
        font-size: 130%;
        font-weight: bold;
    }

</style>