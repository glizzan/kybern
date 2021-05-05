<template>

    <span>

        <navbar-component :user_name=user_name :signed_in=signed_in></navbar-component>

        <div class="container">
        <div class="row mt-5">
        <div class="col-12">

            <h3>Templates Library</h3>
            <p>Templates are sets of actions you can apply to your communities with one click. They largely
                set permissions and conditions, but they may also create roles or resources. You can explore
                the existing templates here. To apply them, go to one of the "apply templates" interfaces
                within your group.</p>

            <b-button-group class="mb-4">
                <b-button variant="outline-info" v-for="scope in scopes" v-bind:key="scope"
                    @click="selected_scope=scope">{{scope}}</b-button>
            </b-button-group>

            <b-card-group columns>
                <b-card v-for="template in filtered_templates" v-bind:key="template.pk" :title="template.name">
                <b-card-text>
                    <b-badge v-for="scope in template.scopes" v-bind:key="scope" class="mb-3"
                        variant="secondary">{{scope}}</b-badge>
                    <br />
                    {{template.description}}
                    <br />
                    <b-button variant="outline-info" class="mt-3" @click="show_modal(template)">
                        view details</b-button>
                </b-card-text>
                </b-card>
            </b-card-group>

            <b-modal :title=modal_title @hide="close_modal()" hide-footer :visible=modalIsVisible size="lg">

                <span v-if=selected_template>

                    <p>{{ selected_template.action_breakdown.foundational }}</p>

                    <ol class="mt-3">
                        <li v-for="action in selected_template.action_breakdown.actions"
                            v-bind:key=action.pk>{{action}}</li>
                    </ol>

                </span>

            </b-modal>

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

export default {

    components: { NavbarComponent },
    store,
    data: function() {
        return {
            user_name: initialState.user_name,
            user_pk: initialState.user_pk,
            signed_in: initialState.is_authenticated,
            templates: initialState.templates,
            selected_template: null,
            selected_scope: "all templates"
        }
    },
    created () {
    },
    computed: {
        scopes: function() {
            var scopes = ["all templates"]
            this.templates.forEach(template => {
                template.scopes.forEach(scope => {
                    if (!scopes.includes(scope)) { scopes.push(scope) }
                }) })
            return scopes
        },
        modal_title: function() {
            if (this.selected_template) { return this.selected_template.name } else { return "" }
        },
        modalIsVisible: function() { return this.selected_template ? true : false },
        filtered_templates: function() {
            if (this.selected_scope != "all templates") {
                var templates = []
                this.templates.forEach(template => {
                    if (template.scopes.includes(this.selected_scope)) {
                        templates.push(template)
                    }
                })
                return templates
            } else {
                return this.templates
            }
        }
    },
    methods: {
        show_modal(template) { this.selected_template = template },
        close_modal() { this.selected_template = null }
    }

}

</script>

