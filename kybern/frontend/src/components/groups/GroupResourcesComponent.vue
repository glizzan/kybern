<template>

    <span>

        <ForumListComponent></ForumListComponent>

        <hr />

        <SimpleListListComponent></SimpleListListComponent>

        <hr />

        <DocumentListComponent></DocumentListComponent>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ForumListComponent from '../forums/ForumListComponent'
import SimpleListListComponent from '../simplelists/SimpleListListComponent'
import DocumentListComponent from '../documents/DocumentListComponent'


export default {

    store,
    mixins: [UtilityMixin],
    components: { ForumListComponent, SimpleListListComponent, DocumentListComponent },
    data: function() {
        return {}
    }

}

</script>