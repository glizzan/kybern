<template>

    <div v-if="document" class="bg-white p-3">

        <h3 class="mt-3">{{ document.name }}</h3>
        <p>{{ document.description }}</p>

        <hr >

        <div v-html=rendered_content class="pt-4"></div>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import marked from 'marked'


export default {

    props: ['item_id'],
    store,
    created (){
        if (!this.document) { this.getDocuments() }
    },
    computed: {
        ...Vuex.mapGetters(['getDocumentData']),
        document: function() {
            return this.getDocumentData(this.item_id)
        },
        rendered_content: function() {
            if (this.document) {
                return marked(this.document.content, { sanitize: true });
            }
            return null
        }
    },
    methods: {
        ...Vuex.mapActions(['getDocuments'])
    }

}

</script>