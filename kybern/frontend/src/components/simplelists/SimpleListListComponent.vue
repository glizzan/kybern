<template>

    <span>

        <h5 class="pb-3">
            <span class="font-weight-bold">Lists</span>
                <form-button-and-modal :item_model="'list'" :button_text="'+ add new'" :supplied_variant="'light'"
                    :supplied_classes="'btn-sm ml-3'"></form-button-and-modal>
        </h5>

        <b-card-group columns>

            <b-card v-for="({ pk, name, description, rows }, index) in lists" v-bind:key=pk class="bg-white">
                <b-card-text>
                    <div class="font-weight-bold text-info">
                        <router-link :to="{ name: 'list-detail', params: { list_id: pk } }" :id="'link_to_list_' + index"
                            class="text-info">
                            {{ name }}
                            <span class="text-dark ml-2"><small>{{ rows.length }} items</small></span>
                        </router-link>
                    </div>
                    <div class="list-description mt-1">{{ description }}</div>
                </b-card-text>
            </b-card>

        </b-card-group>

        <span v-if="Object.keys(lists).length === 0">There are no lists yet.</span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: { FormButtonAndModal },
    store,
    data: function() {
        return {
        }
    },
    computed: {
        ...Vuex.mapState({
            lists: state => state.simplelists.lists,
            group_name: state => state.group_name
        }),
    },
    created () {
        this.getLists()
    },
    methods: {
        ...Vuex.mapActions(['getLists'])
    }

}

</script>