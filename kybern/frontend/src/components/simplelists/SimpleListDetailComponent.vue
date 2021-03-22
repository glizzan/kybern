<template>

    <b-row>
        <b-col cols=3>
            <resource-sidebar-component :highlight_model="'simplelist'" :highlight_pk=list_id>
            </resource-sidebar-component>
        </b-col>
        <b-col cols=9>
            <simple-list-component :list_id=list_id></simple-list-component>
        </b-col>
    </b-row>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import SimpleListComponent from '../simplelists/SimpleListComponent'
import ResourceSidebarComponent from '../groups/ResourceSidebarComponent'


export default {

    components: { SimpleListComponent, ResourceSidebarComponent },
    props: ['list_id'],

}

</script>