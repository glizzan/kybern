import Vue from 'vue'
import VueRouter from 'vue-router'
// groups
import GroupConfigComponent from '../components/groups/GroupConfigComponent'
import GroupResourcesComponent from '../components/groups/GroupResourcesComponent'
// actions
import ActionHistoryComponent from '../components/actions/ActionHistoryComponent'
import ActionDetailComponent from '../components/actions/ActionDetailComponent'
// governance
import GovernanceComponent from '../components/governance/GovernanceComponent'
import ChangeLeadershipComponent from '../components/governance/ChangeLeadershipComponent'
// permissions
import GroupPermissionsComponent from '../components/permissions/GroupPermissionsComponent'
import PersonPermissionsComponent from '../components/permissions/PersonPermissionsComponent'
import ConditionManagerComponent from '../components/conditions/ConditionManagerComponent'
// forums
import ForumDetailComponent from '../components/forums/ForumDetailComponent'
import PostComponent from '../components/forums/PostComponent'
// templates
import TemplateComponent from '../components/templates/TemplateComponent'
// lists
import SimpleListDetailComponent from '../components/simplelists/SimpleListDetailComponent'
// documents
import DocumentDetailComponent from '../components/documents/DocumentDetailComponent'
import DocumentFullPageComponent from '../components/documents/DocumentFullPageComponent'


Vue.use(VueRouter)

const routes = [

    {
        name: 'home',
        path: '/',
        meta: { tab: 'resources' },
        components: {
            sidebar: GroupConfigComponent,
            main: GroupResourcesComponent
        }
    },

    // Actions
    {
        name: 'action-history',
        path: '/actions/history/:item_id/:item_model/:item_name',
        meta: { tab: 'history' },
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ActionHistoryComponent
        }
    },
    {
        name: 'action-detail',
        path: '/actions/detail/:action_id',
        meta: { tab: 'history' },
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ActionDetailComponent
        }
    },

    // Templates
    {
        name: 'templates',
        path: '/templates/:scope/',
        meta: { tab: 'governance' },
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: TemplateComponent
        }
    },
    {
        name: 'item-templates',
        path: '/templates/:scope/:target_id/:target_model',
        meta: { tab: 'governance'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: TemplateComponent
        }
    },

    // Governance
    {
        name: 'governance',
        path: '/governance',
        meta: { tab: 'governance'},
        components: {
            sidebar: GroupConfigComponent,
            main: GovernanceComponent
        }
    },
    {
        name: 'change-leadership',
        path: '/governance/change-leadership',
        meta: { tab: 'governance'},
        components: {
            sidebar: GroupConfigComponent,
            main: ChangeLeadershipComponent
        }
    },

    // Permissions
    {
        name: 'group-permissions',
        path: '/permissions/:group_pk',
        meta: { tab: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: GroupPermissionsComponent
        }
    },
    {
        name: 'user-permissions',
        path: '/permissions/user/:user_pk',
        meta: { tab: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: PersonPermissionsComponent
        }
    },
    {
        name: 'conditions',
        path: '/conditions/:conditioned_on/:dependency_scope',
        meta: { tab: 'permissions'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ConditionManagerComponent
        }
    },

    //Forums
    {
        name: 'forum-detail',
        path: '/forums/:item_id',
        meta: { tab: 'resources'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: ForumDetailComponent
        }
    },
    {
        name: 'post-detail',
        path: '/forums/:forum_id/posts/:item_id',
        meta: { tab: 'resources'},
        props: { sidebar: false, main: true },
        components: {
            sidebar: GroupConfigComponent,
            main: PostComponent
        }
    },

    // Lists
    {
        name: 'list-detail',
        path: '/lists/detail/:list_id',
        meta: { tab: 'resources'},
        props: { sidebar: false, main: true},
        components: {
            sidebar: GroupConfigComponent,
            main: SimpleListDetailComponent
        }
    },

    // Documents
    {
        name: 'document-detail',
        path: '/documents/detail/:item_id',
        meta: { tab: 'resources'},
        props: { sidebar: false, main: true},
        components: {
            sidebar: GroupConfigComponent,
            main: DocumentDetailComponent
        }
    },
    {
        name: 'document-full-page',
        path: '/documents/detail/full/:item_id/',
        meta: { tab: 'resources'},
        props: { sidebar: false, main: true},
        components: {
            sidebar: GroupConfigComponent,
            main: DocumentFullPageComponent
        }
    }

]

const router = new VueRouter({
  routes
})

export default router
