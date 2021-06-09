<template>

    <span>

        <h5 class="pb-3">
            <span class="font-weight-bold">Forums</span>
            <form-button-and-modal :item_model="'forum'" :button_text="'+ add new'" :supplied_variant="'light'"
                :supplied_classes="'btn-sm ml-3'"></form-button-and-modal>
        </h5>

        <b-card-group columns>

            <b-card v-for="{ pk, name, description } in processed_forums" v-bind:key=pk class="bg-white">
                <b-card-text>
                    <div class="font-weight-bold text-info">
                        <router-link :to="{ name: 'forum-detail', params: {item_id: pk}}" class="forum-link text-info">
                            {{ name }}</router-link>
                    </div>
                    <div class="forum-description mt-1">{{ description }}</div>
                </b-card-text>
            </b-card>

        </b-card-group>

    </span>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: { FormButtonAndModal },
    store,
    computed: {
        ...Vuex.mapState({
            forums: state => state.forums.forums,
            group_name: state => state.group_name
        }),
        processed_forums: function() {
            var processed_forums = []
            for (let index in this.forums) {
                if (this.forums[index].special == "Gov") {
                    processed_forums.unshift(this.forums[index])
                }
                else { processed_forums.push(this.forums[index]) }
            }
            return processed_forums
        }
    }

}

</script>

<style scoped>

    .card-deck .card {
        max-width: 5px;
    }

</style>


