<template>

    <b-row>
        <b-col cols=3>
            <resource-sidebar-component :highlight_model="'forum'" :highlight_pk=forum_id>
            </resource-sidebar-component>
        </b-col>
        <b-col cols=9>
            <forum-component :forum_id=forum_id></forum-component>
        </b-col>
    </b-row>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
import ForumComponent from '../forums/ForumComponent'
import ResourceSidebarComponent from '../groups/ResourceSidebarComponent'


export default {

    components: { ForumComponent, ResourceSidebarComponent },
    props: ['forum_id'],

}

</script>