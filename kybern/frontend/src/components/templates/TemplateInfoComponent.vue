<template>

    <b-card :title=template.name v-bind:key=template.pk  class="w-50" style="display:inline-block"
        :id="slugify_name(template.name)">
        <b-card-text>{{ template.description }}
            <div>
                <b-button v-b-toggle="'template_actions_' + slugify_name(template.name)" class="btn-sm mt-3">
                    Template Details</b-button>
                <b-collapse :id="'template_actions_' + slugify_name(template.name)" class="mt-3">
                    <b-card><small>
                        <span v-if="!create_group">{{template.action_breakdown.foundational}}</span>
                        <ol class="mt-3">
                            <li v-for="action in template.action_breakdown.actions" v-bind:key=action.pk>{{action}}</li>
                        </ol>
                    </small></b-card>
                </b-collapse>
            </div>
        </b-card-text>
        <b-button v-if="display_select" :id="'select_template_' + slugify_name(template.name)" variant="outline-dark"
            class="my-2" v-on:click="$emit('template-selected', template)">select template</b-button>
    </b-card>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    store,
    props: ['create_group', 'template', 'display_select'],
    data: function() {
        return {
        }
    },
    methods: {
        slugify_name(name) {
            return name.toLowerCase().replace(/ /g, "_")
        }
    }

}

</script>