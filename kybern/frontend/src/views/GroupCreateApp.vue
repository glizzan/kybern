<template>

    <span>

        <navbar-component :user_name=user_name :signed_in=signed_in></navbar-component>

        <div class="container">
            <div class="mt-5">
                <div class="row">
                    <div class="col-2"></div>
                    <div class="col-8" id="createGroupApp">

                        <span v-if="!group_pk">

                            <h5>Create your group</h5>

                            <b-form-group label="Group name:" label-for="group_name">
                                <b-form-input id="group_name" name="group_name" v-model="group_name" required>
                                </b-form-input>
                                <small class="form-text text-muted">Please limit yourself to letters, numbers and spaces.
                                    200 characters or fewer.</small>
                            </b-form-group>

                            <b-form-group label="Group description:" label-for="group_description">
                                <b-form-textarea id="group_description" name="group_description" v-model="group_description"
                                    required></b-form-textarea>
                            </b-form-group>

                            <error-component :message=group_error_message></error-component>

                        </span>

                        <span v-else>
                            <h5>New Group: {{ group_name}} </h5>
                            <p>Description: {{ group_description }} </p>
                        </span>

                        <h5 class="text-info">Please select a template for your group</h5>

                        <span v-if="!start_from_scratch">

                            <div class="mb-2">

                                <small>
                                    Don't want a template?
                                    <span class="text-info" id="start_from_scratch" @click="start_from_scratch = true">
                                        Start from scratch</span>.
                                    By default, you will be the only one able to do anything in your group.
                                </small>

                            </div>

                            <template-component :scope="'community'" :create_group="true" ref="createCommunityTemplate">
                            </template-component>
                            <error-component :message=template_error_message></error-component>

                        </span>

                        <p v-else>
                            You have chosen not to use a template. <span class="text-info" @click="start_from_scratch = false">Use a template</span>.
                        </p>

                        <button display=block class="btn btn-info btn-block my-5" id="create_group_button"
                            @click="create_group()">Create Your Group</button>

                    </div>
                </div>
            </div>
        </div>

    </span>

</template>

<script>

let initialState = JSON.parse(window.__INITIAL_STATE__);

import store from '../store'
import axios from '../store/axios_instance'
import NavbarComponent from '../components/utils/NavbarComponent'
import ErrorComponent from '../components/utils/ErrorComponent'
import TemplateComponent from '../components/templates/TemplateComponent'


export default {

    components: { ErrorComponent, NavbarComponent, TemplateComponent },
    store,
    data: function() {
          return {
            user_name: initialState.user_name,
            user_pk: initialState.user_pk,
            signed_in: initialState.is_authenticated,
            group_pk: null,
            group_name: "",
            group_description: "",
            start_from_scratch: false,
            group_error_message: null,
            template_error_message: null
          }
    },
    created: function () {
        this.initialize_url_data({urls: initialState.urls})
        // in the template manager, we need to reference the current user as a group member although the group
        // has not been created yet. this requires us to set users and members with their data
        this.initialize_members_with_current_user({ user: {name: this.user_name, pk: this.user_pk}})
    },
    computed: {
        ...Vuex.mapGetters(['url_lookup'])
    },
    methods: {
        ...Vuex.mapActions(['initialize_url_data', 'initialize_members_with_current_user']),
        async create_group() {
            if (!this.group_pk) {
                // validate name & description
                if (this.group_name == "") { this.group_error_message = "Your group must have a name"; return }
                if (this.group_description == "") { this.group_error_message = "Your group must have a description"; return }

                // create group and get pk
                var url = await this.url_lookup('create_group')
                var params = { group_name: this.group_name, group_description: this.group_description }
                axios.post(url, params).then(response => {
                    this.group_pk = response.data.group_pk
                    this.create_template()
                }).catch(error => { this.group_error_message = error.message })
            } else {
                this.create_template()
            }
        },
        go_to_group() {
            var url = window.location.href.split('/').slice(0, 3).join('/') + "/groups/" + this.group_pk + "/"
            window.location.href = url
        },
        async create_template() {
            if (this.group_pk) {

                if (!this.start_from_scratch) {

                    var selected_template = this.$refs.createCommunityTemplate.selected_template
                    var supplied_fields = this.$refs.createCommunityTemplate.configuration_fields

                    if (!selected_template) {
                        this.template_error_message = "You must select a template or 'start from scratch'."
                    }

                    if (!this.$refs.createCommunityTemplate.validate_template()) {
                        return
                    }

                    // then, once group is created, apply template
                    var url = await this.url_lookup('apply_template')
                    var params = { target_model: "group", target_pk: this.group_pk, supplied_fields: supplied_fields,
                        template_model_pk: selected_template.pk }
                    axios.post(url, params).then(response => {  this.go_to_group() })
                    .catch(error => { this.template_error_message = error.message })

                } else {
                    this.go_to_group()
                }
            }
        }
    }

}

</script>
