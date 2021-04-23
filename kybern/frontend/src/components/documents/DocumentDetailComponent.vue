<template>

    <b-row>
        <b-col cols=3>
            <resource-sidebar-component :highlight_model="'document'" :highlight_pk=item_id>
            </resource-sidebar-component>
        </b-col>
        <b-col cols=9>
            <document-component :item_id=item_id></document-component>
        </b-col>
    </b-row>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import DocumentComponent from '../documents/DocumentComponent'
import ResourceSidebarComponent from '../groups/ResourceSidebarComponent'


export default {

    components: { DocumentComponent, ResourceSidebarComponent },
    props: ['item_id'],

}

</script>