<template>

    <span>

        <ForumListComponent></ForumListComponent>

        <hr />

        <SimpleListListComponent></SimpleListListComponent>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ForumListComponent from '../forums/ForumListComponent'
import SimpleListListComponent from '../simplelists/SimpleListListComponent'


export default {

    store,
    mixins: [UtilityMixin],
    components: { ForumListComponent, SimpleListListComponent },
    data: function() {
        return {}
    }

}

</script>